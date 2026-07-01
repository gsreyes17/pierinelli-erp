# -*- coding: utf-8 -*-
{
    'name': 'Pierinelli Peru (SUNAT)',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Localizacion peruana + compras (l10n_pe, account, purchase)',
    'description': """
Agrega la localizacion peruana y compras al proyecto Pierinelli. La configuracion
del plan de cuentas, IGV 18%, RUC y la generacion de facturas se realiza en el
seed post-install (seed_pe.py), ya que el plan contable solo se carga de forma
fiable con el registry cargado.

NOTA: NO envia comprobantes reales a SUNAT (requiere certificado digital, RUC
habilitado y un OSE / modulo EDI de Enterprise u OCA). Es una simulacion funcional.
""",
    'author': 'Pierinelli',
    'website': 'https://pierinelli.com',
    'license': 'LGPL-3',
    'depends': ['pierinelli_data', 'l10n_pe', 'purchase'],
    'data': [],
    'installable': True,
    'application': False,
}
