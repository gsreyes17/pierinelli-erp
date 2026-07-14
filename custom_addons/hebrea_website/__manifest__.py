{
    'name': 'Academia Hebrea - Sitio Web',
    'version': '19.0.1.0.0',
    'category': 'Website',
    'summary': 'Página web institucional de la Academia Hebrea de Panamá',
    'description': (
        "Sitio web MVP de la Academia Hebrea de Panamá. "
        "Instala el módulo Website con la página principal ya diseñada "
        "(paleta azul marino / dorado, tipografías Newsreader y Hanken Grotesk)."
    ),
    'author': 'Giancarlo Olivares',
    'license': 'LGPL-3',
    'depends': ['website'],
    'data': [
        'views/homepage.xml',
        'views/footer.xml',
        'views/disable_website_login.xml',
        'data/website_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'hebrea_website/static/src/scss/hebrea.scss',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'application': False,
    'installable': True,
}
