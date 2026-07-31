# Avances del desarrollo — Plan Inventario V2

> Registro de lo implementado sobre [PLAN_INVENTARIO_V2.md](PLAN_INVENTARIO_V2.md).
> Se actualiza al cierre de cada bloque de trabajo.

---

## Sesión 1 — 30 jul 2026 · Fases 0, 1 y 2 completas

### Qué quedó funcionando

**Fase 1 — Cimientos** ✅

| Tarea | Estado | Detalle |
|---|---|---|
| Costo promedio (AVCO) | ✅ Verificado | Las 8 subfamilias + 2 familias en `average`. Probado en vivo: Sparkle Blue costó 426.00, se compró a 390.50 → promedio pasó a 418.08. El "100+120→110" del cliente funciona. |
| Valorización en tiempo real | ✅ Verificado | Compras debitan Mercaderías (2011100); ventas la acreditan. Cta 201 = S/ 791,192.99 = valor físico exacto del inventario. Balance cuadra (descuadre 0.00). |
| Familia / Subfamilia | ✅ | `Naturales` (Mármol, Granito, Cuarcita, Ónix) y `Artificiales` (Sinterizada, Porcelánico, Cuarzo, Solid Surface). |
| Natural / Artificial en producto | ✅ | Campo `tipo_material`: decide si la foto individual es obligatoria. |
| Fix "subir factura" | ✅ | `account_edi` instalado (estaba desinstalado, causaba parte del problema). |

**Fase 2 — La plancha como entidad** ✅ (módulo nuevo `pierinelli_planchas`)

| Tarea | Estado | Detalle |
|---|---|---|
| Ficha de plancha | ✅ | `stock.lot` extendido: largo, alto, espesor, m² bruto/neto, condición, estado, ubicación referencial, ref. importación, observaciones, cliente, asesor, reserva, comprobante, **foto** (image.mixin). |
| Código interno automático | ✅ Verificado | Iniciales + mes/año + correlativo: "Pietra Grey" → `PG0726.01`. Retorno de corte: `PG0726.01.01` (método `siguiente_codigo_corte`). Prefijo editable en el producto. |
| Estado calculado | ✅ | Disponible / Reservada / Vendida, desde el stock físico y la reserva vigente. |
| Alta masiva | ✅ Verificado | Wizard "Alta de Planchas": producto + cantidad + medidas → genera códigos y stock de golpe. Con vista previa de códigos. |
| m² almacenado | ✅ | `m2_disponible` es campo almacenado (los listados grandes no se degradan). |
| Vista de Operaciones | ✅ | Tabla completa (~24 columnas, con columnas opcionales) en `Inventario → Planchas → Tabla de Operaciones`. |
| Marcado Hueso | ✅ Verificado | Cron diario: >365 días en almacén → condición Hueso + mensaje en la plancha. 32 planchas marcadas en la demo. |

**Adelantos de Fases 3 y 4** (salieron gratis con el modelo)

| Tarea | Estado | Detalle |
|---|---|---|
| Vista Comercial (F3) | ✅ | `Ventas → Planchas`: sin costos, editable en reserva/venta/observaciones. ACL: vendedor lee y escribe planchas, no crea ni borra. |
| Reserva 7 días + liberación (F3) | ✅ Verificado | Botón "Reservar (7 días)" (exige cliente, asigna asesor y vencimiento) + cron diario que libera vencidas avisando en el chatter. No libera si ya hay comprobante. |
| Alerta retazo < 0.5 m (F4 §7.1) | ✅ | Al crear un retorno de corte con una dimensión < 0.5 m, la plancha recibe el aviso de considerar merma/liquidación. |

**Fase 0 — Datos reconstruidos** ✅

- BD recreada desde cero. Seed v13:
  - **292 planchas** con ficha completa (247 iniciales + 45 nacidas de recepciones de compra).
  - Naturales con foto (en demo, la del producto; en producción, la real de cada plancha).
  - Estados reales: 241 disponibles · 4 reservadas · 47 vendidas · 32 en Hueso.
  - **Las recepciones de compra dan de alta planchas** (un lote por plancha, con su código).
  - Las entregas de venta reservan y consumen **planchas concretas** (el sistema elige cuáles salen).
  - **Asesores reales en los 133 pedidos** (Valeria, Diego, vendedor) — antes todo era OdooBot.
  - Asiento de **apertura de existencias** (S/ 996,985.83): con tiempo real, el inventario inicial necesita su débito en la 201; sin él la cuenta quedaba negativa.
- Limpieza de deuda: códigos muertos del hook eliminados, categorías vacías ahora en la jerarquía.

### Dónde ver cada cosa

| Qué | Dónde |
|---|---|
| Tabla de Operaciones | Inventario → Planchas → Tabla de Operaciones |
| Alta masiva | Inventario → Planchas → Alta de Planchas |
| Vista Comercial | Ventas → Planchas (probar con `valeria@pierinelli.com` / `pierinelli`) |
| Ficha de plancha | Clic en cualquier plancha (foto, medidas, reserva, chatter) |
| Planchas de un producto | Ficha del producto → botón "Planchas" |
| Filtros del negocio | En la tabla: Disponibles / Reservadas / Hueso / Naturales... |

### Decisiones técnicas tomadas

1. **Plancha = lote con UoM m²** (Plan §2): venta parcial nativa, costo promedio intacto.
2. La **ubicación referencial es texto libre** (r. 4 del cliente) — sin jerarquía de racks en Odoo.
3. El **estado** se calcula, no se digita: stock físico + reserva vigente. Nadie puede "olvidar" marcar vendida una plancha.
4. En Odoo 19 la valorización continental postea al **facturar** (no al recibir): compras D-201, ventas H-201. Por eso el seed necesita el asiento de apertura.
5. La alerta de retazo usa el **chatter del lote** (sin modelos nuevos).

### Pendiente (próximos bloques)

- ~~Fase 4~~ → completada en sesión 2 (ver abajo).
- ~~Fase 5~~ → completada en sesión 2, salvo etiquetas de código de barras (pendiente por decisión del cliente: "puede esperar, apartado vacío").
- Ajuste menor: reportes de almacén agrupan por subfamilia (ya funcionan); sumar la dimensión plancha donde aporte.
- Conector automático a la tasa SUNAT (API): pendiente — hoy las tasas se cargan a mano en la tabla, que ya registra origen y vigencia.

---

## Sesión 2 — 31 jul 2026 · Fase 3 completa

**Reserva de plancha desde el pedido de venta** ✅ (tareas 14 y 17 del plan; la 13 y 15 salieron en la sesión 1)

| Qué | Detalle |
|---|---|
| Columna **Plancha** en la línea del pedido | El vendedor elige LA plancha concreta (solo muestra disponibles del producto). Al elegirla, la cantidad se propone con sus m². |
| Al confirmar el pedido | La plancha queda **reservada comercialmente** (cliente + asesor del pedido + 7 días) y la **reserva de stock se fuerza a ese lote exacto** — no a cualquiera. |
| **Anti-conflicto** | Si otro vendedor intenta confirmar la misma plancha: bloqueo con mensaje claro (quién la tiene, hasta cuándo). El problema central del ERP anterior, resuelto. |
| Validación de sede | Plancha en otra sede → bloqueo con instrucción (cambiar almacén del pedido o trasladar primero). |
| Al facturar | El **número y fecha de comprobante** quedan escritos en la ficha de cada plancha vendida, con mensaje en su chatter. |

**Verificado end-to-end** (test con rollback, sin ensuciar la demo): reserva → conflicto bloqueado → sede equivocada bloqueada → entrega (estado `vendida`) → factura (`comprobante` en ficha). Perfiles: comercial sin costo ✓ · almacenero con costo ✓ · contador sin acceso a planchas ✓ (cada rol ve lo suyo).

**Archivos:** `models/sale_order.py` + `views/sale_order_views.xml` en `pierinelli_planchas`.

---

## Sesión 2 (cont.) · Fases 4 y 5 completas

### Fase 4 — Producción y merma ✅

**Orden de Producción / Corte** (`Inventario → Planchas → Ordenes de Corte`):

| Qué | Detalle |
|---|---|
| La orden | Plancha origen + cliente/pedido/asesor + tabla de **cortes con medidas** (pieza, cantidad, largo, alto, m²). El sistema muestra en vivo: m² a cortar / retorno / merma. |
| Al ejecutar | El **retorno nace como plancha hija** con código extendido (`BM0726.01` → `BM0726.01.01`), sus medidas nuevas, su foto y el vínculo a la madre. La **merma sale a la Zona de Mermas** (fuera del stock vendible y de la vista comercial) con su valor al costo. Lo cortado queda en la plancha para salir por la entrega del pedido. |
| **PDF con modulación anexa** | Botón "Imprimir OP + Modulación": genera el PDF de la orden (estilo Pierinelli) y le **fusiona los PDFs de AutoCAD** subidos — un solo documento, como pidió el cliente. |
| Validaciones | No se puede cortar más de lo disponible; alerta de **retazo < 0.5 m** en el retorno (sugiere merma/liquidación). |

**Mermas** (`Inventario → Planchas → Mermas` + wizard "Registrar Merma"):
- Registro con **motivo** (corte, rotura, defecto, muestra, otro) y **destino** (asumida por el cliente / pérdida del negocio), valorizada al costo kardex.
- Botón **Reingresar**: si el retazo resulta aprovechable, vuelve al stock de su sede.
- **Reporte PDF de Mermas** con indicadores (total m², valor, pérdida del negocio vs. asumida por clientes) — se imprime desde la lista filtrando el período.

**Motivo obligatorio en ajustes de inventario**: columna "Motivo del ajuste" en el conteo; sin motivo, el ajuste **no se aplica** (bloqueo con mensaje). El motivo queda en la referencia del movimiento.

**Verificado end-to-end** (OP-00007 quedó como demo): corte 3.18 m² + retorno 1.20 m² + merma 0.74 m² (S/ 321.15) → madre quedó exacta en 3.18; PDF fusionado con modulación (43 KB); reingreso de merma OK; ajuste sin motivo bloqueado y con motivo aplicado.

**Bug encontrado y corregido en el camino:** `m2_merma` es calculado sobre lo disponible, que cambia al mover el retorno — había que **congelar las cantidades antes de mover stock** o la merma quedaba en cero.

### Fase 5 — Contabilidad avanzada ✅ (en `pierinelli_reportes`)

**Tipos de cambio configurables** (`Contabilidad → Configuración → Tipos de Cambio`):
- Tabla de tasas por fecha y origen (**SUNAT** compra/venta y **Corporativa**), editable en línea.
- En la factura en USD, campo **"Origen de la tasa"**: el vendedor elige (SUNAT venta/compra, Corporativa, Manual) y el sistema aplica la tasa vigente y **registra cuál se usó** (con seguimiento). Verificado: factura de USD 118 → S/ 440.14 con tasa 3.73 exacta.
- Multi-moneda activado para usuarios internos; 6 tasas demo cargadas.
- Pendiente (documentado): conector automático a la API de SUNAT — hoy la tasa se digita a mano.

**Plantillas de asientos** (`Contabilidad → Asientos contables → Plantillas de Asientos`):
- Se definen una vez las líneas (cuenta, glosa, Debe/Haber, monto fijo o **% de un importe base**).
- "Generar asiento": fecha + importe base → borrador cuadrado en dos clics.
- 2 plantillas demo: **Planilla mensual** (sueldos + EsSalud 9% contra cuentas por pagar) y **Depreciación mensual**. Verificado: planilla de S/ 25,000 → asiento de 4 líneas, Debe = Haber = 27,250.

### Dónde ver lo nuevo

| Qué | Dónde |
|---|---|
| Orden de Corte + PDF con planos | Inventario → Planchas → Ordenes de Corte (OP-00007 de demo) |
| Mermas y reingreso | Inventario → Planchas → Mermas |
| Registrar merma manual | Inventario → Planchas → Registrar Merma |
| Motivo en ajustes | Inventario → Operaciones → Ajustes de inventario (columna Motivo) |
| Tipos de cambio | Contabilidad → Configuración → Tipos de Cambio |
| Origen de tasa | Cualquier factura en USD, junto al campo de tasa |
| Plantillas de asientos | Contabilidad → Asientos contables → Plantillas de Asientos |

### Estado del plan completo

| Fase | Estado |
|---|---|
| 0 — Datos reconstruidos | ✅ |
| 1 — Cimientos (AVCO, tiempo real, familias, fix factura) | ✅ |
| 2 — La plancha como entidad | ✅ |
| 3 — Comercial (reserva desde pedido, perfiles) | ✅ |
| 4 — Producción y merma | ✅ |
| 5 — Contabilidad avanzada | ✅ (salvo etiquetas de barras: a pedido del cliente, "puede esperar") |

### Verificación ejecutada (todo en BD limpia)

```
Instalación 10 módulos ........ OK (registry 88.6s)
Seed v13 ...................... OK (SEED COMPLETO)
292 planchas, códigos bien formados: 292/292
AVCO en vivo .................. 426.00 → 418.08 tras compra a 390.50
Cta 201 = inventario físico ... S/ 791,192.99 (exacto)
Balance General ............... descuadre 0.00
Dashboard y 17 reportes ....... consistentes con el nuevo modelo
Alta masiva + reserva + liberación + código de corte: probados end-to-end
Vistas (operaciones, comercial, form, wizard, producto): compilan
ACL vendedor .................. lee/escribe, sin crear/borrar
```
