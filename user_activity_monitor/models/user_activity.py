# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)

class UserActivity(models.Model):
    _name = 'user.activity'
    _description = 'Registro de Actividad de Usuario'
    _order = 'timestamp desc' # Ordenar por fecha y hora descendente por defecto

    user_id = fields.Many2one('res.users', string='Usuario', required=True, ondelete='cascade')
    department_id = fields.Many2one('hr.department', string='Departamento', compute='_compute_department_id', store=True)
    module_name = fields.Char(string='Módulo Odoo', help='Nombre técnico del módulo (ej. sale, purchase, crm)')
    model_name = fields.Char(string='Modelo Afectado', help='Nombre técnico del modelo (ej. res.partner, sale.order)')
    action_type = fields.Selection([
        ('create', 'Crear'),
        ('write', 'Modificar'),
        ('unlink', 'Eliminar'),
        ('view', 'Ver'),
        ('login', 'Iniciar Sesión'),
        ('logout', 'Cerrar Sesión'),
        ('report_print', 'Imprimir Informe'),
        ('other', 'Otro')
    ], string='Tipo de Acción', required=True)
    record_id = fields.Integer(string='ID del Registro', help='ID del registro afectado (si aplica)')
    record_name = fields.Char(string='Nombre del Registro', help='Nombre visible del registro (si aplica)')
    timestamp = fields.Datetime(string='Fecha y Hora', default=fields.Datetime.now, required=True)
    # Puedes añadir más campos si necesitas más detalle, como 'ip_address', 'user_agent', etc.

    @api.depends('user_id')
    def _compute_department_id(self):
        for rec in self:
            rec.department_id = False # Inicializar para evitar problemas
            if rec.user_id and rec.user_id.employee_id:
                rec.department_id = rec.user_id.employee_id.department_id

    @api.model
    def create_activity_record(self, user, action_type, model_name=False, record_id=False, record_name=False, module_name=False):
        """
        Método auxiliar para crear un registro de actividad.
        Esto centraliza la lógica y puede ser llamado desde cualquier lugar.
        """
        # Evitar registrar actividades de sistema (como el usuario 'OdooBot' o el usuario root)
        # o bucles infinitos (al crear el propio registro de user.activity).
        # También se puede usar el contexto 'skip_activity_logging' para evitar el log.
        if not user or user._uid == self.env.ref('base.user_root').id or self.env.context.get('skip_activity_logging') or model_name == 'user.activity':
            return

        # Inferir el nombre del módulo si no se proporciona
        if not module_name and model_name:
            try:
                # Intentar inferir el módulo usando ir.model.data
                # Buscar un registro ir.model.data que contenga este modelo
                # ir.model.data almacena las referencias de modelos como 'model_sale_order',
                # así que reemplazamos los puntos del model_name con guiones bajos.
                model_ref_name = 'model_' + model_name.replace('.', '_')
                model_data = self.env['ir.model.data'].sudo().search([
                    ('model', '=', 'ir.model'),
                    ('name', '=', model_ref_name)
                ], limit=1)

                if model_data and model_data.module:
                    module_name = model_data.module
                else:
                    # Si no se encuentra por ir.model.data, intentar el atributo _module directo
                    model_obj = self.env[model_name]
                    if model_obj and hasattr(model_obj, '_module') and model_obj._module:
                        module_name = model_obj._module
                    else:
                        _logger.info(f"No se pudo inferir el módulo para el modelo: {model_name}. _module o ir.model.data no proporcionaron información.")
            except KeyError:
                _logger.warning(f"Modelo '{model_name}' no encontrado en el entorno para inferir el módulo.")
            except Exception as e:
                _logger.error(f"Error general al inferir el módulo para '{model_name}': {e}")
        
        try:
            # Usar .sudo() para asegurar que la creación del registro de actividad
            # no falle por permisos, incluso si el usuario original no tiene permisos sobre user.activity
            self.sudo().create({
                'user_id': user.id,
                'action_type': action_type,
                'model_name': model_name,
                'record_id': record_id,
                'record_name': record_name,
                'module_name': module_name, # Este campo ahora debería estar mejor poblado
            })
        except AccessError:
            _logger.warning(f"No se pudo crear el registro de actividad para '{model_name}' debido a problemas de permisos. Usuario: {user.login}")
        except Exception as e:
            _logger.error(f"Error al crear registro de actividad para '{model_name}': {e}", exc_info=True)


# --- SOBREESCRITURA DE BASEMODEL PARA CAPTURAR ACTIVIDADES GLOBALES ---
class BaseModelExtended(models.AbstractModel):
    _inherit = 'base' # Extiende el modelo base (models.BaseModel subyacente)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        # Asegúrate de no registrar actividades del propio user.activity o modelos específicos del sistema
        if self._name != 'user.activity' and not self.env.context.get('skip_activity_logging'):
            user = self.env.user
            model_name = self._name
            for record in records:
                self.env['user.activity'].create_activity_record(
                    user, 'create', model_name, record.id, record.display_name
                )
        return records

    def write(self, vals):
        # Es importante capturar los datos ANTES de la escritura, por si la escritura falla
        # o cambia el display_name.
        # Capturamos los datos relevantes de los registros que van a ser modificados.
        if self._name != 'user.activity' and not self.env.context.get('skip_activity_logging'):
            user = self.env.user
            model_name = self._name
            # Almacenar los datos de los registros ANTES de la operación
            records_data_before = [{'id': record.id, 'display_name': record.display_name} for record in self]
            
            result = super().write(vals) # Realizar la escritura
            
            # Registrar la actividad DESPUÉS de la operación exitosa
            # Iteramos sobre los datos almacenados antes, ya que 'self' podría ser un record vacío si se eliminó
            for rec_data in records_data_before:
                self.env['user.activity'].create_activity_record(
                    user, 'write', model_name, rec_data['id'], rec_data['display_name']
                )
            return result
        return super().write(vals)


    def unlink(self):
        # Es crucial capturar los datos antes de la eliminación, ya que después no existirán.
        if self._name != 'user.activity' and not self.env.context.get('skip_activity_logging'):
            user = self.env.user
            model_name = self._name
            # Copiamos los datos antes de eliminarlos, ya que después no existirán en la base de datos
            records_data_before_unlink = [{'id': record.id, 'display_name': record.display_name} for record in self]
            
            result = super().unlink() # Realizar la eliminación
            
            # Registrar después de la operación de eliminación exitosa
            for rec_data in records_data_before_unlink:
                self.env['user.activity'].create_activity_record(
                    user, 'unlink', model_name, rec_data['id'], rec_data['display_name']
                )
            return result
        return super().unlink()