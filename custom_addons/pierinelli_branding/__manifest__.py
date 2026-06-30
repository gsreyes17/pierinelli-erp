# -*- coding: utf-8 -*-
{
    'name': 'Pierinelli Branding',
    'version': '19.0.1.0.0',
    'category': 'Theme/Backend',
    'summary': 'Identidad visual Pierinelli para el backend (negro / blanco / dorado)',
    'description': """
Personalizacion visual del backend de Odoo para Pierinelli:
- Acento dorado (#C9962F) en botones, enlaces y elementos activos.
- Barra superior negra con logo blanco.
- Pantalla de login con identidad Pierinelli (fondo oscuro + logo blanco).
No modifica ningun modulo del core; todo se aplica por herencia de assets/plantillas.
""",
    'author': 'Pierinelli',
    'website': 'https://pierinelli.com',
    'license': 'LGPL-3',
    'depends': ['web'],
    'data': [
        'views/login_templates.xml',
    ],
    'assets': {
        # Variables de marca: PREPEND para que se carguen ANTES del core
        # y todos los colores derivados (botones, enlaces, mapas) usen el dorado.
        'web._assets_primary_variables': [
            ('prepend', 'pierinelli_branding/static/src/scss/primary_variables.scss'),
        ],
        # Estilos del cliente web (navbar negra, acentos).
        'web.assets_backend': [
            'pierinelli_branding/static/src/scss/backend.scss',
        ],
        # Estilos de la pantalla de login (frontend).
        'web.assets_frontend': [
            'pierinelli_branding/static/src/scss/frontend.scss',
        ],
    },
    'installable': True,
    'application': False,
}
