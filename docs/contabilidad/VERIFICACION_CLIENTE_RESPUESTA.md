# Verificacion operativa solicitada por el cliente

> Actualización: para la matriz vigente, incluyendo arqueo diario de cobranzas,
> cierres contables, tipos de comprobante y dimensiones analíticas, consulte
> [IMPLEMENTACION_REQUISITOS_2026-08-12.md](IMPLEMENTACION_REQUISITOS_2026-08-12.md).

Fecha de revisión: 9 de agosto de 2026.

Leyenda: **Operativo** se puede ejecutar hoy con Odoo y los addons instalados. **Parcial** existe una parte útil del flujo, pero falta automatización, una pantalla o una decisión contable. **Pendiente** no debe prometerse como resuelto aún.

## Caja chica (PEN)

| Necesidad | Estado | Dónde se usa / observación |
|---|---|---|
| Apertura de caja chica | **Operativo** | **Contabilidad -> Contabilidad -> Caja Chica -> Nuevo**. Indicar diario de efectivo, diario bancario de reposición, responsable y fondo fijo; pulsar **Abrir caja**. Se publica Banco al Haber / Caja chica al Debe y se enlaza el asiento de apertura. |
| Registrar planilla de movilidad o gasto pagado en efectivo | **Operativo** | Dentro de la caja abierta, pestaña **Movimientos**. Ingresar beneficiario, comprobante o planilla, descripción, cuenta de gasto e importe; pulsar **Contabilizar**. Genera gasto al Debe y efectivo al Haber. |
| Factura de proveedor pagada desde caja | **Parcial** | El gasto y sustento se registran en Caja Chica, pero no se crea ni reconcilia automáticamente una factura de proveedor en CxP. Para control de proveedores completo, primero cree la factura en **Compras -> Facturas** y registre el pago con el diario de efectivo. |
| Reposición bancaria | **Operativo** | En la caja abierta pulse **Reponer desde banco**. Registra Banco al Haber y Caja chica al Debe por los gastos ya contabilizados y deja el comprobante en la pestaña **Reposiciones**. Requiere cuentas predeterminadas en ambos diarios. |
| Arqueo físico, ajuste y cierre | **Operativo** | Registre **Efectivo contado**, revise la **Diferencia de arqueo** y marque **Arqueo físico confirmado**. Si hay diferencia aprobada, pulse **Ajustar diferencia de arqueo**: un faltante carga su cuenta y reduce efectivo; un sobrante aumenta efectivo y abona su cuenta. Configure ambas cuentas al crear la caja. El sistema bloquea el cierre si quedan movimientos en borrador. |

La caja chica se restringe a PEN. El arqueo multimoneda y el cuadre diario de todas las cobranzas de caja son un proceso de tesorería distinto y siguen pendientes.

## Compras

| Necesidad | Estado | Dónde se usa / observación |
|---|---|---|
| Crear proveedor | **Operativo** | **Compras -> Pedidos -> Proveedores -> Nuevo**. Complete razón social, RUC, dirección y condiciones de pago. |
| Orden de compra | **Operativo** | **Compras -> Pedidos -> Solicitudes de presupuesto -> Nuevo**; confirmar para convertirla en orden. |
| Factura de proveedor en PEN o USD | **Operativo** | **Compras -> Facturas -> Nuevo**. Seleccione proveedor, moneda y líneas; confirme/contabilice según la configuración del diario. |
| Registrar pago de proveedor | **Operativo** | Abra la factura publicada y pulse **Registrar pago**. El diario (banco o efectivo), moneda y fecha determinan el cobro contable. |
| Factura con o sin detracción | **Parcial** | La factura normal se registra en Compras. El seguimiento se crea en **Contabilidad -> Contabilidad -> Detracciones y Retenciones**, con factura vinculada, base, porcentaje, fecha y constancia. No calcula ni genera por sí solo la detracción. |
| Pago de detracción | **Parcial** | En el mismo control tributario cambie el estado a pagado solo después del depósito real y guarde la constancia. Falta generar automáticamente el pago/conciliación con Banco de la Nación. |

## Ventas

| Necesidad | Estado | Dónde se usa / observación |
|---|---|---|
| Crear cliente | **Operativo** | **Ventas -> Pedidos -> Clientes -> Nuevo**. |
| Referidor relacionado a cliente | **Parcial** | El modelo ya tiene el vínculo técnico de referidor, pero aún no se expone en la ficha de cliente. Falta una extensión pequeña de la vista para que el usuario lo mantenga. |
| Cotización y orden de venta en USD | **Operativo** | **Ventas -> Pedidos -> Cotizaciones -> Nuevo**. Seleccione USD antes de añadir líneas; pulse **Enviar por correo** si corresponde y **Confirmar** para crear la orden. |
| Entrega antes de facturar | **Operativo** | Desde la orden confirmada pulse **Entrega** y valide; luego use **Crear factura** en la orden. La política de facturación del producto determina si se factura por cantidades entregadas. |
| Factura contado o crédito en USD | **Operativo** | En la orden pulse **Crear factura**, publique la factura y use **Registrar pago** para contado. Para crédito, deje la factura abierta hasta recibir el pago. |
| Copiar número emitido externamente por SUNAT | **Parcial** | El campo técnico **Número externo SUNAT** existe en el asiento, pero todavía no está visible en la factura. No se debe editar la secuencia interna de una factura publicada; falta exponer ese campo y definir el procedimiento de control. |
| Factura de servicio con detracción y documento en PEN | **Parcial** | Puede emitir la factura y crear el control de detracción manual. Falta una automatización que cree el documento/registro PEN de detracción a partir de la factura de servicio. |
| Anticipo USD y aplicación parcial o total | **Operativo en estándar Odoo, requiere configuración** | Cree una factura de anticipo desde la orden usando **Crear factura -> Anticipo** y registre su pago. La aplicación y conciliación posterior depende de las cuentas de anticipos y la configuración de contabilidad. Debe probarse con el plan contable definitivo antes de operar. |
| Pago USD exacto, por transferencia o efectivo | **Operativo** | En la factura publicada pulse **Registrar pago** y seleccione diario de banco/efectivo USD. |
| Sobrepago USD y saldo a favor | **Operativo en estándar Odoo, requiere prueba** | Registre el importe recibido; el crédito queda en la cuenta del cliente para conciliarlo contra una factura posterior. Confirmar el comportamiento con los diarios y cuentas reales antes de producción. |
| Pago en PEN de factura USD y diferencia de cambio | **Parcial** | Odoo maneja multimoneda y puede reconocer diferencias al conciliar, pero la tasa propia y las cuentas de ganancia/pérdida deben configurarse y validarse con casos reales. No hay una regla personalizada de tipo de cambio por pago. |
| Retención SUNAT 3 % | **Parcial** | Se controla desde **Detracciones y Retenciones** como registro manual. Falta cálculo, validación de umbral, asiento y pago automatizados. |
| Detracción SUNAT | **Parcial** | El control manual está disponible. La tasa debe ser definida por operación; no se debe asumir 4 % para todos los servicios. Falta integración de pago/constancia y automatización contable. |
| Nota de crédito USD y aplicación | **Operativo en estándar Odoo** | Abra la factura publicada y use **Nota de crédito**; publique y concilie contra el documento original. Probar con USD y el diario definitivo. |
| Factura a título gratuito | **Parcial** | Se puede crear una factura con líneas sin valor, pero la emisión tributaria válida exige configuración de comprobante y, si se integra SUNAT, reglas del proveedor electrónico. |
| Anular factura o nota de crédito | **Operativo con control contable** | Sobre un documento publicado use **Nota de crédito** (reversión); los borradores se pueden cancelar. No se borra un comprobante contable ya publicado. |
| Cuadre diario de efectivo PEN y USD | **Pendiente** | Caja Chica cubre arqueo PEN. Falta un módulo/pantalla de tesorería que consolide cobros por moneda, efectivo esperado, efectivo contado, diferencias y depósitos. |

## Importación e inventario

| Necesidad | Estado | Dónde se usa / observación |
|---|---|---|
| Orden de compra de importación en USD | **Operativo** | **Compras -> Pedidos -> Solicitudes de presupuesto -> Nuevo**, con moneda USD; confirmar. |
| Factura de importación | **Operativo** | **Compras -> Facturas -> Nuevo**, seleccione proveedor, USD y la orden/recepción relacionada. |
| Ingreso de material | **Operativo** | Desde la orden, **Recepciones**; valide la recepción. Para planchas use el flujo documentado en `docs/operacion/GUIA_OPERATIVA.md`. |
| Costos adicionales / costeo | **Operativo con configuración** | **Inventario -> Operaciones -> Costos en destino**. Cree el costo, asocie recepciones y costos (flete, seguro, aduana), compute y valide. Requiere productos configurados con valoración/coste compatible. |
| Kardex final en PEN | **Operativo con configuración y prueba** | La compañía opera en PEN y la compra puede estar en USD. El resultado correcto depende de tipo de cambio, valoración automática y costos en destino; debe validarse en una importación de prueba antes de cierre real. |

## Contabilidad, presupuestos y reportes ya disponibles

| Función | Acceso |
|---|---|
| Centro Financiero | **Contabilidad -> Panel Contable**. Atajos de facturación/cobros, compras/pagos, asientos, caja, tributos, asientos tipo y presupuestos. |
| Asientos manuales | **Contabilidad -> Contabilidad -> Asientos contables -> Nuevo**. |
| Asientos tipo para provisiones, planilla o depreciación manual | **Contabilidad -> Contabilidad -> Plantillas de Asientos**. Generar, revisar el borrador y publicar. No existe depreciación automática de activos fijos. |
| Presupuesto por cuenta y periodo | **Contabilidad -> Presupuestos**. Crear, agregar cuentas e importes, aprobar y revisar ejecutado frente a asientos publicados. |
| Centro de costo | **Contabilidad -> Configuración -> Contabilidad analítica**. Asigne distribución analítica en líneas contables. La comparación del presupuesto por centro de costo requiere validación adicional. |
| Reportes financieros | **Contabilidad -> Reportes**: balance, ganancias/pérdidas, flujo de efectivo, libro diario, mayor, balance de comprobación, antigüedad CxC/CxP, IGV y ratios, según permisos. |

## Integraciones que no están incluidas todavía

No existe una conexión real con SUNAT, un OSE/PSE ni el Banco de la Nación. Por tanto, el ERP **no debe presentarse como emisor electrónico, validador de CPE, generador de PLE/SIRE ni pagador automático de detracciones**. Para eso se necesita contratar/seleccionar un proveedor, obtener credenciales/certificados, definir contingencia y desarrollar o instalar el conector compatible con la versión de Odoo.

Tampoco hay API bancaria para importar extractos, ejecutar transferencias o confirmar depósitos. Los pagos y constancias se registran manualmente hasta que se integre el banco.

Las detracciones son un sistema regulado de SUNAT y las retenciones tienen condiciones y tasas que deben verificarse por comprobante; por ello el módulo deja porcentaje, base y constancia bajo control del contador, en vez de aplicar una tasa universal. Consulte las referencias oficiales de [detracciones](https://emprender.sunat.gob.pe/principales-impuestos/impuesto-general-las-ventas-igv/sistema-detracciones-igv) y [retenciones del IGV](https://emprender.sunat.gob.pe/principales-impuestos/impuesto-general-las-ventas-igv/regimen-retencion-igv) antes de parametrizar.

## Precondiciones antes de producción

1. Contador: aprobar plan de cuentas, cuentas de caja/bancos, anticipos, diferencia de cambio, retenciones, detracciones y ajustes de arqueo.
2. Administrador: configurar diarios PEN/USD, tasas de cambio, métodos de pago, impuestos, condiciones de pago, permisos y secuencias.
3. Operación: ejecutar una prueba completa por cada caso sensible: anticipo USD, pago PEN de factura USD, sobrepago, nota de crédito, importación con costo en destino, detracción y cierre de caja.
4. Dirección: decidir si se implementan SUNAT/OSE-PSE, PLE/SIRE, Banco de la Nación/API bancaria y el cuadre diario multimoneda; cada uno es un proyecto de integración adicional.
