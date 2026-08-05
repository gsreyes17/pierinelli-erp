# -*- coding: utf-8 -*-
{
    'name': 'Pierinelli MCP Inventario',
    'version': '19.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Base segura para un asistente de consultas de inventario',
    'description': """Entorno inicial del asistente de inventario.

No conecta todavia con proveedores de IA externos. Expone tres consultas
predefinidas y de solo lectura, que luego pueden convertirse en herramientas
MCP o ser llamadas por un proveedor como DeepSeek.
""",
    'author': 'Pierinelli',
    'license': 'LGPL-3',
    'depends': ['stock', 'pierinelli_planchas'],
    'data': ['security/ir.model.access.csv'],
    'assets': {
        'web.assets_backend': [
            'pierinelli_mcp_inventario/static/src/chat/*.js',
            'pierinelli_mcp_inventario/static/src/chat/*.xml',
            'pierinelli_mcp_inventario/static/src/chat/*.scss',
        ],
    },
    'installable': True,
    'application': False,
}
