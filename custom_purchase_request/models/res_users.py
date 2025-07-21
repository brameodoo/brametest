# -*- coding: utf-8 -*-
from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    # Odoo 17 ya incluye el campo 'employee_ids' (One2many a hr.employee)
    # que es una relación a todos los registros de empleado asociados a este usuario
    # en las compañías permitidas. Por lo tanto, no es necesario añadirlo aquí.
    # Este archivo se mantiene por si se requieren futuras extensiones en el usuario.
    pass