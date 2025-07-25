# fleet_engomado_color/models/fleet_vehicle.py

from odoo import fields, models

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    engomado_color = fields.Selection([
        ('amarillo', 'Amarillo (5 o 6) Lunes'),
        ('rosa', 'Rosa (7 o 8) Martes'),
        ('rojo', 'Rojo (3 o 4) Miercoles'),
        ('verde', 'Verde (1 o 2) Jueves'),
        ('azul', 'Azul (9 o 0) Viernes'),
    ], string='Color de Engomado',
        help="Color del engomado del vehículo para el programa Hoy No Circula (CDMX).",
        tracking=True)
