# Pruebas oficiales SUNAT y decisión de integración

## Respuesta corta

Sí existe un entorno de pruebas oficial y sin costo de SUNAT, pero no una API libre que permita convertir un ERP en emisor electrónico sin configuración. El servicio Beta sirve para comprobar estructuras XML UBL de prueba; no se debe enviar información real ni usarlo como producción.

Para el **tipo de cambio USD/PEN** sí se implementó una ventaja práctica sin credenciales: el ERP consulta la publicación pública de SUNAT desde **Contabilidad → Configuración → Tipos de Cambio → Actualizar desde SUNAT**. La automatización diaria queda desactivada hasta verificar una primera consulta desde Render, porque es una página web pública y no una API REST con contrato de estabilidad. SUNAT explica que la cotización publicada corresponde al cierre SBS del día anterior y que, si no hay publicación, se usa el día inmediato anterior.

El endpoint Beta oficial de factura es `https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService?wsdl`. SUNAT indica para las pruebas el usuario formado por `RUC + MODDATOS` y contraseña `MODDATOS`. Antes de usarlo debe confirmarse el manual vigente y utilizar datos ficticios.

## Lo que hace falta antes de programar el conector

1. RUC, razón social, domicilio fiscal y condición de emisor electrónico confirmados.
2. Decisión escrita: envío directo a SUNAT o proveedor OSE/PSE.
3. Certificado digital, usuario SOL secundario y permisos adecuados. Las claves no se suben al repositorio ni se pegan en chats; se cargan como secretos del entorno cuando el módulo esté listo.
4. Series por sucursal, tipos de CPE, catálogo de productos/servicios, impuestos, detracciones y reglas de notas de crédito aprobados por el contador.
5. Casos de aceptación: factura USD/PEN, crédito, anticipo, nota de crédito, operación gratuita, detracción, guía de remisión y contingencia.

## Alcance de una integración correcta

- Generar XML UBL 2.1 y firmarlo digitalmente.
- Comprimir, enviar, guardar XML, CDR, hash, códigos y mensajes de rechazo.
- Consultar estado y reintentar de forma idempotente, sin duplicar comprobantes.
- Producir representación PDF y permitir su descarga al cliente.
- Integrar guía de remisión electrónica, cuando se apruebe su flujo logístico.
- Mantener una bitácora auditable y separar configuración Beta de Producción.
- Para SIRE, usar sus APIs oficiales con token/credenciales creados en SOL y validar la propuesta antes de aceptarla; no confundirlo con los reportes internos del ERP.

## Decisión recomendada

Para esta entrega, mantenga el ERP como fuente operativa y use los campos de **Número externo SUNAT**, control tributario y tipos de comprobante. Luego implemente un conector dedicado en una fase con datos del cliente y pruebas formales. Conectar ahora sin certificado, Clave SOL, series ni casos aprobados crearían documentos inválidos o un riesgo de seguridad.

Fuentes oficiales: [servicios web disponibles de SUNAT](https://orientacion.sunat.gob.pe/guias-manuales-y-servicios-web), [servicio Beta UBL](https://cpe.sunat.gob.pe/noticias/servicio-beta-para-realizar-pruebas-ubl-21), [manual de SIRE API](https://cpe.sunat.gob.pe/sites/default/files/2026-06/Manual%20del%20servicio%20API%20del%20Registro%20de%20Ventas%20e%20Informaci%C3%B3n%20Electr%C3%B3nica.%20v30.pdf).
