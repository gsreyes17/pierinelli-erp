# Guía del Módulo de Almacenes (Inventario) — Pierinelli

Manual práctico para operar el inventario multi-sede de Pierinelli en Odoo 19.
El módulo se llama **Inventario** en el menú principal.

> **Sugerencia de captura (para la presentación):** cada sección marca con 📸
> el momento ideal para tomar una pantalla.

---

## 1. Panorama: las 5 sedes

Pierinelli opera **5 almacenes** reales, cada uno con su propia ubicación de
existencias y su juego de operaciones (recepción, entrega, traslado, manufactura):

| Código | Almacén | Ubicación física | Existencias (demo) |
|---|---|---|---|
| **UG** | Pierinelli Urban Gallery | Miraflores (showroom) | ~3,700 m² |
| **PRIN** | Almacén Principal | Zárate | ~3,000 m² |
| **VES** | Almacén Villa El Salvador | Villa El Salvador | ~3,000 m² |
| **TRU** | Almacén Trujillo | Trujillo | ~3,100 m² |
| **AQP** | Almacén Arequipa | Arequipa | ~3,000 m² |

**Dónde verlo:** `Inventario → Configuración → Almacenes`.
📸 *Captura del listado de 5 almacenes.*

**Concepto clave:** cada almacén tiene una **ubicación de existencias**
(`UG/Existencias`, `PRIN/Existencias`, …). El stock de un producto siempre vive
en una ubicación; por eso el mismo producto puede tener cantidades distintas en
cada sede.

---

## 2. El tablero de Inventario (pantalla de inicio)

Al entrar a **Inventario** ves tarjetas por tipo de operación y por almacén:
- **Recepciones** — entradas de mercadería (compras, importaciones).
- **Órdenes de entrega** — salidas hacia el cliente (ventas).
- **Traslados internos** — mover placas entre sedes.
- **Manufactura** — corte de placas madre en piezas (ver sección 7).

Cada tarjeta muestra un contador de operaciones **por procesar**.
📸 *Captura del tablero con las tarjetas por almacén.*

---

## 3. Consultar stock de un producto por sede

1. `Inventario → Productos → Productos`.
2. Abre un producto (p. ej. *Cuarcita Enigma*).
3. Botón **En existencias** (arriba a la derecha) → ves la cantidad total y,
   al entrar, el desglose **por ubicación/almacén**.

Alternativa rápida (vista global): `Inventario → Productos → Ubicaciones` o el
reporte `Inventario → Reportes → Existencias`, que lista **producto × almacén**.
📸 *Captura del desglose de un producto mostrando las 5 sedes.*

> Aquí se aprecia el criterio "cada plancha es un SKU con su stock por sede".

---

## 4. Recepción de mercadería (entrada)

Las recepciones **se generan solas** al confirmar una Orden de Compra, pero
también puedes crear una manual.

**Flujo automático (recomendado):**
1. `Compras → Órdenes de compra` → confirma un pedido.
2. Odoo crea una **Recepción** en el almacén del pedido.
3. `Inventario → Recepciones` → abre la recepción → **Validar**.
4. El stock sube en la ubicación de ese almacén.

**Recepción manual:**
1. `Inventario → Recepciones → Nuevo`.
2. Elige el proveedor, agrega productos y cantidades → **Validar**.

📸 *Captura de una recepción validada (estado "Hecho").*

---

## 5. Entrega al cliente (salida)

1. `Ventas → Pedidos` → confirma un pedido de venta.
2. Odoo crea una **Orden de entrega** en el almacén configurado del pedido.
3. `Inventario → Órdenes de entrega` → abre → **Validar**.
4. El stock baja en la ubicación de ese almacén.

📸 *Captura de una entrega validada.*

> Si el stock no alcanza, Odoo lo marca en **espera**; sirve para detectar
> quiebres de inventario antes de despachar.

---

## 6. Traslado interno entre sedes (mover placas)

El caso típico de Pierinelli: una placa está en **Principal (Zárate)** y el
cliente la quiere ver en el **showroom Urban Gallery (Miraflores)**.

1. `Inventario → Traslados internos → Nuevo`
   *(o desde la tarjeta "Traslados internos" del almacén de origen).*
2. **Ubicación de origen:** `PRIN/Existencias`.
3. **Ubicación de destino:** `UG/Existencias`.
4. Agrega el producto y la cantidad (m²).
5. **Marcar como "Por hacer"** → **Validar** cuando la placa sale físicamente.

Resultado: el stock baja en Principal y sube en Urban Gallery.
📸 *Captura del traslado PRIN → UG.*

---

## 7. Trazabilidad: de placa madre a piezas cortadas

Pierinelli corta una **placa madre** en varias **piezas**. Esto se modela con
**lotes/números de serie** y una **orden de fabricación (Manufactura)**:

1. `Inventario → Productos` → la placa madre y las piezas tienen **seguimiento
   por lote/serie** activado.
2. La **Orden de Fabricación** (`Fabricación → Órdenes de fabricación`) consume
   la placa madre (lote de origen) y produce las piezas (lotes hijos).
3. **Ver la genealogía:** `Inventario → Productos → Números de serie/lote` →
   abre un lote → pestaña **Trazabilidad** → ves de qué placa madre proviene y
   en qué venta/entrega terminó cada pieza.

📸 *Captura de la trazabilidad mostrando placa madre → piezas.*

> Este es el argumento fuerte para el cliente: **cada m² es rastreable** desde la
> placa original hasta la obra donde se instaló.

---

## 8. Ajuste de inventario (conteo físico)

Cuando el conteo real difiere del sistema:

1. `Inventario → Operaciones → Ajustes de inventario`.
2. Filtra por almacén/ubicación.
3. En cada línea escribe la **Cantidad contada** real.
4. Botón **Aplicar** → Odoo genera el movimiento de ajuste (positivo o negativo).

📸 *Captura de un ajuste aplicado.*

---

## 9. Reportes de inventario útiles

`Inventario → Reportes`:
- **Existencias** — stock actual por producto y ubicación.
- **Movimientos de producto** — historial de entradas/salidas (kardex).
- **Valoración** — valor del inventario (cantidad × costo).

📸 *Captura del reporte de Existencias filtrado por almacén.*

---

## 10. Flujo completo de ejemplo (para la demo)

1. **Compra** una placa → se recibe en **Principal (PRIN)**.
2. **Traslada** la placa a **Urban Gallery (UG)** para exhibición.
3. **Corta** la placa en piezas con una **Orden de Fabricación** (lotes hijos).
4. **Vende** una pieza → se genera la **entrega** desde UG.
5. **Consulta la trazabilidad** de esa pieza: aparece la placa madre de origen.
6. **Revisa Existencias**: el stock refleja todos los movimientos por sede.

Con esto se demuestra el ciclo logístico completo, multi-sede y con
trazabilidad placa→pieza — el diferenciador de Pierinelli.

---

### Roles y permisos
El usuario **`almacen`** (contraseña `pierinelli`) ve solo la app **Inventario**.
Úsalo para mostrar la operación desde la perspectiva del almacenero.
Ver también **[LOCAL.md](LOCAL.md)** para la tabla de usuarios.
