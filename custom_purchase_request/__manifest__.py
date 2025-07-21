# -*- coding: utf-8 -*-
{
    'name': "Compras Nlace",
    'summary': """
        Módulo para que los departamentos puedan crear solicitudes de compra internas
        con visibilidad restringida por departamento y en un entorno multi-compañía.
    """,
    'description': """
        Este módulo introduce un nuevo modelo 'purchase.request' que permite a los usuarios
        crear solicitudes de compra. Utiliza reglas de registro para asegurar que cada
        departamento solo pueda ver sus propias solicitudes, mientras que el equipo de
        compras tiene visibilidad total.
        
        Características:
        - Nuevo menú de Solicitudes de Compra.
        - Flujo de aprobación simple (Borrador -> Aprobado -> Realizado).
        - Asignación automática de departamento en entorno multi-compañía.
        - Seguridad por departamento.
    """,
    'author': "Brame telecom",
    'website': "https://www.grupobrame.com",
    'category': 'Purchases',
    'version': '17.0.1.0.0',
    'web_icon': "custom_purchase_request/static/description/icon.png", # <--- ¡ESTA ES LA LÍNEA CLAVE!    
    'depends': [
        'base',
        'purchase',
        'hr',
        'mail',
    ],
    'data': [
        # Seguridad
        'security/purchase_request_groups.xml',   
        'security/ir.model.access.csv',        
        'security/purchase_request_rules.xml',

        # Datos
        'data/ir_sequence_data.xml',

        # Vistas y Menús
        'views/purchase_request_views.xml',
        'views/purchase_request_menu.xml',
    ],
    'installable': True,
    'application': True, # Marcar como una aplicación completa si quieres que aparezca en el menú de Apps
    'auto_install': False,
    'license': 'LGPL-3',
    'web_icon': "custom_purchase_request,static/description/icon.png", # <--- ¡AÑADE ESTA LÍNEA!
}
