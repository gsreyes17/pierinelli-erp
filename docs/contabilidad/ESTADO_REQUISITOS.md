# Estado de los requisitos del cliente

Actualizado el 13 de agosto de 2026. Este documento responde punto por punto al listado de [verificacion_cliente.md](verificacion_cliente.md): convierte cada requisito en una ruta de uso, distingue lo que ya se puede operar de lo que exige aprobación contable o una integración externa, e incorpora las correcciones de la auditoría de código del 13 de agosto.

## Lectura rápida

- **Operativo:** se puede usar hoy en la base de pruebas.
- **Operativo con parametrización:** el flujo existe, pero el contador debe validar cuentas, diarios, impuestos, tasas o productos antes de usarlo con información real.
- **Proyecto de integración:** requiere credenciales, certificado, proveedor o una decisión funcional; no se debe presentar como terminado.

> **Verificación funcional (14 de agosto de 2026):** los ciclos principales se
> ejecutaron completos de punta a punta contra la base de pruebas: boleta (03)
> a cliente con DNI y factura (01) a cliente con RUC, ambas con IGV; venta PEN
> cotización→entrega→factura→pago; venta USD con tasa SUNAT/corporativa
> elegible; nota de crédito (07) aplicada; anticipo 50% descontado en la
> factura final; compra de servicio con número de documento del proveedor,
> control de detracción y pago; recepción de planchas con su wizard y lotes;
> caja chica abrir→gasto→reponer→arqueo→cerrar; arqueo diario de cobranzas; y
> anulación de factura. Los 13 formatos de Libros/SIRE generan XLSX, TXT y PDF.

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
| Detracciones y retenciones | **Registro de control; integración pendiente** | En la factura, pestaña **Control tributario**, o en **Contabilidad → Contabilidad → Detracciones y Retenciones**. El módulo registra base, porcentaje, constancia y estado; **no calcula el asiento del depósito ni genera una "factura de detracción"**. El depósito real y su contabilización se validan con el contador. |
| Importación USD y kardex final PEN | **Operativo con parametrización y prueba** | Cree la OC USD, valide la recepción y abra **Inventario → Operaciones → Recepciones**. En la recepción validada agregue la pestaña **Costos adicionales**, pulse **Preparar costeo**, calcule y valide el costo en destino. Revise valoración, cuentas y tipo de cambio antes de un cierre real. |
| Traslado entre sucursales con flete, seguridad u otros | **No operativo hoy** | La pantalla permite agregar costos a una transferencia interna, pero un costo en destino de Odoo aplicado sobre movimientos internos termina en una operación silenciosa sin efecto: no genera asiento ni modifica el costo AVCO. La corrección está pendiente de diseño; no debe prometerse este flujo hasta resolverla. |
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
| Número emitido externamente | **Operativo como control interno** | En la factura, bloque **Control interno**, use **Número externo SUNAT**. Es un campo paralelo de referencia (`numero_externo`): **no cambia la serie ni el correlativo** con los que el documento sale en los libros. Nunca edite la secuencia interna de un comprobante publicado. |
| Factura a título gratuito | **No cubierto** | No existe hoy ningún desarrollo para este caso. Su tratamiento tributario como CPE exige reglas específicas y la integración de emisión electrónica elegida. |

## Los 20 puntos de contabilidad

Documento práctico basado en los puntos 1 al 20 de [verificacion_cliente.md](verificacion_cliente.md). Las rutas se indican para el usuario **Administrador**; el usuario **contabilidad** tiene acceso operativo, pero la configuración sensible se reserva al responsable/Administrador.

### 1. Plan de cuentas, reportes y diferencia de cambio

**Estado: Operativo con configuración.**

1. Entre a **Contabilidad → Configuración → Contabilidad → Plan de cuentas**.
2. Pulse **Nuevo** para una cuenta o abra una existente para modificarla.
3. Complete código, nombre, tipo de cuenta y opciones de conciliación según el PCGE aprobado.
4. Para reportes, vaya a **Contabilidad → Reportes** y elija Balance, Estado de resultados, Mayor o Balance de comprobación. Los reportes usan la clasificación/tipo de las cuentas y los saldos contabilizados.
5. Para diferencia de cambio, el contador debe revisar las cuentas de ganancia y pérdida cambiaria en la configuración contable y probar un pago PEN de una factura USD antes de operar en producción.

No se debe cambiar cuentas ya usadas sin criterio contable ni borrar cuentas con movimientos.

### 2. Centros de costo y dimensiones

**Estado: Operativo mediante analítica.**

1. Entre a **Contabilidad → Configuración → Dimensiones Analíticas**.
2. Cree un plan para cada dimensión requerida: `Área`, `Subárea`, `Proyecto`, `Sucursal` o `Presupuesto`.
3. Dentro de cada plan cree las cuentas analíticas, por ejemplo: Área Comercial, Área Operaciones, Proyecto Obra A o Sucursal Lima.
4. Al registrar una factura o asiento, distribuya la línea contable entre las dimensiones correspondientes.
5. Para presupuestar por centro de costo, vaya a **Contabilidad → Presupuestos → Nuevo**, agregue cuenta, centro de costo e importe; luego pulse **Aprobar**.

El presupuesto toma únicamente la parte efectivamente distribuida al centro de costo indicado.

### 3. Tipos de comprobante y planilla de movilidad

**Estado: Operativo.**

1. Entre a **Contabilidad → Configuración → Tipos de Comprobantes**.
2. Revise los tipos iniciales: Factura, Boleta, Nota de crédito, Nota de débito, Recibo por honorarios, DAM/Importación y `PM · Planilla de movilidad`.
3. Pulse **Nuevo** si necesita uno adicional; indique código, alcance, si requiere RUC y si permite crédito fiscal según el contador.
4. En una factura, use el bloque **Control interno → Tipo de comprobante**.
5. En **Caja Chica → Movimientos**, use **Tipo de sustento**. Para una planilla de movilidad seleccione `PM · Planilla de movilidad`.

El tipo es un control interno: no sustituye una validación o emisión electrónica SUNAT.

### 4. Tipo de cambio SUNAT y tipo de cambio corporativo/caja

**Estado: Operativo.** El botón **Actualizar desde SUNAT** funciona (el 13 de agosto se corrigió que no apareciera con la lista vacía) y admite tasas manuales y corporativas; el cron diario sigue desactivado por diseño hasta la primera prueba manual en el servidor. El paso a paso completo está en la [Guía de contabilidad operativa](GUIA_CONTABILIDAD_OPERATIVA.md).

### 5. Guías de remisión electrónica y estado SUNAT

**Estado: No cubierto.**

> **Nota SUNAT (aplica a los puntos 5, 9, 10 y 18):** el ERP no se conecta a ninguna API productiva de SUNAT ni actúa como emisor electrónico; los archivos y reportes descritos son de control interno. La ruta para una futura integración (Beta, credenciales, certificado, CDR) está en [SUNAT_PRUEBAS.md](SUNAT_PRUEBAS.md).

Hoy solo existe un listado de albaranes etiquetado "guías" dentro del asistente SIRE. No hay emisión electrónica de GRE: no se genera XML, no se recibe CDR ni se consulta el estado en SUNAT, y Odoo Community no incluye el módulo `l10n_pe_edi_stock`. Las entregas y transferencias se controlan en **Inventario → Operaciones → Entregas / Transferencias**, pero la GRE electrónica es un proyecto de integración completo aún no iniciado.

### 6. Asientos tipo recurrentes

**Estado: Operativo.**

1. Entre a **Contabilidad → Contabilidad → Plantillas de Asientos**.
2. Pulse **Nuevo**, complete nombre, diario y descripción.
3. En líneas, agregue cuenta, glosa, Debe/Haber y monto fijo o porcentaje del importe base.
4. Pulse **Generar asiento**, indique fecha, referencia e importe base.
5. Revise el borrador generado y publíquelo cuando cuadre y sea aprobado.

Úselo para provisiones, planillas, depreciación manual, seguros u otros procesos repetitivos.

### 7. Asientos manuales y provisiones mensuales

**Estado: Operativo.**

1. Abra **Contabilidad → Contabilidad → Asientos contables → Nuevo**.
2. Elija diario general, fecha y referencia.
3. Agregue líneas; el total Debe debe ser igual al total Haber.
4. En **Control interno**, seleccione **Tipo de operación: Provisión** si corresponde.
5. Pulse **Publicar** solo después de la revisión contable.

Para una provisión recurrente es preferible crear antes una plantilla del punto 6.

### 8. Asientos de destino, clase 6 y clase 9

**Estado: No cubierto como automatización.**

No existe ningún mecanismo automático de destino 6→9. A lo sumo puede resolverse manualmente: el contador define el mapa de cuentas, se crea una plantilla en **Plantillas de Asientos** y cada mes se genera, revisa y publica el borrador. La automatización, si se decide, es un desarrollo pendiente que depende de la política de costos de la empresa.

### 9. Libros SIRE y cruce SUNAT

**Estado: Parcial.**

Los formatos 14.1, 8.1, 8.2, 1.1, 1.2, 3.x, 7.1 y 13.1 existen como vistas con exportación XLSX/PDF/TXT y nomenclatura PLE de 33 caracteres. Sin embargo, el TXT generado es una demostración estructurada, **no** la estructura oficial de campos RVIE/RCE, y no hay cruce con SUNAT porque no se ha conectado la API SIRE (OAuth 2.0 con credenciales generadas en SOL).

Mientras tanto, use **Contabilidad → Reportes** para control interno y compare manualmente con SOL. La integración requiere credenciales, decisión del contador y pruebas por periodo.

### 10. Libros PRICO, régimen general y contabilidad completa

**Estado: Parcial — reportes internos sólidos, libros oficiales pendientes.**

1. Vaya a **Contabilidad → Reportes**.
2. Seleccione el reporte: Libro Diario, Libro Mayor, Balance de comprobación, Situación financiera, Resultados, Flujo de efectivo, antigüedad CxC/CxP o resumen IGV.
3. Ingrese el rango de fechas y genere el PDF/resultado.

El Diario, el Mayor y el Balance de comprobación son sólidos como reportes internos. El formato 7.1 (activos) es solo una base de revisión: muestra la depreciación acumulada en 0.0 porque no hay motor de activos fijos en Community. El Registro de Costos no existe. Los archivos oficiales electrónicos son proyectos de localización/integración adicionales.

Para el inventario permanente, además del formato 13.1 del wizard SIRE, existe el **Kardex de Producto físico y valorizado** (14 de agosto): `Inventario → Reportes → Kardex de Producto`, o el botón **Kardex** en la ficha del producto. Saldo corriente movimiento a movimiento, salidas valorizadas al promedio (AVCO), con vista en pantalla, Excel y PDF; el saldo final cuadra contra el stock a la mano.

### 11. Reportes de gastos por dimensiones

**Estado: Operativo con uso disciplinado de analítica.**

1. Al contabilizar compra, caja o asiento, distribuya cada gasto por Área/Proyecto/Sucursal según corresponda.
2. Abra **Contabilidad → Reportes → Reporte analítico** para revisar movimientos por dimensión.
3. Para comparar gasto contra presupuesto, abra **Contabilidad → Presupuestos**, ingrese al período y revise ejecutado, saldo y porcentaje en las líneas.

Sin distribución analítica en la línea, un gasto no se puede atribuir correctamente a una dimensión.

### 12. Contabilidad PEN y reportes PEN/USD

**Estado: Parcial.**

1. Mantenga PEN como moneda de la compañía en **Contabilidad → Configuración → Monedas**.
2. Active USD y configure sus tasas mediante el punto 4.
3. Emita compras y ventas USD eligiendo la moneda en el documento.

La contabilidad en PEN funciona. Ningún reporte propio se expresa todavía en USD: los importes en moneda extranjera se consultan documento por documento. Una presentación consolidada en USD requiere definir tasa y metodología de conversión con el contador y un desarrollo de reporte.

### 13. Traslado entre sucursales con costos de transporte

**Estado: No operativo hoy.**

El flujo en pantalla permite crear la transferencia interna, agregar líneas en **Costos adicionales** y pulsar **Preparar costeo**; pero un costo en destino de Odoo aplicado sobre movimientos internos termina en una operación silenciosa sin efecto: no genera asiento contable ni modifica el costo AVCO de los productos. La corrección está pendiente de diseño; este flujo no debe prometerse ni usarse para valorizar traslados hasta que se resuelva.

### 14. Rotura, diferencias y reclamos al seguro

**Estado: Operativo base; cuentas y asientos por aprobar.**

1. Registre el ajuste físico en **Inventario → Operaciones → Ajustes de inventario** o use el flujo de merma/corte cuando corresponda.
2. Identifique claramente el motivo en la referencia o glosa: rotura, diferencia, reclamo al seguro, etc.
3. Cuando el contador apruebe las cuentas, use una plantilla en **Contabilidad → Contabilidad → Plantillas de Asientos** para el asiento de rotura, pérdida o reclamo.
4. Genere, revise y publique el asiento.

Las cuentas de inventario, pérdida y recupero/seguro deben ser definidas por el contador antes de contabilizar un caso real.

### 15. Importar, exportar, predeterminar, duplicar, anular y eliminar asientos

**Estado: Operativo, con control contable.** La carga segura usa **Plantilla Excel → Importar asientos** (valida encabezados, cuentas, diarios, fechas y cuadre antes de crear borradores); un asiento publicado no se borra, se revierte. El paso a paso completo está en la [Guía de contabilidad operativa](GUIA_CONTABILIDAD_OPERATIVA.md).

### 16. Reportes de guías/facturas y costos de servicios

**Estado: Parcial.**

- Entregas y transferencias: **Inventario → Operaciones → Entregas / Transferencias**. Use filtros por fecha, cliente, estado u origen para identificar entregas facturadas o pendientes.
- Facturas: **Contabilidad → Clientes → Facturas**; filtre por estado, fecha, cliente y referencia de pedido/entrega.
- Costos de servicios: clasifique las facturas de proveedor como **Servicios** en **Control interno** y use cuentas/dimensiones para analizarlos.

No existe aún un reporte único y automático que cruce guía facturada, factura despachada, servicio realizado y costo diferido. Para construirlo correctamente se debe definir qué campos, fechas y cuentas determinan cada concepto.

### 17. Cierres mensuales y anuales

**Estado: Operativo.** El 13 de agosto se corrigió un error de permisos (AccessError) que impedía al responsable contable aplicar el bloqueo: ya no es exclusivo del Administrador.

1. Complete conciliaciones, caja, impuestos, provisiones y revisiones.
2. Entre a **Contabilidad → Contabilidad → Cierres Contables → Nuevo**.
3. Indique nombre, tipo de cierre (Contable, Tributario o Ventas), fecha a bloquear y el sustento.
4. Pulse **Aplicar bloqueo**.
5. El sistema impide registrar o modificar documentos en el período bloqueado según el tipo elegido.

La opción **Revertir bloqueo** es excepcional, solo para responsable/Administrador, y queda registrada.

### 18. Balance de comprobación según SUNAT

**Estado: Parcial.**

1. Abra **Contabilidad → Reportes → Balance de comprobación**.
2. Indique la fecha/rango solicitado y genere el reporte.
3. Revise sumas, saldos y que no existan borradores que alteren la lectura.

El balance de sumas y saldos de 8 columnas es correcto y útil para control interno, pero no incluye las columnas del anexo oficial SUNAT (ajustes y resultados por naturaleza y por función). Ese formato adicional sigue pendiente.

### 19. Asientos de cierre y apertura anual

**Estado: No cubierto.**

Hoy solo existe el bloqueo de fechas del punto 17; no hay ningún proceso de cierre/apertura anual (cancelación de resultados, traslado a patrimonio, asiento de apertura). Puede ejecutarse manualmente con plantillas bajo criterio del contador, pero como funcionalidad el punto no está cubierto y no debe presentarse como resuelto.

### 20. Niveles de usuario y control de ingreso

**Estado: Operativo.**

1. Como Administrador vaya a **Ajustes → Usuarios y compañías → Usuarios**.
2. Abra el usuario y asigne solo los módulos/niveles que necesita: Ventas, Compras, Inventario, Contabilidad, Analítica o Administración.
3. Use `contabilidad` para operación contable; reserve Administrador para configuración, tipos de comprobante y tareas programadas.
4. Evite compartir usuarios y mantenga contraseñas individuales.

En este entorno de prueba existen usuarios demostrativos. Antes de producción cambie contraseñas, elimine accesos no requeridos y valide una matriz de permisos con el cliente.

## Precondiciones antes de producción

1. Contador: aprobar plan de cuentas, cuentas de caja/bancos, anticipos, diferencia de cambio, retenciones, detracciones y ajustes de arqueo.
2. Administrador: configurar diarios PEN/USD, tasas de cambio, métodos de pago, impuestos, condiciones de pago, permisos y secuencias.
3. Operación: ejecutar una prueba completa por cada caso sensible: anticipo USD, pago PEN de factura USD, sobrepago, nota de crédito, importación con costo en destino, detracción y cierre de caja.
4. Dirección: decidir si se implementan SUNAT/OSE-PSE, PLE/SIRE, Banco de la Nación/API bancaria y el cuadre diario multimoneda; cada uno es un proyecto de integración adicional.

Las detracciones son un sistema regulado de SUNAT y las retenciones tienen condiciones y tasas que deben verificarse por comprobante; por ello el módulo deja porcentaje, base y constancia bajo control del contador, en vez de aplicar una tasa universal. Consulte las referencias oficiales de [detracciones](https://emprender.sunat.gob.pe/principales-impuestos/impuesto-general-las-ventas-igv/sistema-detracciones-igv) y [retenciones del IGV](https://emprender.sunat.gob.pe/principales-impuestos/impuesto-general-las-ventas-igv/regimen-retencion-igv) antes de parametrizar.

Tampoco hay API bancaria para importar extractos, ejecutar transferencias o confirmar depósitos. Los pagos y constancias se registran manualmente hasta que se integre el banco.

## Referencias relacionadas

- [Verificación operativa solicitada por el cliente](verificacion_cliente.md)
- [Guía de contabilidad operativa](GUIA_CONTABILIDAD_OPERATIVA.md)
- [Pruebas SUNAT](SUNAT_PRUEBAS.md)
