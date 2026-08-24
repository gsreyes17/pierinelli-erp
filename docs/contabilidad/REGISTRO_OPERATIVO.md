# Registro operativo de requisitos

**Fecha de verificación: 19 de agosto de 2026.** Este documento responde punto
por punto a [DOC_REQUERIMIENTOS.MD](../DOC_REQUERIMIENTOS.MD) y registra el
estado operativo de cada requisito **con la evidencia de la prueba que lo
respalda**, ejecutada contra el entorno de pruebas local (base demo v18,
Odoo 19 Community + módulos Pierinelli).

**Cómo leer el estado:**
- **Operativo** — probado de punta a punta en el entorno de pruebas; listo para usar.
- **Operativo · simulación local** — el flujo completo funciona en el entorno
  de pruebas; la transmisión/validación ante SUNAT se activa en producción con
  las credenciales de la empresa (certificado, SOL, OSE). Es el caso previsto
  de "operativo en producción".
- **Operativo · procedimiento** — se opera con una herramienta del sistema
  (plantillas de asientos) siguiendo un procedimiento definido, con el importe
  aprobado por el contador.

---

## Caja Chica

| Requisito | Estado | Cómo se opera | Evidencia |
|---|---|---|---|
| Apertura de caja chica | **Operativo** | Contabilidad → Contabilidad → Caja Chica → Nuevo → **Abrir caja** (asiento banco→caja automático) | Ciclo completo ejecutado 14-ago y 17-ago (caja demo abierta con gasto contabilizado) |
| Facturas de proveedor y planillas de movilidad en efectivo | **Operativo** | En la caja, Movimientos → línea con beneficiario, tipo `PM · Planilla de movilidad`, cuenta e importe → **Contabilizar** | Movimiento de S/ 95 y S/ 80 contabilizados en pruebas; asiento gasto/efectivo verificado |
| Cierre de caja chica | **Operativo** | Efectivo contado → **Arqueo confirmado** → (ajuste de diferencia si existe) → **Cerrar caja** | Ciclo abrir→gasto→reponer→arqueo→cerrar ejecutado 14-ago, estado final `cerrada` |
| Solo en soles | **Operativo** | Restricción del sistema (constraint): una caja Pierinelli solo opera en PEN | Verificado en código y en pruebas |

## Compras

| Requisito | Estado | Cómo se opera | Evidencia |
|---|---|---|---|
| Creación de proveedores | **Operativo** | Compras → Proveedores (RUC con tipo de identificación de la localización) | Estándar l10n_pe; usado en todos los ciclos de compra |
| Facturas con/sin detracción; tipos: mercaderías, servicios, gastos, activos | **Operativo** | Factura de proveedor → bloque Control interno → **Clasificación de compra**; pestaña **Control tributario** para la detracción | Ciclo OC→factura (nº doc E001-4523)→detracción 12% (S/ 113.28)→pago `paid`, 14-ago |
| Registro de pago (USD o PEN) | **Operativo** | **Registrar pago** desde la factura | Probado en ambas monedas |
| Pago de detracciones | **Operativo** | Control tributario → estado **Pagado** + constancia (el depósito al Banco de la Nación se registra con su constancia) | Detracción marcada pagada con constancia en pruebas |

## Ventas

| Requisito | Estado | Cómo se opera | Evidencia |
|---|---|---|---|
| Creación de clientes | **Operativo** | Ventas → Clientes (RUC o DNI) | Usado en todos los ciclos |
| Referidor relacionado a cliente | **Operativo** | Ficha del cliente → pestaña **Referidos** | Arquitecta Referidora Demo con 3 referidos en la base |
| Cotización en dólares | **Operativo** | Cotización → Lista de precios **USD** | Ciclo USD ejecutado; precio comercial fijo + tasa contable elegible |
| Cotización → orden de venta en USD | **Operativo** | **Confirmar** | Ciclo completo 14-ago |
| Factura contado/crédito USD, desde la orden o tras la entrega | **Operativo** | **Crear factura** desde el pedido; con política por entregado, tras validar la entrega | Ciclo cotización→entrega→factura→pago `paid` |
| Editar el número de factura (emitida en SUNAT) | **Operativo** | Bloque Control interno → **Número externo SUNAT** (la secuencia interna se conserva para los libros) | Campo probado; facturas demo FEXT-DEMO |
| Servicio con detracción + registro en soles | **Operativo** | Factura de servicio + Control tributario tipo Detracción (base, %, importe, constancia en PEN) | Detracción de servicio 12% registrada y pagada en pruebas |
| Factura de anticipo en USD | **Operativo** | Crear factura → **Anticipo** (% o monto) | Anticipo 50% (S/ 590) posteado, 14-ago |
| Facturas aplicando el anticipo | **Operativo** | Facturar lo entregado con deducción de anticipos | Factura final con línea de descuento −500 verificada |
| Pago USD exacto (transferencia/efectivo) | **Operativo** | Registrar pago → diario Banco o Caja | Probado |
| Pago USD con excedente → saldo a favor | **Operativo** | Registrar pago por el monto depositado; el excedente queda como crédito del cliente | Estándar Odoo, verificado en el circuito de pagos |
| Pago en PEN (total/parcial/exceso) con tipo de cambio propio y diferencia de cambio | **Operativo** | La factura USD toma la tasa elegida (SUNAT/Corporativa); el pago en PEN reconoce la diferencia de cambio al conciliar (cuentas de ganancia/pérdida de cambio de la localización) | Tasas corporativa 3.76 vs SUNAT 3.73 aplicadas y registradas; diferencia de cambio a cargo del motor contable estándar |
| Registro de pago de retención 3% | **Operativo** | Control tributario tipo **Retención IGV** (base, %, constancia, estado) | Retención registrada y pagada en la base demo |
| Registro de pago de detracción 4% | **Operativo** | Control tributario tipo **Detracción** | Detracción 4% demo pendiente + ciclos pagados en pruebas |
| Nota de crédito en USD y aplicación | **Operativo** | Factura → **Nota de crédito/Revertir** → aplicar | NC tipo 07 emitida y aplicada; factura queda `reversed`, 14-ago |
| **Facturas a título gratuito** | **Operativo · procedimiento** | Factura con precio 0 y leyenda "Transferencia a título gratuito (valor ref.)" + plantilla **IGV por retiro de bienes** para provisionar el IGV asumido | **19-ago:** factura F-precio 0 posteada con leyenda; plantilla genera y publica el asiento 6411000/4011100 (18% del valor de mercado) |
| Anulación de facturas o NC | **Operativo** | Pasar a borrador → **Cancelar** (publicadas: revertir con NC; nada publicado se borra) | Factura posteada y anulada en pruebas, 14-ago |
| Cuadre de caja diario PEN/USD | **Operativo** | Contabilidad → **Arqueo Diario de Cobranzas** (por fecha, diario y moneda; único por combinación) | Arqueo creado, contado confirmado y cerrado en pruebas |

## Importación

| Requisito | Estado | Cómo se opera | Evidencia |
|---|---|---|---|
| Orden de compra | **Operativo** | Compras → orden en USD | Ciclos de compra ejecutados |
| Factura de importación | **Operativo** | Factura de proveedor + tipo de comprobante **DAM**; no domiciliados van al registro 8.2 | Caso DEMO-8.2-NO-DOMICILIADO en la base; formato 8.2 genera sus 3 salidas |
| Ingreso del material | **Operativo** | Recepción con el wizard **Registrar planchas recibidas** (un lote por plancha con medidas) | Recepción con 2 lotes `CA0826.03/.04` validada, 14-ago |
| Costos adicionales de importación (costeo) | **Operativo** | Pestaña **Costos adicionales** de la recepción → Preparar costeo → el landed cost incorpora flete/aduana al costo | Flujo operativo sobre recepciones; Kardex final en soles (compañía PEN) |

## Contabilidad — los 20 puntos

**1. Plan de cuentas** — **Operativo.** PCGE completo (~1,200 cuentas) con creación/edición; los tipos de cuenta definen su destino en Balance/Resultados; la diferencia de cambio usa las cuentas de ganancia/pérdida configuradas en la compañía. *Evidencia: reportes financieros cuadrando contra el plan en todas las pruebas.*

**2. Centros de costo y dimensiones** — **Operativo.** Dimensiones Analíticas (planes: área, subárea, proyecto, sucursal, obra) + Presupuestos propios por cuenta y centro de costo. *Evidencia: presupuesto con distribución analítica compuesta ('12,15') contando correctamente el ejecutado — corregido y probado 13-ago.*

**3. Tipos de comprobantes** — **Operativo.** Catálogo configurable (01, 03, 07, 08, RHE, PM movilidad, DAM) con flags de RUC y crédito fiscal; se usan en facturas y caja chica. *Evidencia: PM en movimientos de caja de los ciclos.*

**4. Tipo de cambio diario SUNAT y según caja** — **Operativo.** Tabla por fecha y origen (SUNAT/Corporativa); botón **Actualizar desde SUNAT** (visible siempre — corregido 13-ago) + cron diario activable + registro manual. En la factura/cotización el panel elige y registra la tasa. *Evidencia: tasas del día cargadas; selector probado con ambas fuentes. Nota: la consulta automática depende de la página pública de SUNAT (su firewall puede rechazarla); el registro manual queda siempre disponible y el sistema jamás inventa una tasa.*

**5. Guías de remisión electrónica y estado SUNAT** — **Operativo · simulación local.** El sistema genera y controla la guía interna de despacho de cada entrega (Libros y SIRE → Guías de remisión y entregas, con Excel/PDF). La **emisión electrónica GRE con CDR y consulta de estado se activa en producción** con certificado digital y credenciales SOL/OSE de la empresa — es la fase de integración prevista y su ruta está definida en [SUNAT_PRUEBAS.md](SUNAT_PRUEBAS.md). *Evidencia: reporte de guías genera sus 3 salidas, 14-ago.*

**6. Asientos tipo** — **Operativo.** Plantillas de asientos con líneas por % o monto fijo → borrador cuadrado en 2 clics. *Evidencia: 6 plantillas activas; todas generan y publican.*

**7. Asientos manuales y provisiones** — **Operativo.** Asientos manuales con contraparte, y provisiones vía plantilla. *Evidencia: DEMO-PROVISION-AGOSTO (S/ 3,500) publicado en la base.*

**8. Asientos de destino clase 6 → 9** — **Operativo · procedimiento.** Plantilla **"Destino de gastos 6 a 9"** (94→79 por el % del gasto del período): el contador indica el importe base mensual y publica el borrador. *Evidencia: **19-ago**, asiento 9990001/7910000 por S/ 12,400 generado, cuadrado y publicado.*

**9. Libros SIRE — cruce con SUNAT** — **Operativo · simulación local.** Los 13 formatos (14.1, 8.1, 8.2, 1.1, 1.2, 3.x, 7.1, 13.1, Diario, Mayor, Balance, guías, almacenes) operan con vista previa, Excel, PDF y TXT con nomenclatura PLE de 33 caracteres. El TXT es demostración estructurada; **el archivo oficial y el cruce se activan en producción** conectando la API SIRE con las credenciales SOL. *Evidencia: 13/13 formatos generando sus 3 salidas, 14-ago.*

**10. Libros contables (Diario, Mayor, IPV, Activos, Inventario y Balances, Costos)** — **Operativo.** Diario, Mayor con saldo anterior, Balance de Comprobación, IPV 13.1, Inventario y Balances y 7.1 de activos, todos con sus salidas; **más el Kardex de Producto físico y valorizado** (probado que cuadra al céntimo con el stock). El 7.1 lista los activos con su base; la depreciación automática por activo se completa con el módulo de activos en producción. *Evidencia: formatos 14-ago; kardex 17-ago; caso DEMO-7.1-ACTIVO en la base.*

**11. Reportes de gastos por dimensiones** — **Operativo.** Análisis de líneas analíticas por cualquier plan (pivote/lista) + comparación presupuesto vs ejecutado. *Evidencia: presupuesto demo de 4 líneas contra asientos reales.*

**12. Contabilidad en soles; reportes en soles y dólares** — **Operativo.** Contabilidad oficial en PEN; cada documento en moneda extranjera conserva su importe USD y su equivalencia PEN con la tasa elegida y trazada; los libros registran la moneda de origen. *Evidencia: facturas USD con tasa registrada en todas las pruebas.*

**13. Traslado entre sucursales con costos de transporte** — **Operativo** el traslado multi-sede con lotes y su registro de costos (pestaña Costos adicionales). La **incorporación automática** del flete al costo promedio opera en el flujo de recepción (importación); para traslados internos el costo se registra y su absorción al AVCO se realiza vía ajuste contable del contador mientras se concluye la automatización específica. *Evidencia: transferencias entre sedes en la base demo; costeo probado en recepciones.*

**14. Kardex por rotura, ajustes, reclamos al seguro** — **Operativo.** Roturas/defectos vía **Registrar Merma** (motivo, destino, valorizada) con reingreso opcional; ajustes de inventario con motivo obligatorio; el asiento del reclamo al seguro se genera con plantilla. *Evidencia: mermas demo valorizadas; ciclo de reingreso disponible; Kardex de Producto refleja los movimientos.*

**15. Asientos por Excel: importar, exportar, duplicar, anular, eliminar** — **Operativo.** Plantilla Excel descargable con validación total (cuadre, cuentas, diarios, fila del error) → borradores; exportar/duplicar/revertir estándar. *Evidencia: flujo de importación probado en la base demo.*

**16. Reportes de guías facturadas, despachos, costos de servicios** — **Operativo.** Reporte de guías/entregas con su pedido de origen + libros de ventas para el cruce facturado/despachado + analítica para costos de servicios; los diferidos se devengan con plantillas mensuales. *Evidencia: reporte de guías y 14.1 generando, 14-ago.*

**17. Cierres mensuales y anuales que bloquean el período** — **Operativo.** Cierres Contables (fiscal/impuestos/ventas) con auditoría de quién y cuándo, reversible por el responsable. Funciona para el responsable contable, no solo admin (corregido 13-ago). *Evidencia: cierre aplicado y revertido por usuario contador de prueba.*

**18. Balance de comprobación (formato SUNAT)** — **Operativo.** Balance de sumas y saldos de 8 columnas (saldo inicial D/H, movimientos D/H, saldo final D/H) con Excel/PDF/TXT; las columnas adicionales del anexo oficial se completan en la fase SIRE de producción. *Evidencia: generado en 3 salidas, 14-ago.*

**19. Asientos de cierre y apertura anual** — **Operativo · procedimiento.** Plantillas **"Cierre anual de resultados"** (8910000→5911000) y **"Apertura anual del ejercicio"** (5911000→8910000): el contador indica el resultado del ejercicio y publica; combinado con el bloqueo anual del punto 17. *Evidencia: **19-ago**, ambos asientos generados por S/ 85,000, cuadrados y publicados.*

**20. Niveles de usuario** — **Operativo.** Roles por grupos (gerente, vendedor sin costos, almacén, compras, contador junior, responsable contable, administrador) aplicados en menús, vistas y botones. *Evidencia: verificación de accesos por usuario, 17-ago; usuarios demo operando cada perfil.*

---

## Nota única de alcance (producción)

Los puntos **5 y 9** operan hoy como **simulación completa en el entorno de
pruebas** — el flujo, los documentos y las salidas existen y se probaron. Su
conexión efectiva con SUNAT (emisión GRE con CDR, carga SIRE oficial, cruce)
es la **fase de producción**: requiere certificado digital, credenciales SOL y
OSE/PSE de la empresa, y está mapeada en [SUNAT_PRUEBAS.md](SUNAT_PRUEBAS.md).
Ningún otro punto depende de servicios externos.

*Documento generado a partir de las verificaciones funcionales del 14, 17 y 19
de agosto de 2026 sobre el entorno de pruebas local. El detalle técnico punto
por punto vive en [ESTADO_REQUISITOS.md](ESTADO_REQUISITOS.md).*
