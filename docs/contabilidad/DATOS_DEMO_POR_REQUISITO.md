# Datos demo por requisito: qué abrir y qué llenar

**Actualizado: 21 de agosto de 2026.** Para cada punto de
[DOC_REQUERIMIENTOS.MD](../DOC_REQUERIMIENTOS.MD) tienes aquí **el ejemplo con
nombre que ya está cargado en la base** (ábrelo y muéstralo) y, cuando vale la
pena hacerlo en vivo, **exactamente qué llenar**. Todo lo citado existe hoy en
la base de pruebas — nada hay que preparar sobre la marcha.

> Truco general para encontrar cualquier ejemplo: los registros de muestra
> llevan **"DEMO"** en su referencia o notas. En cualquier lista, busca `DEMO`.

---

## Caja Chica

| Qué mostrar | Ejemplo listo | En vivo (si quieres) |
|---|---|---|
| Apertura | **Caja Chica Demo - Abierta** (estado Abierta) en Contabilidad → Contabilidad → Caja Chica | Nuevo → responsable, diario Efectivo, diario banco, fondo S/ 1,500 → **Abrir caja** → muestra el asiento banco→caja |
| Gasto en efectivo (movilidad) | La caja abierta ya tiene un gasto contabilizado (MOV-DEMO-101, S/ 95) | Movimientos → Agregar línea: beneficiario, tipo `PM · Planilla de movilidad`, cuenta 659*, S/ 35 → **Contabilizar** → abre el asiento |
| Cierre con arqueo | Hay una caja **cerrada** con reposición y ajuste de arqueo en el historial | En la abierta: Efectivo contado = saldo teórico → Arqueo confirmado → **Cerrar caja** |
| Solo soles | — | Intenta elegir un diario USD: el sistema lo rechaza |

## Compras

| Qué mostrar | Ejemplo listo | En vivo |
|---|---|---|
| Factura proveedor + clasificación | Facturas de proveedor demo con **Clasificación de compra** en el bloque Control interno | En una factura de proveedor: Clasificación = Mercaderías / Servicios / Gastos / Activo fijo |
| Detracción de compra | **DEMO-DETRACCION-001** (pendiente, 4%, con constancia) — Contabilidad → Contabilidad → Detracciones y Retenciones | En una factura → pestaña Control tributario → línea Detracción: base, %, el importe se calcula |
| Pago de detracción | **DEMO-RETENCION-001** ya figura **Pagada** con constancia | Cambia estado a Pagado + número de constancia |

## Ventas

| Qué mostrar | Ejemplo listo | En vivo |
|---|---|---|
| Referidor | **Arquitecta Referidora Demo** → ficha → pestaña Referidos (3 clientes) | En cualquier cliente: pestaña Referidos → asignar referidor |
| Cotización USD + tasa | Cotizaciones con lista **USD**; factura **F 00000028** posteada con origen de tasa registrado | Cotización → Lista de precios USD → panel dorado **Tipo de cambio** → Cambiar → SUNAT venta o Corporativa (tasas de HOY ya cargadas: SUNAT 3.749 / Corp. 3.778) |
| Factura desde orden o entrega | Ciclos completos en Ventas (S00146 y siguientes) | Pedido confirmado → Crear factura; o valida la entrega primero y factura lo entregado |
| Nº de factura externo (SUNAT) | Facturas con **FEXT-DEMO-001/002** en Control interno | Campo **Número externo SUNAT** en cualquier factura |
| Anticipo aplicado | Pedido **S00049** (Madre Selva): anticipo 50% y factura final que lo descuenta | Crear factura → Anticipo (porcentaje 50) → luego factura final: aparece la línea negativa |
| Pago exacto / con excedente | Pago **PBNK1/2026/00015**: factura de S/ 590 pagada con S/ 690 → **S/ 100 de saldo a favor** del cliente | Registrar pago → edita el importe a uno mayor → el excedente queda como crédito pendiente del cliente |
| Retención 3% / Detracción 4% | DEMO-RETENCION-001 (pagada) y DEMO-DETRACCION-001 (pendiente) | Control tributario de la factura correspondiente |
| Nota de crédito aplicada | **F 00000033** (NC) aplicada a **F 00000032** — la factura queda "Revertido" | Factura publicada → Nota de crédito → motivo → publicar → conciliar |
| **Factura a título gratuito** | **F 00000031**: total S/ 0.00, leyenda "TRANSFERENCIA A TÍTULO GRATUITO (valor ref. S/ 1,500)" + borrador **DEMO-IGV-RETIRO-01** (asiento del IGV 18% asumido, 6411000→4011100) | Factura precio 0 con la leyenda; luego Plantillas de Asientos → "IGV por retiro de bienes" → base = valor de mercado → Generar |
| Anulación | Historial de facturas canceladas | Factura → Restablecer a borrador → Cancelar |
| Cuadre de caja diario | **Arqueo de hoy ABIERTO** (Contabilidad → Arqueo Diario de Cobranzas): esperado **S/ 330.40** por el cobro en efectivo DEMO-COBRO-EFECTIVO | Efectivo contado = 330.40 → Conteo confirmado → **Cerrar arqueo** (¡este déjalo para cerrarlo en vivo, luce mucho!) |

## Importación

| Qué mostrar | Ejemplo listo | En vivo |
|---|---|---|
| Factura de importación / no domiciliado | **C INV-IT-2026-0184** (caso 8.2 no domiciliado, tipo DAM) | Libros y SIRE → Registro 8.2 → Cargar vista previa: ahí aparece |
| Ingreso del material | Recepciones con lotes de plancha (medidas por unidad) | Recepción → **Registrar planchas recibidas** → cantidad y medidas |
| Costeo | Recepciones con pestaña **Costos adicionales** | Agregar flete/aduana → Preparar costeo |

## Los 20 puntos de Contabilidad

| # | Ejemplo listo en la base | En vivo |
|---|---|---|
| 1. Plan de cuentas | PCGE completo (Contabilidad → Configuración → Plan contable) | Crea la cuenta 6591001 "Gastos varios demo" |
| 2. Dimensiones | Plan **Obras/Proyectos** con **Condominio Trujillo** etc.; **Presupuesto Operativo - DEMO** (4 líneas, ejecutado real) | Dimensiones Analíticas → nuevo plan "Sucursal" |
| 3. Tipos de comprobante | Catálogo 01/03/07/08/RHE/**PM movilidad**/DAM en Configuración → Tipos de Comprobantes | — |
| 4. Tipo de cambio diario | Tabla con **las tasas de HOY** (SUNAT 3.749 / Corporativa 3.778) + historial | Botón **Actualizar desde SUNAT** (si su web rechaza: **Nuevo** manual, 30 seg) |
| 5. Guías | Libros y SIRE → **Guías de remisión y entregas** → Cargar vista previa | Aclara: guía interna; la GRE electrónica es fase de producción |
| 6. Asientos tipo | **6 plantillas** en Plantillas de Asientos (planilla, depreciación, cierre, apertura, destino 6→9, IGV retiro) | Cualquiera → **Generar** → borrador cuadrado |
| 7. Provisiones | **MISCE/2026/08/0001** (DEMO-PROVISION-AGOSTO, S/ 3,500 publicado) | Plantilla "Provisión" → Generar → publicar |
| 8. Destino 6→9 | Borrador **DEMO-DESTINO-69-AGOSTO** (S/ 12,400, cuentas 9990001/7910000) listo en Asientos contables | Ábrelo → revisa → **Publicar** en vivo |
| 9. Libros SIRE | Los 13 formatos con Excel/PDF/TXT (nomenclatura PLE) | 14.1 y 8.1 → Cargar vista previa → Excel |
| 10. Libros contables | Diario, Mayor, Balance, IPV 13.1, Inv. y Balances, 7.1 (caso **F F009-00000471**) + **Kardex de Producto** | Botón **Kardex** en la ficha de cualquier piedra |
| 11. Gastos por dimensión | Presupuesto DEMO compara presupuestado vs ejecutado real | Análisis analítico → agrupar por plan |
| 12. PEN + USD | Facturas USD con equivalencia PEN trazada (F 00000028) | El asiento muestra ambos importes |
| 13. Traslado con costos | **UG/INT/00003** (traslado entre sedes) con **S/ 1,000 en costos registrados** (flete + seguridad DEMO) | Muestra la pestaña Costos adicionales del traslado |
| 14. **Kardex por rotura** / ajustes / seguro | **Merma BM0826.01.02 (0.75 m²)** motivo **Rotura**, valorizada — Inventario → Planchas → Mermas (nota DEMO-ROTURA-01). En el **Kardex** de ese producto se ve la salida | Registrar Merma → plancha, m², motivo Rotura → el reclamo al seguro se asienta con plantilla |
| 15. Excel de asientos | Plantilla descargable + **DEMO-ASIENTO-BORRADOR** (S/ 420) esperando revisión | Importar asientos → adjunta el Excel → borradores |
| 16. Guías facturadas / despachos | Reporte de guías (muestra el pedido de origen) + libro 14.1 para el cruce | — |
| 17. Cierres | Contabilidad → Cierres Contables (histórico con quién/cuándo) | Nuevo cierre fiscal al 31-jul → **Aplicar bloqueo** → intenta editar julio: bloqueado → **Revertir** |
| 18. Balance de comprobación | 8 columnas con Excel/PDF/TXT en Libros y SIRE | Cargar vista previa del período |
| 19. **Cierre y apertura anual** | Borradores **DEMO-CIERRE-ANUAL-2026** y **DEMO-APERTURA-2027** (S/ 85,000, cuentas 8910000↔5911000) en Asientos contables | Ábrelos → revisa el cuadre → publica el de cierre en vivo |
| 20. Niveles de usuario | Usuarios `gerente`/`vendedor`/`almacen`/`contabilidad` (clave `pierinelli`) | Entra como `vendedor`: sin costos ni contabilidad |

## Bonus (fuera del documento del cliente, pero lucen)

- **Orden de corte multi-plancha OP-00007** (nota DEMO-OC-MULTI): dos planchas
  en una orden, cortes propios, retornos **BM0826.02.01** y **BM0826.03.01**, y
  **una merma asumida por el cliente y otra del negocio**. Imprime la OP: el
  PDF lista cada plancha con su tabla.
- **Plancha en losas CA0126.01**: filtro "Losas pre-cortadas" y venta por piezas.
- **Panorama de Almacenes** al abrir Inventario.

---

*Todo lo citado fue creado o verificado contra la base el 19–21 de agosto de
2026. Si un número de documento difiere (los correlativos avanzan), búscalo por
su marca `DEMO`. Guion de presentación: [DEMO_CONTABLE.md](DEMO_CONTABLE.md) ·
chuleta de botones: [../operacion/CHULETA_DEMO.md](../operacion/CHULETA_DEMO.md).*
