# user_activity_monitor/__manifest__.py
{
    'name': "Monitor de Actividad de Usuarios",
    'summary': """
        Módulo para monitorear y visualizar la actividad de los usuarios en Odoo,
        incluyendo módulos usados, acciones realizadas y porcentaje de actividad.
    """,
    'description': """
        Este módulo proporciona herramientas gerenciales para analizar la usabilidad de la plataforma Odoo.
        Permite visualizar gráficos de actividad de usuarios y departamentos,
        identificar patrones de uso y fomentar la adopción.
    """,
    'author': "Grupo Brame",
    'website': "http://www.grupobrame.com",
    'category': 'Productivity/Dashboard',
    'version': '1.0',
    'depends': ['base', 'web', 'hr'], # 'hr' es útil si quieres filtrar por departamento de empleado
    'data': [
        'security/ir.model.access.csv', # Asegúrate de crear este archivo
        'models/user_activity.xml', # Si necesitas una vista de formulario/árbol para el modelo
        'views/user_activity_views.xml',
        'views/user_activity_dashboard.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'images': ['static/description/icon.png'], # Asegúrate de tener un icono
}