# fleet_engomado_color/models/fleet_vehicle.py

from odoo import fields, models

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    engomado_color = fields.Selection([
        ('amarillo', 'Amarillo (5 o 6)'),
        ('rosa', 'Rosa (7 o 8)'),
        ('rojo', 'Rojo (3 o 4)'),
        ('verde', 'Verde (1 o 2)'),
        ('azul', 'Azul (9 o 0)'),
    ], string='Color de Engomado',
        help="Color del engomado del vehículo para el programa Hoy No Circula (CDMX).",
        tracking=True)