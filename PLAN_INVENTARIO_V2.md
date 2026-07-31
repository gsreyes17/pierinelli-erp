# Plan de Inventario V2 — Pierinelli

> Documento de trabajo. Consolida lo hablado en la reunión con el cliente, la
> tabla de 28 columnas de su ERP anterior (su requerimiento de inventario), y la
> investigación técnica contra Odoo 19 Community y la BD actual del proyecto.
>
> **Fecha:** 27 jul 2026 · **Estado:** ✅ **APROBADO — listo para desarrollar**
>
> Las 10 preguntas abiertas fueron respondidas (§11). Sus respuestas están
> incorporadas al plan; el resumen de qué cambió está en §0.1.

---

## 0. Resumen ejecutivo

El requerimiento del cliente no pide mejoras al inventario actual: pide **otro modelo de
datos**. Hoy el sistema dice "tengo 400 m² de Cuarcita Iron Green". El cliente
necesita que diga "tengo estas 20 planchas, cada una con su código, sus medidas,
su foto, su ubicación exacta y su estado". Es un cambio de fondo, no de forma.

La buena noticia: **Odoo 19 Community soporta el modelo correcto de forma
nativa**, y el catálogo actual es lo bastante pequeño y sintético como para
rehacerlo barato.

**La decisión técnica central** (y el hallazgo que condiciona todo lo demás):

> Cada plancha debe ser un **lote** (`stock.lot`) de un producto cuya unidad de
> medida es el **m²**. No un producto individual, y no un número de serie.

El porqué está en §2. De esa decisión cuelgan el código interno, la foto por
plancha, la reserva, el corte con merma y el costo promedio.

**Lo que sí hay que aceptar:** hay 5 limitaciones reales de Odoo Community que
no tienen solución razonable, listadas sin adornos en §9. Ninguna es bloqueante,
pero dos de ellas cambian expectativas del cliente y conviene decírselas antes
de desarrollar, no después.

**Alcance estimado:** 4 a 5 semanas de desarrollo, más limpieza de base de datos.
Detalle y orden en §10.

### 0.1 Qué cambió al responderse las preguntas

Las respuestas del cliente (§11) simplificaron el plan en tres puntos y
cambiaron un criterio:

| Respuesta | Efecto |
|---|---|
| **Ubicación es solo texto referencial** (r. 4) | **Se elimina** la jerarquía de ubicaciones de la Fase 1. Es un campo libre en la plancha ("Zona A · Rack 3"), no una estructura de Odoo. Ahorra días |
| **Todo se maneja igual; solo cambia la foto** (r. 3) | Sin lógica separada para artificiales. Un indicador Natural/Artificial decide si la foto es obligatoria. Fase 2 más simple |
| **Sin rendimiento por piedra** (r. 6) | Se reemplaza por una **alerta de retazo pequeño** (< 0.5 m tras corte). Mejor: detecta el problema real sin pedir un dato que el cliente no tiene |
| **Merma en sección aparte** (r. 5) | La merma sale a una **zona de mermas** fuera de la vista de ventas, donde se decide su destino. Reemplaza el modelo de subproducto que se había propuesto |
| **Mantener datos demo** (r. 1) | Ver §10 Fase 0: se conservan catálogo, fotos y clientes; **las planchas hay que generarlas** porque hoy no existen |

---

## 1. Qué cambia respecto a lo que hay hoy

### 1.1 El modelo actual, medido

Investigado contra la BD real, no supuesto:

| Elemento | Hoy | Qué implica |
|---|---|---|
| Productos | 33, con 5 campos: nombre, código, categoría, precio, foto | Un producto = un tipo de piedra, no una plancha |
| Unidad | m² para todos | Correcto, se conserva |
| Lotes | 4 (solo la demo de corte) | El resto del catálogo no distingue planchas |
| Ubicaciones internas | 5 (una por almacén) | Sin zonas, racks ni posiciones |
| Categorías | 8 planas, 3 de ellas vacías | Sin familia/subfamilia real |
| Atributos de producto | 0 | Sin estructura de variantes |
| Dimensiones | No existen | Ni en producto ni en lote |
| Estado del producto | No existe | Sin disponible/reservado/vendido |
| Asesor en pedidos | 133 pedidos, todos a `OdooBot` | No hay dato de quién vendió |
| Stock | 216 registros, 15 919 m² | Cantidad agregada, sin identidad |

### 1.2 Lo que el cliente exige (tabla de su ERP anterior)

La tabla global del ERP anterior tiene **28 columnas**. Contra lo que hay hoy:

| Columna pedida | Estado | Dónde vivirá |
|---|---|---|
| Almacén | ✅ Existe | `stock.warehouse` |
| Código SAP | ⚠️ Es el código de producto actual | `product.default_code` |
| Ubicación (zona específica) | ❌ No existe | `stock.location` (jerarquía nueva) |
| Descripción del material | ✅ Existe | `product.name` |
| **Código interno (por plancha)** | ❌ **No existe** | `stock.lot.name` — **núcleo del rediseño** |
| Condición (Estándar/Oferta/Liquidación/Hueso) | ❌ No existe | Campo nuevo en lote |
| Largo / Alto | ❌ No existe | Campos nuevos en lote |
| M. Neto / M. Bruto | ❌ No existe | Neto = calculado; Bruto = campo nuevo |
| Cantidad + UM | ⚠️ Parcial (solo m²) | Ver §9.3 — limitación |
| Estado (disponible/vendido/reservado) | ❌ No existe | Campo calculado en lote |
| Familia / Subfamilia | ⚠️ Solo 1 nivel | Jerarquía de categorías |
| Observaciones | ❌ No existe | Campo nuevo en lote |
| Cliente reserva / Asesor | ❌ No existe | Campos nuevos + §6 |
| Nro. y fecha de comprobante | ⚠️ Existe en factura, no en plancha | Enlace desde el lote |
| Inicio / Fin de reserva (7 días) | ❌ No existe | §6 — desarrollo |
| Ref. importación (lote de llegada) | ❌ No existe | Campo nuevo |
| Fecha de ingreso / Antigüedad | ⚠️ Existe en el stock, no visible | Ya disponible, hay que exponerlo |
| **Costo kardex (promedio)** | ❌ **Está en costo estándar** | §4 — corregir |
| Código de barras | ❌ No existe | §9.5 — limitación parcial |
| Precio | ✅ Existe | `product.list_price` |
| Foto por plancha | ❌ No existe | §5 |

---

## 2. La decisión de arquitectura: la plancha es un lote

### 2.1 Las tres opciones evaluadas

**Opción A — Un producto por plancha.** 20 planchas de Iron Green = 20 productos.
*Descartada:* el catálogo crecería a miles de productos, el costo promedio
perdería sentido (§4), y los reportes por familia serían inmanejables.

**Opción B — Número de serie (`tracking='serial'`).** Cada plancha un serial.
*Descartada por un impedimento técnico duro:* Odoo fuerza cantidad = 1 en los
seriales, en múltiples puntos del flujo (`stock_move.py:664` fija `quantity: 1.0`;
`stock_move_line.py:243` lanza error si la cantidad no es 1). **Una plancha con
serial se vende entera o no se vende** — imposible vender 1.5 m² de una plancha
de 3.2 m². Incompatible con el negocio.

**Opción C — Lote (`tracking='lot'`) con UoM en m². ← ELEGIDA.**
Cada plancha es un lote con su cantidad real en m². Permite venta parcial
nativamente, mantiene identidad individual, y la ubicación exacta funciona
(`stock.lot.location_id` se rellena solo cuando el lote está en un único sitio,
que es siempre el caso de una plancha).

> **Aclaración importante sobre el modelo (confirmada con el cliente).**
> "Cada plancha es un registro" **no** significa "cada plancha es un producto del
> catálogo". Las 20 planchas de un contenedor de Cuarzo Verde Transparente
> **comparten el mismo producto**; lo que se lista individualmente es cada
> plancha, con su código interno y su medida.
>
> Esto es precisamente lo que hace posible el **costo promedio** (§4): cuando
> ingresa otro contenedor del mismo material a distinto precio, el sistema
> promedia entre todas las planchas de ese producto. Si cada plancha fuera un
> producto aparte, cada una tendría su costo aislado y no habría nada que
> promediar — el kardex por promedio, que el cliente marcó como tema sensible,
> se perdería.
>
> En la **tabla** se ven 20 líneas. En el **catálogo** se ve 1 producto.

### 2.2 Cómo queda

```
Producto: "Cuarcita Iron Green Traslucid"  [CIG]   UoM: m²   tracking: lot
  │
  ├── Lote CIG1025.01   2.94 m²   3.40 × 1.65 m   PRIN/Zona A/Rack 3   Estándar
  ├── Lote CIG1025.02   3.12 m²   3.20 × 1.70 m   PRIN/Zona A/Rack 3   Oferta
  ├── Lote CIG1025.03   2.88 m²   3.20 × 1.60 m   UG/Showroom          RESERVADO
  └── ... hasta CIG1025.20
```

El producto sigue siendo el tipo de piedra (para catálogo, precio y costo
promedio). El lote es la plancha física (para identidad, medidas, foto y
ubicación). **Ambos niveles conviven** — que es exactamente lo que el ERP
anterior no sabía hacer.

### 2.3 Por qué esto resuelve los tres problemas del ERP anterior

El cliente nombra tres fallas concretas de su ERP anterior. Las tres se resuelven aquí:

1. *"Ingresaba la factura y se acabó, sin indicar cuántas planchas ni sus
   medidas."* → Ahora la recepción exige crear un lote por plancha, con sus
   medidas. No se puede recibir sin detallar.

2. *"El ERP no indicaba cuál plancha se vendía; dos vendedores agarraban la
   misma."* → La venta reserva **un lote concreto**, que queda marcado como
   reservado y con el asesor que lo tomó. Otro vendedor lo ve ocupado (§6).

3. *"Decía 100 m² cuando en realidad eran retazos inservibles."* → Cada lote
   tiene sus medidas reales. Un retazo de 0.4 × 0.6 m es visiblemente un
   retazo, no "0.24 m² de material". Además la condición "Hueso" marca lo
   estancado (§3.2).

---

## 3. El código interno y el ciclo de corte

### 3.1 La nomenclatura

Del ejemplo del cliente: `CIG` + `1025` (mes/año de llegada) + `.` + correlativo.

```
CIG1025.01        plancha 1 del lote de importación de octubre 2025
CIG1025.01.01     lo que quedó tras el primer corte de esa plancha
CIG1025.01.02     lo que quedó tras el segundo corte
```

**Resuelto (r. 2): el prefijo se genera solo.** Sale de las **iniciales de las
palabras del nombre del producto**:

```
"Cuarcita Iron Green"        → CIG
"Mármol Pietra Grey"         → MPG
"Ónix Oro"                   → OO
```

El sistema propone el prefijo al crear el producto y queda **editable** (por si
dos productos colisionan o el cliente prefiere otro). Al recibir mercadería solo
se completa lo que sigue: mes/año y correlativo, que también se autocompletan.

El almacenero, en la práctica, **solo confirma**: escribe "20 planchas" y el
sistema genera `CIG1025.01` … `CIG1025.20`.

### 3.2 Condición del material

Cuatro estados, del documento: **Estándar · Oferta · Liquidación · Hueso**.

"Hueso" es el interesante: material con más de un año que necesita gestión. Como
la antigüedad ya es calculable, el sistema puede **marcarlo solo**: una tarea
programada que pasa a "Hueso" toda plancha con más de 365 días en almacén, y un
aviso al responsable. Se conecta directo con el reporte de antigüedad que ya
existe.

### 3.3 El ciclo de corte

```
Factura de venta
   ↓
Orden de producción (§8)  ── consume ──>  Lote CIG1025.01  (2.94 m²)
   ↓
   ├── Producto vendido al cliente         1.80 m²
   ├── Retorno a stock: CIG1025.01.01      0.90 m²  (con medidas nuevas)
   └── Merma                               0.24 m²  (§7)
```

El retorno con código extendido y medidas menores es desarrollo custom sobre la
orden de fabricación, pero el motor (consumo flexible, subproductos, reparto de
costo) ya está en Community.

---

## 4. Costo promedio — corregir antes que nada

> **Hallazgo que contradice un supuesto del proyecto.** El cliente describe el
> costo kardex como promedio ponderado ("tengo uno de 100, ingresa otro de 120,
> todos pasan a 110"). **Hoy el sistema no hace eso.** Las 8 categorías no
> definen método de costo, así que corren en **costo estándar**.

Consecuencias de dejarlo así:

- El costo no se recalcula al recibir mercadería a otro precio.
- En una orden de corte, **Odoo no reparte el costo** entre pieza y merma si el
  producto está en estándar. La merma no se valorizaría (verificado en
  `mrp_account/models/mrp_production.py:77-85`).

**Corrección:** pasar las 8 categorías a **AVCO (costo promedio)**. Es una hora
de trabajo y **desbloquea el corte con merma valorizada**. Va primero en el plan.

Decisión pendiente con el cliente: activar además **valoración en tiempo real**
(cada movimiento de stock genera su asiento contable automático) en vez de la
periódica actual. Es lo que corresponde a una empresa que quiere que el kardex
cuadre con contabilidad, pero cambia cómo trabaja el contador.

---

## 5. Tipo de material y foto por plancha

### 5.1 Natural vs. Artificial — el eje que gobierna el comportamiento

Se agrega al producto una columna **Tipo de material: Natural / Artificial**.
No es solo informativa: define cómo se comporta el material en todo el sistema.

| | **Natural** (mármol, ónix, cuarcita, granito) | **Artificial** (porcelánico, sinterizada, cuarzo, solid surface) |
|---|---|---|
| Foto | **Una por plancha** — cada veta es única | **Compartida** del formato |
| Identificación | Plancha por plancha, obligatoria | Ver §5.2 |
| Al agotarse | La plancha desaparece con su foto | El formato permanece en catálogo |
| Venta | Se corta, venta parcial | Caja cerrada o plancha entera |
| Filtro comercial | El arquitecto puede pedir "solo piedra natural" | — |

Es mejor eje que dejarlo implícito en la familia: permite filtrar el catálogo,
decidir qué exige foto y qué no, y saber qué se corta y qué se vende cerrado.

### 5.2 Decisión pendiente: ¿los artificiales llevan registro individual?

Si el porcelánico se vende **por caja cerrada** y al cliente le da igual cuál
caja, no tiene sentido dar de alta cientos de cajas una por una: se manejan por
cantidad, como hoy. El detalle plancha por plancha se reserva a las naturales,
donde la veta decide la venta.

Esto **reduce mucho el trabajo diario del almacenero** y concentra el esfuerzo
donde sí paga. Pendiente de confirmar con el cliente (§11, pregunta 3).

### 5.3 Implementación de la foto

- **Foto de catálogo** en el producto — ya funciona, las 33 imágenes existen.
- **Foto de plancha** en el lote — campo nuevo (`stock.lot` no tiene imagen de
  fábrica, pero se le añade el mixin estándar de Odoo sin fricción).
- El tipo de material decide si la foto individual es obligatoria o si hereda
  la del producto.

**Cómo se toma:** desde el celular en el almacén. Odoo es responsive
(`web_responsive` ya instalado), así que el almacenero abre la plancha y sube la
foto con la cámara. Sin desarrollo extra.

**Advertencia de proceso, no técnica:** si llegan 200 planchas al mes, alguien
las fotografía 200 veces. Si eso no se sostiene, el campo queda vacío y la
funcionalidad muere. Vale la pena acordar con el cliente **para qué familias es
obligatorio** (mármol, ónix, cuarcita) y para cuáles no.

---

## 6. Reserva de planchas y perfiles de usuario

### 6.1 Reserva con vencimiento a 7 días

Regla de negocio del documento: las reservas duran 7 días.

**Odoo Community no tiene reservas con vencimiento.** Hay que construirlo:
fecha de inicio y fin en el lote, cliente, asesor, y una **tarea programada que
libere automáticamente** lo vencido, avisando al asesor unos días antes. Es
desarrollo directo, sin complicación.

También hay que construir la **selección de plancha desde el pedido de venta**:
Odoo Community solo permite elegir el lote en el albarán, no en el pedido
(verificado: no existe `lot_id` en la línea de venta). Como el vendedor tiene
que poder decir "te reservo *esta* plancha" desde la cotización, se agrega.

### 6.2 Las dos vistas

El cliente define exactamente dos perfiles, y coincide con lo que
hablamos:

**Vista de Operaciones** (28 columnas) — el control total: costos, ubicación,
antigüedad, importación, valorización.

**Vista Comercial** (13 columnas) — solo lo que el vendedor necesita:

> Almacén · Ubicación · Cód. SAP · Nro. plancha · Condición · Descripción ·
> Largo · Alto · Neto · Stock · UM · Asesor · Observaciones

El comercial **puede editar** lo suyo (marcar vendido/reservado, cliente,
comprobante, observaciones) pero **no ve costo, margen ni valorización**. Esto
se hace con permisos por campo, sin duplicar pantallas.

Perfiles completos a configurar: Almacenero · Comercial · Contador · Gerencia.

### 6.3 Un dato que hoy no existe

Los 133 pedidos de la demo están asignados a `OdooBot`. **No hay asesor real en
ningún registro.** Como el cliente quiere saber quién vendió o reservó cada
plancha, esto hay que sembrarlo desde cero con los vendedores reales.

---

## 7. Mermas: zona propia, fuera de la vista de ventas

**Modelo definido por el cliente (r. 5).** Como cada vez que se usa el material
este sale del inventario, la merma no se trata como subproducto de la orden:
va a una **zona de mermas** separada, donde queda **fuera de la vista comercial**
hasta que se decida su destino.

```
Plancha CIG1025.05  (5.61 m²)
   │
   ├─→ Vendido al cliente        3.85 m²
   ├─→ Retorna a stock  .05.01   1.73 m²   ← visible para ventas
   └─→ ZONA DE MERMAS            0.03 m²   ← NO visible para ventas
            │
            └── se decide su destino:
                 · Merma asumida por el cliente  (venta por metro lineal)
                 · Merma del negocio             (corte por bloques → pérdida)
                 · Reingreso a stock             (resultó aprovechable)
```

La distinción de quién la asume es de negocio, no técnica:

- **Venta por metro lineal** → la asume el **cliente** (se le cobra el material
  completo aunque el sobrante no le sirva).
- **Corte por bloques** → se queda en el **negocio**: pérdida propia, hay que
  valorizarla.

**Lo que hay que construir:** la zona de mermas como ubicación propia, el
registro de qué pasó con cada una, y su exclusión de la vista comercial. Odoo
Community trae desecho con **etiquetas de motivo** de fábrica (hallazgo
positivo: `stock.scrap.reason.tag`) pero llega **sin datos** — se siembran los
motivos reales: rotura en manipulación, defecto de cantera, corte fallido,
muestra, merma de cliente, merma del negocio.

Falta también: el desecho **no tiene menú propio** en Community (hay que
exponerlo), y los **ajustes de inventario no tienen campo de motivo** — es el
único hueco sin nada nativo, se agrega obligatorio para que ningún ajuste quede
sin explicar.

### 7.1 Alerta de retazo pequeño

En lugar de un rendimiento esperado por tipo de piedra — que el cliente indica
que es **impreciso porque hay muchos tipos de corte** (r. 6) — el sistema avisa
cuando un reingreso tras corte queda **por debajo de 0.5 m** en cualquiera de sus
dimensiones.

Detecta el problema real que describieron del ERP anterior (*"decía 100 m²
cuando en realidad era suma de retazos"*) sin exigir un dato que el negocio no
tiene. La alerta sugiere mandarlo a merma o a liquidación en vez de dejarlo
contando como stock vendible.

Cierra con un **reporte de mermas y pérdidas del período** por motivo, destino y
sede, en el mismo estilo PDF de los 17 que ya existen.

---

## 8. Orden de producción con plano adjunto

Lo que pide el cliente: tras la factura, una orden de producción que liste todas
las medidas de corte **y lleve anexada la modulación** (1 a 3 diseños de AutoCAD)
en un solo PDF, para no andar trasladando información entre documentos.

Es una extensión natural de lo que ya construimos con los 17 reportes:

- Documento con cabecera (cliente, comprobante, asesor, fecha), el detalle de
  cortes con sus medidas, la plancha de origen con su código interno y foto, y
  el destino de la merma.
- **Anexo de modulación:** subir 1–3 archivos (PDF o imagen exportada de AutoCAD)
  que se incrustan al final del documento generado.

**Limitación a conocer:** si suben un **DWG nativo**, no se puede incrustar — no
hay lector de DWG. Deben exportar a **PDF o imagen** desde AutoCAD, que es un
paso que ya hacen normalmente. Si suben PDF, se anexan las páginas tal cual.

---

## 8b. Tipos de cambio configurables

**Criterio del cliente (r. 8): decide el vendedor, y queda registrado.** No hay
una regla rígida por flujo — el usuario elige qué conversión aplicar en cada
operación, y el sistema deja constancia de cuál usó.

Lo que se construye:

- Un **lugar donde configurar y agregar conversiones**: la oficial de SUNAT, la
  corporativa propia, y las que el cliente quiera sumar después, cada una con su
  vigencia.
- Un **selector en la operación** (venta, cobro en dólares) donde el vendedor
  elige cuál aplica.
- El registro de **qué tasa se usó, en qué documento y quién la eligió** — que es
  la trazabilidad que pedían.

Odoo Community **sí permite forzar el tipo de cambio por documento** de fábrica;
lo que no trae es de dónde sacar la tasa ni el registro del origen. Eso es lo
que se agrega. Va en Fase 5 (tarea 24).

---

## 9. Limitaciones reales — lo que no se puede o cuesta caro

Sin adornos. Dos de estas cambian expectativas del cliente.

### 9.1 No hay escaneo de códigos de barras con app móvil
El cliente lo menciona como algo "que aún no existe y se quisiera implementar".
Odoo trae el **campo** de código de barras y puede imprimirlos, pero la
**aplicación de escaneo** (`stock_barcode`) es **Enterprise**, no está en
Community. Alternativas: usar un lector físico USB (funciona como teclado, sin
desarrollo), o desarrollar una pantalla de escaneo propia (varios días).
**Recomiendo:** imprimir etiquetas con el código interno ahora, y decidir el
escaneo después con el volumen real de operación.

### 9.2 No hay lectura automática de facturas PDF (OCR)
Relacionado con el error que reportaron al "subir factura". El OCR de Odoo es
**Enterprise + créditos**. En Community, subir un PDF crea la factura vacía con
el archivo adjunto y avisa que no pudo importarlo — **ese aviso es lo que se
interpretó como error, no es un bug.** El camino gratis en Perú es el **XML** de
factura electrónica, que el proveedor está obligado a entregar: ese sí se lee
automáticamente. (Aparte, hay dos correcciones reales que sí haré: falta instalar
un módulo y hay un error al subir sin diario definido.)

### 9.3 Una plancha no puede tener su propio factor de conversión
Esto es técnico pero importante. Odoo permite unidades como "caja" o "plancha",
pero **el factor de conversión es global**: si defines "1 plancha = 3.2 m²", vale
para todo el sistema. **No se puede** tener una plancha de 3.2 m² y otra de 2.8
m² usando la misma unidad.
**Cómo se resuelve:** la unidad de stock es siempre **m²** (que es lo real y
medible), y las medidas de cada plancha viven en sus campos. Para porcelánico
vendido en caja cerrada, se define la caja como unidad propia **por producto**,
lo cual sí funciona porque ahí todas las cajas del mismo producto sí son iguales.

### 9.4 El cálculo de "m² disponibles por plancha" no es agrupable directamente
La cantidad de un lote es un dato calculado, no almacenado, así que no se puede
ordenar ni agrupar por él en listados grandes. **Se resuelve** con un campo
almacenado que se mantiene al día — trabajo conocido, sin riesgo, pero hay que
preverlo o los listados de 2 000 planchas irán lentos.

### 9.5 Emisión electrónica a SUNAT sigue fuera de alcance
Ya se sabía, se repite para que no se asuma lo contrario: el sistema genera los
documentos con numeración peruana correcta, pero **no los envía a SUNAT**. Eso
requiere un proveedor OSE/PSE homologado.

---

## 10. Plan de trabajo

### Fase 0 — Reconstrucción de datos (antes de todo)

**Criterio acordado (r. 1): se mantiene la demo actual como base.** Pero hay una
precisión necesaria — **las planchas no existen hoy** en la BD (son 33 productos
con cantidades agregadas, sin identidad), así que hay que generarlas igual:

| | Qué pasa |
|---|---|
| **Se conserva** | Los 33 productos con sus nombres y **las 33 fotos**, las categorías, los 5 almacenes, los 18 clientes y los vendedores |
| **Se genera nuevo** | **~200 planchas de demo** — entre 4 y 8 por producto, cada una con su código interno, medidas realistas, ubicación referencial y condición |
| **Se regenera** | Los pedidos y facturas: los 133 actuales están atados a movimientos sin planchas. Se rehacen algunos ya con plancha asignada y **asesor real** |

Se recrea la base de datos porque las 45 facturas están contabilizadas y los 268
movimientos bloquean el borrado de productos. El resultado se siente igual —
mismo catálogo, mismas fotos — pero con planchas reales debajo.

De paso se limpia deuda que no conviene arrastrar: 3 categorías vacías, 5
códigos muertos en el arranque, y los 133 pedidos asignados a `OdooBot`.

### Fase 1 — Cimientos (semana 1)

| # | Tarea | Notas |
|---|---|---|
| 1 | Costo promedio AVCO en las 8 categorías | 1 h · desbloquea todo lo demás |
| 2 | Valoración de inventario en tiempo real | r. 9 · cada movimiento genera su asiento |
| 3 | Familia / Subfamilia como jerarquía real | Reemplaza las 8 categorías planas |
| 4 | Indicador **Natural / Artificial** en el producto | Gobierna si la foto individual es obligatoria |
| 5 | Corregir "subir factura" + explicar el OCR | 2 h · cierra un tema abierto |

> **Eliminada del plan:** la jerarquía de ubicaciones (Almacén > Zona > Rack).
> Según r. 4, la ubicación es **solo un texto referencial** para saber dónde ir a
> buscar — no se mueve stock entre racks. Pasa a ser un campo libre en la ficha
> de la plancha (Fase 2). Ahorra varios días sin perder nada.

### Fase 2 — La plancha como entidad (semanas 2–3) ← **el núcleo**

| # | Tarea |
|---|---|
| 6 | Ficha de plancha: código interno, medidas, m² neto/bruto, condición, observaciones, ref. importación, **ubicación referencial** y foto |
| 7 | Generador automático del código: prefijo por iniciales + mes/año + correlativo (§3.1) |
| 8 | Estado de la plancha: disponible / reservada / vendida |
| 9 | Alta masiva en recepción ("20 planchas de 3.40 × 1.65" → genera `.01`…`.20`) |
| 10 | Campo de m² almacenado, para que los listados grandes no se degraden (§9.4) |
| 11 | Vista de Operaciones (28 columnas) |
| 12 | Marcado automático de "Hueso" por antigüedad |

### Fase 3 — Comercial (semana 4)

| # | Tarea |
|---|---|
| 13 | Vista Comercial (13 columnas) con permisos por campo |
| 14 | Reserva de plancha desde el pedido de venta |
| 15 | Vencimiento de reserva a 7 días + liberación automática |
| 16 | Perfiles: Almacenero · Comercial · Contador · Gerencia |
| 17 | Trazabilidad del asesor en venta y reserva |

### Fase 4 — Producción y merma (semana 5)

| # | Tarea |
|---|---|
| 18 | Corte: consumo de plancha, retorno con código extendido y medidas nuevas |
| 19 | **Zona de mermas** fuera de la vista comercial, con destino: cliente / negocio / reingreso (§7) |
| 20 | Alerta de retazo pequeño (< 0.5 m tras corte) — §7.1 |
| 21 | Motivo obligatorio en ajustes de inventario |
| 22 | **Orden de producción en PDF con anexo de modulación en PDF** (r. 7) |
| 23 | Reporte de mermas y pérdidas por motivo, destino y sede |

### Fase 5 — Pendientes de la reunión (según prioridad del cliente)

| # | Tarea |
|---|---|
| 24 | **Tipos de cambio configurables** — el vendedor elige cuál usar y queda registrado (r. 8) |
| 25 | Plantillas de asientos contables |
| 26 | Código de barras: **apartado preparado pero vacío** (r. 10), a activar cuando el volumen lo pida |

---

## 11. Preguntas del cliente — ✅ todas respondidas

Las 10 quedaron cerradas. Se conservan con sus respuestas literales como
registro de las decisiones tomadas; su efecto en el plan está en §0.1.

**Bloquean el diseño de datos (necesarias antes de Fase 2):**

1. **¿El catálogo se arma con datos reales?** Códigos, familias y planchas
   actuales en almacén. Cambia si empezamos con datos suyos o de demo.
   RPTA: manten los datos demo que tenemos al alcance.
2. **El código interno: ¿el prefijo viene del producto?** En el ejemplo `CIG` =
   RPTA: Cuarcita Iron Green. ¿Adoptamos sus códigos reales en el catálogo?
   Si, el codigo viene de la primera letra de las 3 o 4 palabras del producto,adoptalo como ejemplo y si es posible añadelo como prefijo automatizado para solo cambiar lo que le sigue al codigo como la fecha y numero de item.
3. **¿Los materiales artificiales necesitan registro plancha por plancha?**
   (§5.2) Si el porcelánico se vende por caja cerrada y da igual cuál caja, se
   manejan por cantidad y solo las naturales llevan el detalle individual — le
   ahorra al almacenero cientos de altas. Confirmar también la lista de qué
   familias son Natural y cuáles Artificial.
   RPTA: Si todo los productos se manejarian igual, la unica discordia es la imagen, q tiene q ser especifica en caso de ser natural.
4. **La jerarquía de ubicaciones:** ¿cómo están organizados físicamente los
   almacenes? ¿Zonas, racks numerados, caballetes? Hay que copiar su realidad.
   RPTA: Los almacenes tienen su nombre como Zarate, el otro codigo de ubicacion es solo referencial que puede pertenecer un rack zona etc.

**Bloquean producción y merma (antes de Fase 4):**

5. **¿El retazo de merma se revende o se descarta?** Si se revende es
   subproducto con costo propio; si se bota es pérdida. Cambia el modelo.
   RPTA: Se agendaria en otra seccion como merma, como cada que se va usar el producto se extrae del inventario no habria problema en reintroducirlo o aclarar que fue de el, si merma de cliente o merma en inventario. Pero quedaria fuera de vista de ventas hasta que se cambie su destino.
6. **¿Rendimiento esperado por tipo de piedra?** (ej. mármol 82 %, sinterizada
   88 %) — para estimar merma y detectar cortes anómalos.
   RPTA: El rendimiento es muy impreciso porque hay muchos tipos de corte, en todo caso se podria agregar una advertencia si se registra un producto reingresado despues de un corte y donde las medidas den menos de 0.5 m. Pero es opcional.
7. **La modulación de AutoCAD: ¿en qué formato la entregan?** Necesitamos PDF o
   imagen; el DWG nativo no se puede incrustar (§8).
   RPTA: Se incrustara por PDF.

**Se pueden responder después:**

8. **¿Qué tipo de cambio manda en cada flujo?** Lo habitual: SUNAT para compras
   y libros, tasa propia para cotizar y vender.
   RPTA: El usuario o vendedor elige, si se vende y paga en dolares el decide que modelo de conversion usar, por lo que habria que tener un lugar donde configurar o agregar nuevas conversiones, asi se registra que tipo de cambio se uso en donde.

9. **¿Valoración de inventario en tiempo real?** Que cada movimiento genere su
   asiento contable automático (§4).
   RPTA: Si es posible si, ya igual se actualizara la tabla cuando un producto se separe o venda.

10. **Volumen real:** ¿cuántas planchas hay hoy en almacén y cuántas ingresan al
    mes? Define si el escaneo de códigos de barras es urgente o puede esperar.
   RPTA: El codigo de barras puede esperar, se le puede dar un apartado pero vacio, las planchas son algo esporadico no hay un control de momento no nos lo comunica el cliente, pero supongase ejemplos de q cae un lote de 5 planchas de material A, 4 de B 5 de C, etc.
---

## 12. Riesgos

| Riesgo | Impacto | Cómo lo mitigo |
|---|---|---|
| El proceso de fotos no se sostiene en el almacén | La funcionalidad muere vacía | Obligatoria solo en **Natural** (r. 3); en artificial hereda la del producto |
| Dar de alta plancha por plancha alarga la recepción | Rechazo del almacenero | **Alta masiva** (Fase 2, tarea 9): "20 planchas de 3.40 × 1.65" y listo |
| Rendimiento con miles de planchas | Listados lentos | Campo de m² almacenado **desde el inicio** (Fase 2, tarea 10) |
| El cliente espera OCR y escaneo móvil | Expectativa incumplida | Decirlo **ahora**, no al entregar (§9.1, §9.2). El apartado de código de barras queda preparado pero vacío (r. 10) |
| Recrear la BD borra la demo actual | Perder trabajo mostrado | Se conservan catálogo, **fotos**, clientes, módulos y los 17 reportes (§10 Fase 0) |
| Valoración en tiempo real cambia el trabajo del contador | Fricción al entregar | Activarla en Fase 1 y mostrarla temprano, no al final |

---

## 13. Lo que ya está hecho y se conserva

No se toca nada de esto; el rediseño se apoya encima:

- **17 reportes PDF con marca** — 10 de Contabilidad (Balance, EE.RR., Flujo de
  Caja, Indicadores, Diario, Mayor, Comprobación, Antigüedad CxC/CxP, IGV) y 7
  de Almacén (existencias, categoría, crítico, antigüedad, kardex,
  transferencias, rotación).
- **Dashboard "Panorama de Almacenes"** con mapa del Perú y ranking.
- **5 almacenes** configurados.
- **Marca Pierinelli** en todo el backend.
- **Localización peruana** con IGV y numeración de comprobantes.
- **Las 33 fotos** de catálogo.
- **Despliegue en Render** con auto-limpieza.

Los reportes de almacén sí necesitarán un ajuste menor: hoy agrupan por
categoría y deberán agrupar por familia/subfamilia, y ganarán la dimensión de
plancha.

---

*Todo lo afirmado aquí sobre capacidades de Odoo fue verificado contra el código
fuente de la versión 19 Community y contra la base de datos actual del proyecto.
Las limitaciones de §9 son técnicas y comprobadas, no estimaciones.*
