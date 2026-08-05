# Contexto del Proyecto — Pierinelli ERP

> **Propósito de este documento:** síntesis completa de todo lo desarrollado y su
> función frente a la empresa. Sirve para retomar el contexto en cualquier
> momento (nueva sesión de trabajo, otro desarrollador, u otro chat de IA).
> Última actualización: **31 jul 2026** — Plan Inventario V2 completo (fases 0–5).

---

## 1. El negocio y el encargo

**Pierinelli** vende superficies y revestimientos de piedra premium en Perú:
mármol, granito, cuarcita, ónix (naturales) y sinterizada, porcelánico, cuarzo,
solid surface (artificiales). Compra **planchas** (importación por contenedor),
las exhibe/almacena en **5 sedes**, las vende enteras o **cortadas a medida**
(generando **merma**), con venta muy personalizada (el cliente elige *su*
plancha por la veta).

**El encargo:** un ERP sobre **Odoo 19 Community** (sin licencias Enterprise)
que replique lo que su ERP anterior no sabía hacer: identificar **cada plancha
individual** con código, medidas, foto, ubicación y estado; costo promedio
(kardex); reservas de 7 días; órdenes de producción con planos; control de
mermas; y contabilidad peruana (IGV, PCGE) con reportes que Community no trae.

**Documentos hermanos:** [PLAN_INVENTARIO_V2.md](PLAN_INVENTARIO_V2.md) (el plan
aprobado, con las decisiones y sus porqués) · [AVANCES_V2.md](AVANCES_V2.md)
(bitácora de implementación) · [README.md](README.md) (arquitectura del entorno).

---

## 2. Arquitectura del entorno (3 capas)

| Capa | Contenido | Nota |
|---|---|---|
| **Local (Windows)** | `odoo/` (núcleo clonado, NO en git), `.venv/`, PostgreSQL local (BD `odoo`), `odoo.conf` | Arranque: `.\arrancar.ps1` (inyecta wkhtmltopdf al PATH). **No borrar `odoo/`**: es el Odoo local |
| **Git** | `custom_addons/` (6 módulos), `seed_pe.py`, `entrypoint.sh`, Docker/Render configs, `*.md` | Lo único que viaja |
| **Render (nube)** | Imagen oficial `odoo:19` + lo de git + Postgres de Render | `entrypoint.sh` auto-instala, corre el seed, y se **auto-repara** (limpia restos del antiguo módulo `hebrea_website` y desinstala `website`) |

**Recrear BD local desde cero:** ver [LOCAL.md](LOCAL.md) (drop/create BD →
instalar módulos → `cmd /c "... < seed_pe.py"`).

---

## 3. Los 6 módulos y su función para la empresa

### `pierinelli_branding` — la identidad
Login con logo y fondo showroom, navbar negra, acentos dorados (#C9962F).
La empresa ve *su* sistema, no un Odoo genérico.

### `pierinelli_data` — los datos maestros
Compañía (RUC 20131312955, Miraflores, PEN), **5 almacenes** (UG Urban Gallery
Miraflores, PRIN Zárate, VES Villa El Salvador, TRU Trujillo, AQP Arequipa),
jerarquía de categorías **Familia → Subfamilia** (Naturales: Mármol/Granito/
Cuarcita/Ónix; Artificiales: Sinterizada/Porcelánico/Cuarzo/Solid Surface),
todas con **costo promedio (AVCO)** y **valorización en tiempo real**.
Grupos activados: multi-almacén, multi-ubicación, lotes.

### `pierinelli_pe` — Perú
Envoltorio de `l10n_pe` + `purchase`: plan contable PCGE (~1200 cuentas),
IGV 18%, tipos de documento (Factura/Boleta), RUC/DNI. **Simulación**: no envía
a SUNAT (eso requiere OSE/PSE homologado — límite conocido y comunicado).

### `pierinelli_planchas` — el corazón (modelo V2)
**Cada plancha física es un lote (`stock.lot`) de su producto, en m².**
El producto es el tipo de piedra (catálogo, precio, costo promedio); el lote es
la plancha concreta. Qué le da a la empresa:

- **Ficha de plancha**: código interno, largo × alto × espesor, m² bruto/neto,
  condición (Estándar/Oferta/Liquidación/**Hueso**), estado
  (Disponible/Reservada/Vendida), ubicación referencial (texto libre tipo
  "Zona A · Rack 3"), ref. de importación, observaciones (quiñe, veta...),
  **foto** (obligatoria en naturales; artificiales heredan la del producto).
- **Código interno automático**: iniciales del producto + mes/año + correlativo
  (`Cuarcita Iron Green` → `CIG1025.01`); el retorno de un corte extiende el
  código de la madre (`CIG1025.01.01`).
- **Alta masiva**: "20 planchas de 3.40×1.65" → genera `.01`…`.20` con stock.
- **Vista de Operaciones** (tabla completa, Inventario → Planchas) y **Vista
  Comercial** (Ventas → Planchas: sin costos, editable en reserva/observaciones).
- **Reserva desde el pedido de venta**: columna Plancha en la línea; al
  confirmar, reserva comercial (cliente + asesor + 7 días) + reserva de stock
  forzada a ESE lote. **Anti-conflicto**: si otro vendedor intenta la misma
  plancha → bloqueo con mensaje (el problema central del ERP anterior).
  Al facturar, el comprobante queda en la ficha.
- **Crons**: Hueso automático (>365 días) y liberación de reservas vencidas.
- **Orden de Corte** (`pierinelli.orden.corte`): plancha + tabla de cortes con
  medidas + retorno + merma. Al ejecutar: nace la plancha hija, la merma sale a
  la **Zona de Mermas** (fuera del stock vendible), y el PDF de la OP se imprime
  **fusionado con la modulación** (PDFs de AutoCAD) en un solo documento.
  Ligada al pedido y a la factura con botones inteligentes.
- **Mermas** (`pierinelli.merma`): motivo (corte/rotura/defecto/muestra),
  destino (**asumida por el cliente** en venta por metro lineal / **pérdida del
  negocio** en corte por bloques / reingreso), valorizada al costo, con reporte
  PDF. Alerta de **retazo < 0.5 m**.
- **Motivo obligatorio** en ajustes de inventario.

### `pierinelli_reportes` — contabilidad que Community no trae
- Renombra "Facturación" → **"Contabilidad"** y la app abre con el **Tablero**
  (como Enterprise).
- **10 reportes financieros PDF** con marca (wizard con fechas): Balance
  General, EE.RR., Flujo de Caja, Indicadores (8 ratios), Libro Diario, Libro
  Mayor, Balance de Comprobación, Antigüedad CxC, Antigüedad CxP, Resumen IGV
  (estilo PDT 621). Construidos sobre `account.move.line` agrupando por clase
  PCGE (1=activo… 7=ingresos).
- **Tipos de cambio** (`pierinelli.tipo.cambio`): tabla SUNAT/Corporativa por
  fecha; en la factura USD el vendedor elige el **origen de la tasa** (panel
  con radio buttons) y queda registrado. Pendiente: cron a API de terceros
  (apis.net.pe) para la tasa SUNAT automática.
- **Plantillas de asientos** (`pierinelli.plantilla.asiento`): líneas con
  cuenta/lado/% del importe base → asiento borrador cuadrado en 2 clics.
  Demo: Planilla mensual, Depreciación mensual.
- **Bloqueo amable de "Subir factura"**: PDF → mensaje explicando que el OCR es
  Enterprise y que el XML sí se importa. XML pasa normal.

### `pierinelli_almacenes` — visibilidad gerencial
- **Dashboard "Panorama de Almacenes"** (OWL): 5 sedes con tarjetas (m², valor,
  ocupación), mapa del Perú con pines, ranking de productos con foto.
- **7 reportes PDF de almacén**: existencias por sede, composición por
  categoría, stock crítico, antigüedad, kardex, transferencias, rotación.

(+ `web_responsive` de OCA: menú de apps a pantalla completa.)

---

## 4. El hilo funcional completo (lo que la empresa opera)

```
COMPRA         Orden de compra al proveedor → la RECEPCIÓN da de alta las
               planchas (un lote por plancha, con código y medidas)
   ↓
ALMACÉN        292 planchas demo en 5 sedes · tabla de operaciones · fotos ·
               condición Hueso automática · ajustes solo con motivo
   ↓
VENTA          El vendedor ve la Vista Comercial (sin costos), aparta LA
               plancha en la cotización → reserva 7 días, anti-conflicto
   ↓
CORTE          Orden de Corte: piezas con medidas + modulación PDF anexa →
               retorno a stock con código extendido + merma a su zona
   ↓
ENTREGA        El picking despacha exactamente la plancha reservada
   ↓
FACTURA        IGV 18%, numeración peruana, USD con tasa SUNAT/corporativa
               elegida y registrada; comprobante escrito en la plancha
   ↓
CONTABILIDAD   Tiempo real: compra debita Mercaderías (201), venta la
               acredita · AVCO pondera el costo · 10 reportes + plantillas
   ↓
GERENCIA       Dashboard de sedes + 17 reportes + indicadores financieros
```

**Cifras de la demo** (consistentes entre sí): 292 planchas · S/ 791,192.99 de
inventario = cta. 201 = dashboard = reporte de almacén · Balance cuadra 0.00 ·
133 pedidos con asesores reales · OP-00007 ejecutada con retorno y merma.

---

## 5. Decisiones técnicas clave (y por qué)

1. **Plancha = lote, NO serial ni producto**: serial fuerza qty=1 (imposible
   vender 1.5 m² de una plancha); producto-por-plancha rompe el costo promedio.
2. **UoM siempre m²**: el factor de conversión de UoM es global en Odoo — no
   puede haber "1 plancha = X m²" variable. Las medidas viven en la ficha.
   *Corolario (venta en losas):* por eso las **losas pre-cortadas** NO son una
   unidad de medida sino una capa de conteo sobre los m². La plancha declara su
   `modo_venta` (m² / piezas) y el tamaño de pieza; `piezas_disponibles` se
   almacena para poder filtrar por SQL. La línea de venta captura piezas y
   convierte a m², que es lo único que toca stock, AVCO y contabilidad. El
   precio por pieza se deriva del precio por m².
3. **Ubicación referencial = texto libre** (decisión del cliente): no se mueve
   stock entre racks, solo se necesita saber dónde buscar.
4. **Merma en zona propia** (decisión del cliente), no subproducto MRP: sale del
   stock vendible, se decide su destino después.
5. **AVCO + tiempo real**: sin AVCO no hay kardex promedio ni reparto de costos.
6. **Estados calculados, no digitados**: disponible/reservada/vendida sale del
   stock físico + reserva vigente. Nadie "olvida" marcar.

## 6. Gotchas de Odoo 19 aprendidos (leer antes de tocar código)

- QWeb en reportes: **no** `str.format`, **no** `_fields` (safe_eval bloquea
  underscore), **no** `t-field` directo en `<td>` (envolver en `<span>`);
  montos de wizards pre-formateados en Python a claves `_s`.
- `o`/`docs` del contexto de render deben ser **recordset**, no dict.
- **`stock.valuation.layer` no existe** en v19: la valorización continental
  postea **al facturar** (compra D-201, venta H-201) → el stock inicial por
  quants necesita **asiento de apertura** o la 201 queda negativa.
- Ubicaciones virtuales **sin xmlid** en v19 → `get_location_mermas()` es
  get-or-create.
- Search views: `<group>` sin `expand`/`string`.
- `invoice_currency_rate` = moneda extranjera por 1 PEN → aplicar `1/tasa`.
- `_render_qweb_pdf(report_ref, res_ids=...)` (nueva firma).
- `odoo shell` **no comitea al salir** — tests sin `env.cr.commit()` no
  ensucian.
- Al ejecutar la Orden de Corte, **congelar m2_merma/m2_retorno en variables
  antes de mover quants** (el compute depende del disponible, que cambia).
- Campos calculados (`qty_available`, `product_qty` de lote) no van en domains
  SQL ni group_by → por eso `m2_disponible` es **almacenado**.
- Plan PE: depreciación es cuentas `6811%`/`3911%` (no 6814/3913).

## 7. Usuarios demo (todos con contraseña `pierinelli`)

`gerente` (todo) · `vendedor`, `valeria@`, `diego@` (comercial, sin costos) ·
`almacen`, `carlos@` (inventario) · `compras` · `contabilidad`, `rosa@` ·
`aquino@` (producción) · `jorge@pierinelli.com` (dueño, todo).

## 8. Pendientes reales

| Qué | Estado |
|---|---|
| Conector API tasa SUNAT (cron diario) | Diseño listo, falta elegir proveedor (~medio día) |
| Etiquetas de código de barras | Cliente: "puede esperar". La app de escaneo móvil es Enterprise; alternativa: lector USB |
| Envío real a SUNAT (facturación electrónica) | Fuera de alcance Community — requiere OSE/PSE |
| OCR de facturas PDF | Enterprise. El XML sí se importa |
| Reportes de almacén con dimensión plancha | Mejora menor opcional |
