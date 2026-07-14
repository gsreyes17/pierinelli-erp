def _setup_spanish(env):
    """Asegura un idioma espanol como predeterminado del SITIO WEB, sin alterar
    los usuarios ni otros proyectos que compartan la misma base (ej. Pierinelli es_419)."""
    Lang = env['res.lang'].with_context(active_test=False)
    # Reusar el espanol ya activo (es_419, es_ES...) antes que instalar otro
    lang = Lang.search([('active', '=', True),
                        ('code', 'in', ['es_419', 'es_PA', 'es_ES', 'es'])], limit=1)
    if not lang:
        lang = Lang.search([('code', 'in', ['es_PA', 'es_ES', 'es_419'])], limit=1)
        if lang and not lang.active:
            env['base.language.install'].create(
                {'lang_ids': [(6, 0, [lang.id])]}).lang_install()
    if not lang:
        return
    # Solo configurar el idioma del sitio web (no toca usuarios ni el default de contactos)
    websites = env['website'].search([])
    websites.write({
        'default_lang_id': lang.id,
        'language_ids': [(6, 0, [lang.id])],
    })


def post_init_hook(env):
    """Ajustes de datos que no conviene hacer por XML (ids variables entre versiones)."""
    Menu = env['website.menu']

    # Renombrar el menú "Home" a "Inicio"
    home_menus = Menu.search([('url', '=', '/'), ('parent_id', '!=', False)])
    home_menus.write({'name': 'Inicio'})

    # Quitar el menú "Contact us" que crea website por defecto (el MVP usa anclas)
    contact_menus = Menu.search([('url', '=', '/contactus')])
    contact_menus.unlink()

    # Nombre del sitio
    websites = env['website'].search([])
    websites.write({'name': 'Academia Hebrea de Panamá'})

    # Registro solo por invitación (sin signup público)
    env['ir.config_parameter'].sudo().set_param('auth_signup.invitation_scope', 'b2b')

    _setup_spanish(env)
