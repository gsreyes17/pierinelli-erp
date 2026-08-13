# Guia de Contabilidad Operativa

## Alcance y seguridad

Este modulo organiza la operacion contable; no presenta declaraciones ante SUNAT ni sustituye la revision de un contador. Las cuentas, diarios y clasificacion tributaria deben ser aprobados antes de contabilizar.

## Panel contable

Entre como `contabilidad` o `admin` y vaya a **Contabilidad -> Panel Contable**. Desde alli se ven accesos a asientos en borrador, cuentas por cobrar, cuentas por pagar, cajas abiertas y controles tributarios pendientes. El Administrador también tiene los permisos de gerente contable, por lo que puede abrir y operar todas estas opciones.

## Caja chica en soles

1. Configure un diario de tipo **Efectivo** y uno de tipo **Banco** en **Contabilidad -> Configuracion -> Diarios**. Ambos deben tener una cuenta predeterminada; el primero representa el efectivo de caja y el segundo la cuenta bancaria que repone fondos.
2. Abra **Contabilidad -> Contabilidad -> Caja Chica** y pulse **Nuevo**.
3. Indique responsable, diario de efectivo, **Diario bancario de reposicion**, fondo fijo en PEN y fecha. Pulse **Abrir caja**. Se publica el asiento de apertura: Caja chica al Debe y Banco al Haber.
4. En **Movimientos**, agregue factura de proveedor o planilla de movilidad: beneficiario, documento, descripcion, cuenta de gasto e importe.
5. Pulse **Contabilizar**. Se crea un asiento: gasto al Debe y efectivo al Haber.
6. Para reponer los comprobantes ya contabilizados, pulse **Reponer desde banco**. El sistema crea y contabiliza el asiento Banco al Haber / Caja chica al Debe, por los gastos pendientes de reponer. El asiento queda en la pestana **Reposiciones**.
7. Para el arqueo, cuente físicamente el efectivo, registre el resultado en **Efectivo contado**, revise **Diferencia de arqueo** y active **Arqueo fisico confirmado**.
8. Si la diferencia es distinta de cero y fue aprobada, pulse **Ajustar diferencia de arqueo**. Para un faltante el sistema carga la cuenta de faltantes y reduce efectivo; para un sobrante aumenta efectivo y abona la cuenta de sobrantes. Las dos cuentas se eligen al crear la caja y deben ser aprobadas por Contabilidad.
9. Sin movimientos en borrador, pulse **Cerrar caja**. Los ajustes quedan en la pestana **Ajustes de arqueo**.

No se permite otra moneda: una caja chica Pierinelli opera en PEN.

## Detracciones y retenciones

Registre primero la factura normal. Luego vaya a **Contabilidad -> Contabilidad -> Detracciones y Retenciones**, cree el control, vincule comprobante, indique tipo, base, porcentaje, fecha y constancia. Cambie a **Pagado** solo cuando exista el deposito o pago real.

El control es configurable: una tasa no debe suponerse para todos los servicios. El contador debe definir si corresponde detraccion, retencion, porcentaje, umbral y cuenta contable para cada operacion.

## Arqueo diario de cobranzas

1. Vaya a **Contabilidad -> Contabilidad -> Arqueo Diario de Cobranzas** y pulse **Nuevo**.
2. Indique la fecha y el diario de tipo **Efectivo** que recibió los cobros. La moneda se completa desde el diario.
3. Revise **Efectivo esperado** y la pestaña **Cobros incluidos**. Solo se consideran pagos de clientes cobrados, de esa fecha, diario y moneda.
4. Registre el resultado físico en **Efectivo contado**, revise la diferencia y active **Conteo físico confirmado**.
5. Agregue en **Observación / depósito** la constancia o motivo de cualquier diferencia. Pulse **Cerrar arqueo**.

El arqueo no crea un asiento automático por sobrantes o faltantes de cobranza: esa decisión requiere la cuenta y aprobación del contador.

## Comprobantes, dimensiones y cierre de período

- Para crear o ajustar tipos de sustento vaya a **Contabilidad -> Configuración -> Tipos de Comprobantes**. En una factura o movimiento de caja se selecciona el tipo correspondiente; para movilidad use `PM · Planilla de movilidad`.
- En una factura de proveedor, bloque **Control interno**, complete **Clasificación de compra**: Mercaderías, Servicios, Gastos o Activo fijo.
- Para dimensiones de área, subárea, proyecto, sucursal o presupuesto vaya a **Contabilidad -> Configuración -> Dimensiones Analíticas**. Cree un plan por dimensión y sus cuentas; luego use la distribución analítica de cada línea contable.
- Solo Administrador o responsable contable puede ir a **Contabilidad -> Contabilidad -> Cierres Contables**, crear un cierre y pulsar **Aplicar bloqueo**. Antes de hacerlo, confirme conciliaciones, impuestos, caja, provisiones y aprobación del contador. Un cierre evita modificar los períodos hasta la fecha indicada.

## Comprobantes externos y asientos tipo

- Para un comprobante emitido fuera del ERP, abra la factura y vaya al bloque **Control interno**. Registre **Numero externo SUNAT** y el **Tipo de operacion**; no cambie la secuencia interna de un documento contabilizado.
- En la misma factura, abra la pestana **Control tributario** para agregar o revisar detracciones y retenciones vinculadas.
- Para relacionar un cliente con un referidor, vaya a **Ventas -> Pedidos -> Clientes**, abra el cliente y use la pestana **Referidos**.
- Para planilla, provision o depreciacion manual use **Contabilidad -> Contabilidad -> Plantillas de Asientos**, pulse **Generar**, revise el borrador y contabilicelo.
- Los centros de costo usan **Contabilidad analitica**. Existe el plan `Obras / Proyectos`; asigne distribucion analitica a las lineas que correspondan.

## Actualizar tipo de cambio SUNAT

1. Como Administrador, entre a **Contabilidad -> Configuración -> Tipos de Cambio**.
2. Pulse **Actualizar desde SUNAT** y luego **Consultar SUNAT**.
3. El sistema toma la última cotización USD/PEN publicada por SUNAT y crea la tasa con origen **SUNAT**. Si existe una tasa SUNAT del mismo día ingresada manualmente, la conserva.
4. En días sin publicación, o si SUNAT no está disponible, registre la tasa manualmente con **Nuevo**. No se borra ni modifica una tasa existente.
5. Cuando la prueba manual funcione desde Render, Administrador puede activar la tarea diaria en modo desarrollador: **Ajustes -> Técnico -> Automatización -> Acciones planificadas -> SUNAT: actualizar tipo de cambio**. Por defecto está desactivada para que la primera validación sea controlada.

## Importar asientos desde Excel sin errores de estructura

1. Entre a **Contabilidad -> Contabilidad -> Asientos contables**.
2. Pulse **Plantilla Excel** y descargue `plantilla_importacion_asientos.xlsx`.
3. Abra el archivo y lea la hoja **Instrucciones**. En la hoja **Asientos**, elimine las dos filas grises de ejemplo antes de cargar información real.
4. Complete una fila por línea contable: `referencia`, `fecha`, `diario_codigo`, `cuenta_codigo`, `glosa`, `debe`, `haber` y, opcionalmente, `tipo_operacion`.
5. Todas las líneas del mismo asiento deben repetir referencia, fecha y diario. Cada referencia debe cuadrar Debe = Haber.
6. En Odoo pulse **Importar asientos**, adjunte el Excel y pulse **Validar e importar**.
7. Si hay un error, el sistema indica la fila y no crea ningún asiento. Si todo es correcto, abre los asientos creados en estado **Borrador**; revíselos y publíquelos solo cuando estén aprobados.

## Contenido DEMO cargado

La base de prueba contiene una caja chica abierta, una cerrada con reposicion y ajuste de arqueo, movimientos de movilidad/suministros, una provision, una depreciacion, un asiento en borrador, una detraccion pendiente, una retencion pagada y un presupuesto operativo de cuatro lineas. Tambien existe **Arquitecta Referidora Demo**, relacionada con tres clientes de prueba.
