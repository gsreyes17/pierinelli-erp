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

- **Fase 3**: reserva de plancha desde el pedido de venta (`lot_id` en línea de venta); perfiles finos por campo.
- **Fase 4**: flujo de corte completo (consumo → retorno con código extendido), zona de mermas con destino, motivo obligatorio en ajustes, orden de producción PDF con modulación anexa, reporte de mermas.
- **Fase 5**: tipos de cambio configurables, plantillas de asientos, etiquetas de código de barras.
- Ajuste menor: reportes de almacén agrupan por subfamilia (ya funcionan); sumar la dimensión plancha donde aporte.

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
