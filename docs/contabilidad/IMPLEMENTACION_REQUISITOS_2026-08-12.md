# Implementación frente a los requisitos del cliente

Actualizado el 12 de agosto de 2026. Este documento convierte el listado del cliente en rutas de uso y distingue lo que ya se puede operar de aquello que exige aprobación contable o una integración externa.

## Lectura rápida

- **Operativo:** se puede usar hoy en la base de pruebas.
- **Operativo con parametrización:** el flujo existe, pero el contador debe validar cuentas, diarios, impuestos, tasas o productos antes de usarlo con información real.
- **Proyecto de integración:** requiere credenciales, certificado, proveedor o una decisión funcional; no se debe presentar como terminado.

## Caja chica y tesorería

| Requisito | Estado | Ruta exacta |
|---|---|---|
| Apertura, gastos, planilla de movilidad, reposición y cierre de caja chica PEN | **Operativo** | **Contabilidad → Contabilidad → Caja Chica**. Cree la caja, pulse **Abrir caja**; agregue movimientos y **Contabilizar**; use **Reponer desde banco**, registre el efectivo contado, confirme el arqueo y cierre. |
| Sustento de movilidad | **Operativo** | En la pestaña **Movimientos** seleccione **Tipo de sustento: PM · Planilla de movilidad**, documento, beneficiario, cuenta de gasto e importe. |
| Factura de proveedor pagada desde caja | **Operativo con procedimiento** | Registre primero la factura en **Proveedores → Facturas**; desde la factura use **Registrar pago** y el diario de efectivo. Caja Chica sirve además para gastos menores y su sustento. |
| Cuadre diario de efectivo PEN/USD | **Operativo para cobros registrados** | **Contabilidad → Contabilidad → Arqueo Diario de Cobranzas → Nuevo**. Seleccione fecha y diario de efectivo, ingrese el efectivo contado, confirme y cierre. El sistema compara los cobros cobrados en ese diario y moneda; una diferencia se sustenta y regulariza con el asiento autorizado, no automáticamente. |
| Reposición bancaria | **Operativo** | Dentro de una Caja Chica abierta pulse **Reponer desde banco**. Revise el asiento generado en la pestaña **Reposiciones**. |

## Compras, importaciones e inventario

| Requisito | Estado | Ruta exacta |
|---|---|---|
| Proveedores, orden de compra, factura y pago en PEN/USD | **Operativo con parametrización** | **Compras → Pedidos → Proveedores / Solicitudes de presupuesto**; y **Proveedores → Facturas**. En la factura elija la moneda, clasifique la compra y pulse **Registrar pago** tras publicarla. |
| Tipo de compra: mercadería, servicio, gasto o activo fijo | **Operativo** | En la factura de proveedor, bloque **Control interno**, elija **Clasificación de compra**. Es una clasificación de control; las líneas y sus cuentas contables definen el asiento. |
| Detracciones y retenciones | **Operativo como control; integración pendiente** | En la factura, pestaña **Control tributario**, o en **Contabilidad → Contabilidad → Detracciones y Retenciones**. Registre comprobante, base, porcentaje, constancia y estado. El depósito real y el asiento se validan con el contador. |
| Importación USD y kardex final PEN | **Operativo con parametrización y prueba** | Cree la OC USD, valide la recepción y abra **Inventario → Operaciones → Recepciones**. En la recepción validada agregue la pestaña **Costos adicionales**, pulse **Preparar costeo**, calcule y valide el costo en destino. Revise valoración, cuentas y tipo de cambio antes de un cierre real. |
| Traslado entre sucursales con flete, seguridad u otros | **Operativo** | Abra la transferencia interna validada en **Inventario → Operaciones → Transferencias**, agregue líneas en **Costos adicionales** y use **Preparar costeo**. |
| Roturas, diferencias de inventario y reclamos de seguro | **Operativo base; asiento tipo por definir** | Registre el ajuste/operación de inventario según su motivo y genere el asiento con **Contabilidad → Contabilidad → Plantillas de Asientos** cuando el contador haya aprobado cuentas y glosa. |

## Ventas y cobranzas

| Requisito | Estado | Ruta exacta |
|---|---|---|
| Clientes y referidores | **Operativo** | **Ventas → Pedidos → Clientes → Nuevo**. En la ficha del cliente, pestaña **Referidos**, seleccione el referidor. |
| Cotización, orden y factura USD | **Operativo con parametrización** | **Ventas → Pedidos → Cotizaciones → Nuevo**; elija USD, confirme, valide entrega si corresponde y pulse **Crear factura**. |
| Facturación por entrega | **Operativo** | Configure la política de facturación del producto por cantidades entregadas; desde la orden confirme **Entrega**, valide y luego **Crear factura**. |
| Contado, crédito, transferencia, efectivo, sobrepago y saldo a favor | **Operativo estándar, requiere prueba de diarios** | Publique la factura y pulse **Registrar pago**. El crédito restante del cliente se concilia en un documento posterior. Pruebe una vez cada diario/moneda antes de producción. |
| Pago PEN de factura USD y diferencia de cambio | **Operativo con parametrización y prueba** | Registre tipo de cambio en **Contabilidad → Configuración → Tipos de Cambio**, seleccione el origen en la factura USD y concilie el pago PEN con las cuentas de ganancia/pérdida aprobadas. |
| Anticipo USD, aplicación, notas de crédito y anulación | **Operativo estándar, requiere configuración** | Desde la orden: **Crear factura → Anticipo**. Para una nota de crédito, abra la factura publicada y pulse **Nota de crédito**. Un documento publicado se revierte; no se elimina. |
| Número emitido externamente | **Operativo como control interno** | En la factura, bloque **Control interno**, use **Número externo SUNAT**. Nunca edite la secuencia interna de un comprobante publicado. |
| Factura a título gratuito | **Parcial** | Puede registrarse comercialmente, pero su validez como CPE exige reglas tributarias y la integración de emisión electrónica elegida. |

## Contabilidad, presupuestos y dimensiones

| Requisito | Estado | Ruta exacta |
|---|---|---|
| Plan de cuentas, diarios, cuentas de diferencia de cambio | **Operativo** | **Contabilidad → Configuración → Contabilidad → Plan de cuentas / Diarios**. Solo el responsable contable debe modificar esta configuración. |
| Tipos de comprobantes y planillas de movilidad | **Operativo** | **Contabilidad → Configuración → Tipos de Comprobantes**. Los tipos iniciales se pueden editar o ampliar: factura, boleta, RHE, DAM y PM. |
| Dimensiones: área, subárea, presupuesto, proyecto y sucursal | **Operativo mediante analítica** | Como Administrador: **Contabilidad → Configuración → Dimensiones Analíticas**. Cree un plan por dimensión y sus cuentas analíticas; use la distribución analítica en líneas contables. Para presupuesto, el campo **Centro de costo / obra** ahora calcula únicamente el porcentaje distribuido a ese centro. |
| Tipo de cambio SUNAT y caja | **Operativo manual y consulta automática** | Como Administrador, vaya a **Contabilidad → Configuración → Tipos de Cambio → Actualizar desde SUNAT**. La consulta toma la última cotización pública USD/PEN; la tasa corporativa sigue siendo manual. Si SUNAT no publica o cambia su página, use **Nuevo** como respaldo. |
| Asientos tipo, provisiones y depreciación manual | **Operativo** | **Contabilidad → Contabilidad → Plantillas de Asientos**. Pulse **Generar asiento**, revise el borrador y publíquelo. |
| Asientos de destino clase 6 o 9 | **Operativo con diseño contable** | Se resuelven con plantillas de asientos y distribución analítica. El contador debe definir el mapa 6→9, cuentas y condición de cada asiento antes de automatizarlo. |
| Presupuesto por cuenta y centro de costo | **Operativo** | **Contabilidad → Presupuestos → Nuevo**. Cree período y líneas; seleccione cuenta, centro de costo opcional e importe, luego **Aprobar**. |
| Cierre mensual/anual que bloquea modificaciones | **Operativo** | Solo Administrador/responsable: **Contabilidad → Contabilidad → Cierres Contables → Nuevo**. Indique tipo y fecha, agregue sustento y pulse **Aplicar bloqueo**. El bloqueo usa la fecha estándar de la compañía; una reversión queda registrada y es excepcional. |
| Asientos manuales, importar/exportar, duplicar, anular | **Operativo con importación guiada** | **Contabilidad → Contabilidad → Asientos contables → Plantilla Excel** para descargar la estructura segura; luego **Importar asientos** valida cuentas, diarios, fechas y cuadre antes de crear borradores. La importación/exportación estándar sigue disponible. Los publicados se revierten, no se borran. |
| Libros de gestión y estados financieros | **Operativo como reporte interno** | **Contabilidad → Reportes**. Incluye diario, mayor, balance de comprobación, situación financiera, resultados, flujo de caja, antigüedad y resumen IGV. No equivale a un archivo PLE/SIRE presentado ante SUNAT. |
| Planillas, activos fijos y depreciación automática | **Proyecto adicional** | No hay módulo de nómina ni registro de activos desplegado. Hoy se usan asientos tipo/manuales. La automatización exige reglas de RR.HH., vidas útiles, cuentas y validación del contador. |

## SUNAT, SIRE y guías electrónicas

No se conectó una API productiva ni se almacenaron claves en el repositorio. Eso evita emitir documentos reales o exponer una Clave SOL sin autorización.

SUNAT ofrece un **servicio Beta gratuito** para probar la estructura UBL de facturas, boletas y notas; no es un servicio público anónimo ni valida toda la consistencia comercial. Para probarlo se necesita generar y firmar el XML/ZIP y usar las credenciales de prueba indicadas por SUNAT. La emisión real requiere RUC emisor, Clave SOL secundaria con perfil correspondiente, certificado digital, series autorizadas, XML UBL firmado, gestión de CDR/errores y contingencia. SIRE también exige credenciales API creadas en SOL.

La secuencia segura es:

1. Aprobar plan de cuentas, impuestos, diarios, tipos de comprobante y el flujo de notas/detracciones con el contador.
2. Ejecutar los casos de prueba de esta matriz en una base clonada, sin información real.
3. El cliente entrega por canal seguro RUC, usuario SOL secundario, certificado y decisión entre envío directo/OSE/PSE.
4. Implementar un conector aislado con ambiente **Beta**, pruebas de XML/CDR y bitácora; recién después solicitar pase a producción.

Consulte [Pruebas SUNAT](SUNAT_PRUEBAS.md) antes de iniciar esa fase.
