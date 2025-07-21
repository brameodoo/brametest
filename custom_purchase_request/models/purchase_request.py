# models/purchase_request.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.account.models.account_tax import AccountTax 

class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Purchase Request'

    name = fields.Char(string='Referencia', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    requester_id = fields.Many2one('res.users', string='Solicitante', default=lambda self: self.env.user, readonly=True)
    request_date = fields.Date(string='Fecha de Solicitud', required=True, default=fields.Date.context_today)
    department_id = fields.Many2one('hr.department', string='Departamento', compute='_compute_department_id', store=True, readonly=False)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('to_approve', 'Para Aprobar'),
        ('approved', 'Aprobado'),
        ('done', 'Realizado'),
        ('cancel', 'Cancelado')
    ], string='Estado', default='draft', tracking=True)
    line_ids = fields.One2many('purchase.request.line', 'request_id', string='Líneas de Solicitud', copy=True)
    purchase_order_id = fields.Many2one('purchase.order', string='Orden de Compra Generada', readonly=True, copy=False)
    project_id = fields.Many2one('project.project', string='Proyecto Relacionado', tracking=True)
    company_id = fields.Many2one('res.company', 'Compañía', required=True, index=True,
                                  default=lambda self: self.env.company)
    approver_id = fields.Many2one('res.users', string='Aprobador')
    approval_date = fields.Datetime(string='Fecha de Aprobación')

    amount_untaxed = fields.Monetary(string='Subtotal', store=True, compute='_amount_all', tracking=True)
    amount_tax = fields.Monetary(string='Impuestos', store=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, compute='_amount_all')
    currency_id = fields.Many2one(related='company_id.currency_id', depends=['company_id'], store=True, string='Moneda')

    vendor_id = fields.Many2one('res.partner', string='Proveedor Sugerido', domain="[('is_company', '=', True), ('supplier_rank', '>', 0)]")

    @api.depends('line_ids.price_total')
    def _amount_all(self):
        """
        Calcula el subtotal, impuestos y total de la solicitud de compra.
        """
        for request in self:
            amount_untaxed = 0.0
            amount_tax = 0.0
            
            # --- NUEVA COMPROBACIÓN: Asegurarse de que la moneda exista ---
            # Si no hay moneda en la solicitud (ej. al crear un registro nuevo antes de asignar compañía),
            # usamos la moneda de la compañía por defecto del entorno, o una por defecto global si es necesario.
            currency = request.currency_id # Intentar usar la moneda de la solicitud
            if not currency: # Si la moneda de la solicitud no está establecida (por company_id)
                # Intentar usar la moneda de la compañía del usuario o la compañía por defecto
                currency = self.env.company.currency_id 
            
            # Si aún así no tenemos una moneda válida, esto es un problema de configuración grave.
            # En un caso extremo, podríamos buscar la primera moneda activa, pero es mejor que falle
            # si la configuración básica no es correcta.
            if not currency:
                _logger.warning("No se encontró una moneda válida para la solicitud de compra %s. Los totales pueden ser incorrectos.", request.name)
                # Establecer totales a cero si no hay moneda para evitar el error de singleton
                request.update({
                    'amount_untaxed': 0.0,
                    'amount_tax': 0.0,
                    'amount_total': 0.0,
                })
                continue # Saltar al siguiente registro si estamos en un recordset

            for line in request.line_ids:
                amount_untaxed += line.price_subtotal
                # Asegurarse de que el cálculo de impuestos sume la diferencia correctamente.
                # 'taxes.get('total_included', 0.0) - taxes.get('total_excluded', 0.0)' es más robusto
                # porque se basa en los resultados de compute_all directamente.
                amount_tax += (line.price_total - line.price_subtotal) # Suma la parte de impuestos de cada línea
            
            request.update({
                'amount_untaxed': currency.round(amount_untaxed),
                'amount_tax': currency.round(amount_tax),
                'amount_total': currency.round(amount_untaxed + amount_tax), # Redondear el total final también
            })

    @api.depends('requester_id')
    def _compute_department_id(self):
        for rec in self:
            if rec.requester_id and rec.requester_id.employee_id and rec.requester_id.employee_id.department_id != rec.department_id:
                rec.department_id = rec.requester_id.employee_id.department_id
            elif not rec.requester_id or not rec.requester_id.employee_id or not rec.requester_id.employee_id.department_id:
                if not rec.department_id:
                    rec.department_id = False
            
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.request.sequence') or _('New')
            
        if not vals.get('vendor_id'):
            generic_vendor = self.env['res.partner'].search([
                ('name', '=', 'Proveedor Genérico (Solicitudes)'),
                ('is_company', '=', True),
                ('supplier_rank', '>', 0)
            ], limit=1)
            if generic_vendor:
                vals['vendor_id'] = generic_vendor.id
            else:
                pass 
            
        return super(PurchaseRequest, self).create(vals)

    @api.constrains('line_ids')
    def _check_lines(self):
        if not self.line_ids:
            raise ValidationError(_('Debes agregar al menos una línea a la solicitud de compra.'))

    def action_submit_for_approval(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("No puedes enviar una solicitud sin líneas de solicitud."))
            if any(line.price_unit == 0 for line in rec.line_ids):
                raise UserError(_("Todas las líneas de solicitud deben tener un precio unitario mayor a cero para ser enviadas a aprobación."))
            rec.state = 'to_approve'
            rec.message_post(body=_("Solicitud enviada para aprobación."))

    def action_approve(self):
        for rec in self:
            if rec.state != 'to_approve':
                raise UserError(_("La solicitud debe estar en estado 'Para Aprobar' para ser aprobada."))
            rec.state = 'approved'
            rec.approver_id = self.env.user.id
            rec.approval_date = fields.Datetime.now()
            rec.message_post(body=_("Solicitud Aprobada por %s.") % self.env.user.name)

    def action_set_to_done(self):
        for rec in self:
            if rec.state != 'approved':
                raise UserError(_("La solicitud debe estar en estado 'Aprobado' para ser marcada como Realizada."))
            rec.state = 'done'
            rec.message_post(body=_("Solicitud marcada como Realizada."))

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
            rec.message_post(body=_("Solicitud Cancelada."))

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'
            rec.message_post(body=_("Solicitud regresada a Borrador."))

    def action_generate_purchase_order(self):
        self.ensure_one()
        if self.state != 'approved':
            raise UserError(_("Solo puedes generar una Orden de Compra desde una Solicitud de Compra Aprobada."))
        if self.purchase_order_id:
            raise UserError(_("Ya se ha generado una Orden de Compra para esta Solicitud."))

        if not self.vendor_id:
            raise UserError(_("El proveedor no está asignado en la Solicitud de Compra. Por favor, selecciona un proveedor o asegúrate de que el 'Proveedor Genérico (Solicitudes)' existe."))

        purchase_order = self.env['purchase.order'].create({
            'partner_id': self.vendor_id.id, 
            'date_order': fields.Datetime.now(),
            'company_id': self.company_id.id,
            'user_id': self.requester_id.id, 
            'origin': self.name,
            'state': 'draft', 
        })

        for line in self.line_ids:
            self.env['purchase.order.line'].create({
                'order_id': purchase_order.id,
                'product_id': line.product_id.id,
                'product_qty': line.quantity,
                'product_uom': line.uom_id.id,
                'price_unit': line.price_unit, 
                'name': line.description, 
                'taxes_id': [(6, 0, line.taxes_id.ids)], 
            })

        self.purchase_order_id = purchase_order.id
        self.state = 'done'
        purchase_order.message_post(body=_("Orden de Compra generada desde Solicitud de Compra <a href='/web#id=%s&model=purchase.request'>%s</a>.") % (self.id, self.name))
        self.message_post(body=_("Orden de Compra <a href='/web#id=%s&model=purchase.order'>%s</a> generada.") % (purchase_order.id, purchase_order.name))
        return {
            'name': _('Orden de Compra'),
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'res_id': purchase_order.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

class PurchaseRequestLine(models.Model):
    _name = 'purchase.request.line'
    _description = 'Purchase Request Line'

    request_id = fields.Many2one('purchase.request', string='Solicitud de Compra', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Producto', required=True)
    description = fields.Char(string='Descripción', default=lambda self: self.product_id.name if self.product_id else False)
    quantity = fields.Float(string='Cantidad', required=True, default=1.0)
    uom_id = fields.Many2one('uom.uom', string='Unidad de Medida', required=True)
    note = fields.Text(string='Nota de Línea')

    taxes_id = fields.Many2many('account.tax', string='Impuestos', domain=['|', ('active', '=', False), ('active', '=', True)])
    price_unit = fields.Float(string='Precio unitario', required=True, digits='Product Price', default=0.0)
    
    price_subtotal = fields.Monetary(string='Sin Impuestos', store=True, compute='_compute_amount', digits='Account')
    price_total = fields.Monetary(string='Total', store=True, compute='_compute_amount', digits='Account')
    
    currency_id = fields.Many2one(related='request_id.currency_id', store=True, string='Moneda')


    @api.depends('quantity', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        """
        Calcula el precio_subtotal y precio_total de la línea de solicitud.
        """
        for line in self:
            currency = line.currency_id or line.request_id.company_id.currency_id
            if not currency:
                line.update({
                    'price_subtotal': 0.0, # Inicializar a 0 si no hay moneda
                    'price_total': 0.0,    # Inicializar a 0 si no hay moneda
                })
                continue
            
            # --- CAMBIO CRÍTICO AQUÍ ---
            # compute_all espera el precio unitario del producto y la cantidad por separado,
            # no el precio total de la línea (price_unit * quantity).
            # La base para el cálculo de impuestos es solo 'price_unit',
            # y 'quantity' se pasa como argumento 'quantity'.
            taxes = line.taxes_id.compute_all(line.price_unit, currency, line.quantity, product=line.product_id, partner=line.request_id.vendor_id)
            
            line.update({
                'price_subtotal': taxes['total_excluded'], # total_excluded es el subtotal sin impuestos
                'price_total': taxes['total_included'],   # total_included es el total con impuestos
            })

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_po_id or self.product_id.uom_id
            self.description = self.product_id.name
            self.price_unit = self.product_id.standard_price if self.product_id.standard_price else self.product_id.list_price
            self.taxes_id = self.product_id.supplier_taxes_id

