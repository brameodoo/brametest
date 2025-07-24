# fleet_engomado_color/__manifest__.py

{
    'name': 'Color Engomado (Hoy No Circula)',
    'version': '17.0.1.0.0',
    'category': 'Fleet',
    'summary': 'Añade el campo de color de engomado del programa Hoy No Circula a los vehículos.',
    'description': """
        Módulo que extiende el modelo fleet.vehicle para incluir un campo de selección
        para el color del engomado del programa "Hoy No Circula" de la Ciudad de México.
        Los colores disponibles son: Amarillo, Rosa, Rojo, Verde, Azul.
    """,
    'author': 'Brame Telecom', # ¡grupo brame!
    'website': 'https://www.grupobrame.com', # grupo brame
    'depends': [
        'fleet', # Dependencia clave: el módulo base de Flota
        'base',  # Módulo base de Odoo
    ],
    'data': [
       # 'security/ir.model.access.csv',
        'views/fleet_vehicle_views.xml',
    ],
    'installable': True,
    'application': False, # No es una aplicación standalone, es una extensión
    'auto_install': False,
    'license': 'LGPL-3',
}