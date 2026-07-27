# Respuesta a los comentarios del cliente — Pierinelli (Odoo 19)

Cada comentario se clasifica en una de tres categorías:

- 🟢 **Confusión / navegación** → el sistema ya lo hace, solo hay que mostrar dónde.
- 🟡 **Límite de Community** → Odoo Community no lo trae; requiere Enterprise o un módulo externo (OCA / partner SUNAT).
- 🔵 **Pendiente por implementar** → se puede agregar al sistema; queda como trabajo futuro.

---

## 1. "Falta el módulo Contabilidad, sino no podemos registrar factura de compras locales e importaciones."

🟢 **Confusión de nombre — el módulo YA está instalado y funcionando. ✅ RESUELTO: ahora el menú se llama "Contabilidad".**

- En Odoo **Community**, la contabilidad venía rotulada como **"Facturación"**, no "Contabilidad", aunque es el mismo motor contable (`account`): asientos, plan de cuentas peruano (1236 cuentas PCGE), IGV 18%, diarios, impuestos.
- **Ya renombramos el menú principal a "Contabilidad"** (módulo `pierinelli_reportes`), para que el cliente lo reconozca de inmediato. El motor no cambia; solo la etiqueta que ve el usuario.
- **Facturas de compra (locales e importaciones) SÍ se registran hoy.** De hecho ya hay **5 facturas de proveedor** cargadas en la demo. Ver punto 3 para el cómo.

> **Qué decirle al cliente:** "El módulo contable está activo y ahora se llama *Contabilidad*. Registra compras locales e importaciones sin problema."

---

## 2. "Su core es venta de pisos de lujo... ¿más contexto/código para complementar este módulo que se ve un poco básico?"

✅ **RESUELTO — construimos un módulo propio de Estados Financieros con la marca Pierinelli.**

Community no trae los estados financieros con formato oficial (eso es Enterprise).
En lugar de depender de eso, desarrollamos el módulo **`pierinelli_reportes`**, que
los genera directamente sobre la contabilidad real (PCGE peruano) y los imprime en
PDF con el diseño Pierinelli (negro/dorado). Incluye:

| Reporte | Qué muestra |
|---|---|
| **Balance General** (Estado de Situación Financiera) | Activo, Pasivo y Patrimonio por cuenta PCGE, con resultado del ejercicio. Cuadra automáticamente (partida doble). |
| **Estado de Resultados** (Ganancias y Pérdidas) | Ingresos vs. costos/gastos, utilidad bruta, Impuesto a la Renta estimado (29.5%), utilidad neta, **margen** y tarjetas de indicadores. |
| **Balance de Comprobación** | Sumas y saldos por cuenta (Debe/Haber, saldo deudor/acreedor). |
| **Libro Mayor** | Detalle de movimientos por cuenta con saldo corrido. |

**Cómo se usa:** `Contabilidad → Reportes → Estados Financieros` → elige el rango de
fechas → botón del reporte → se genera el PDF con la marca.
📸 *Captura ideal para la presentación: el Estado de Resultados con las tarjetas de
indicadores (Ingresos, Gastos, Utilidad Neta, Margen).*

Lo que **sigue siendo límite de Community** (no lo cubre este módulo):
| Función | Dónde se consigue |
|---|---|
| Envío real de comprobantes a **SUNAT** (facturación electrónica / OSE) | 🟡 Requiere partner SUNAT + certificado digital + módulo EDI. **Hoy es simulación funcional.** |
| Conciliación bancaria asistida, activos fijos, presupuestos | 🟡 Enterprise |

---

## 3. "En compras no tengo la opción crear factura." / "Si coloco *Subir*, pide un archivo; debería decir *Crear factura*, pero no me sale."

🟢 **Confusión de flujo — el botón existe, pero aparece DESPUÉS de confirmar la orden de compra.** El botón *Subir* que viste es otra cosa (adjuntar un PDF externo), no el flujo correcto.

**Flujo correcto (así están cargadas las 5 compras de la demo):**

1. **Compras → Órdenes de compra** → abrir o crear una.
2. Botón **Confirmar pedido** (la orden pasa de *Solicitud de presupuesto* a *Pedido de compra*).
3. **Recién ahí aparece arriba el botón morado `Crear factura`** (Odoo espera a que confirmes la compra antes de dejarte facturarla — no puedes facturar un presupuesto sin confirmar).
4. Se abre el borrador de **factura de proveedor** → ajustas fecha/importes → **Confirmar**.
5. Botón **Registrar pago** cuando pagas.

> **Por qué no lo veías:** si la orden está todavía como *Solicitud de presupuesto* (sin confirmar), el botón `Crear factura` **no se muestra**. El botón *Subir/Upload* que sí aparece es para adjuntar un archivo (una factura escaneada del proveedor), no para generarla — por eso te pedía un archivo.

**Ruta alternativa** (para facturas de compra que llegan sin orden previa, típico en importaciones):
`Facturación → Proveedores → Facturas → Nuevo`.

✅ Verificado: las 5 órdenes de compra de la demo (`P00001`–`P00005`) están **confirmadas y facturadas** — el flujo funciona.

---

## 4. "Me llama más la atención saber cómo usar el módulo de Almacenes."

🟢 **Funciona hoy — es guía de uso, no implementación.** Hay **5 sedes** configuradas.

**Almacenes ya configurados:**
| Código | Almacén | Ubicación |
|---|---|---|
| UG | Urban Gallery | Miraflores |
| PRIN | Principal | Zárate |
| VES | — | Villa El Salvador |
| TRU | — | Trujillo |
| AQP | — | Arequipa |

**Operaciones clave del módulo (Inventario):**
1. **Inventario → Productos** → cada plancha/producto tiene su stock por almacén y su costo.
2. **Transferencias internas** (mover placas entre sedes): `Inventario → Operaciones → Transferencias` → *Nuevo* → tipo *Transferencia interna* → almacén origen/destino.
3. **Recepciones** (entrada de compra): se generan solas al confirmar una orden de compra; se validan en `Inventario → Recepciones`.
4. **Entregas** (salida por venta): se generan al confirmar una venta; se validan en `Inventario → Entregas`.
5. **Ajuste de inventario** (conteo físico): `Inventario → Operaciones → Ajustes de inventario`.
6. **Trazabilidad placa → piezas** (ya implementada con lotes/MRP): `Inventario → Trazabilidad → Números de serie/lote` — se ve la genealogía de una placa madre y las piezas cortadas.

> ✅ **Ya está lista la guía paso a paso:** ver **[GUIA_ALMACENES.md](GUIA_ALMACENES.md)**
> — cubre stock por sede, recepciones, entregas, traslados entre sedes, trazabilidad
> placa→pieza, ajustes de inventario y un flujo completo para la demo, con puntos de captura marcados 📸.

---

## 5. "Me dijeron que Odoo ahora tiene una IA que ayuda a manejar el sistema, ¿cómo la uso o no es accesible para mí?"

🟡 **No accesible en esta instalación (Community + self-hosted).**

Odoo 19 introdujo **"Odoo AI"** (asistente con IA, redacción de correos, resúmenes, sugerencias). Pero:
- **Requiere Odoo Enterprise** (suscripción de pago) **y** conexión a los servicios en la nube de Odoo (Odoo Online / Odoo.sh). No corre en Community.
- Al estar **auto-alojado** (tu propio servidor/Render), aunque tuvieras Enterprise, muchas funciones de IA dependen de los créditos y servicios cloud de Odoo (IAP).
- **Conclusión:** con la configuración actual (Community, self-hosted) **la IA de Odoo no está disponible.** Requeriría migrar a Odoo Enterprise en la nube de Odoo.

> **Alternativa 🔵 (si interesa IA sobre los datos actuales):** se puede conectar la base PostgreSQL a herramientas externas (Power BI ya contemplado, o un asistente propio vía API) sin depender de la IA de Odoo. Es un desarrollo aparte.

---

## Resumen ejecutivo

| # | Comentario | Categoría | Estado |
|---|---|---|---|
| 1 | "Falta Contabilidad" | 🟢 Confusión de nombre | ✅ **Resuelto:** el menú ahora se llama **Contabilidad**. |
| 2 | "Contabilidad se ve básica" | 🟡 Límite Community | ✅ **Resuelto:** módulo `pierinelli_reportes` con Balance, EE.RR., Mayor y Balance de Comprobación en PDF con marca. |
| 3 | "No hay *Crear factura* en compras" | 🟢 Confusión de flujo | **Confirmar** la orden primero → aparece `Crear factura`. Funciona. |
| 4 | "Cómo usar Almacenes" | 🟢 Guía de uso | ✅ **Resuelto:** ver [GUIA_ALMACENES.md](GUIA_ALMACENES.md). |
| 5 | "IA de Odoo" | 🟡 Límite Community | No disponible (necesita Enterprise + cloud de Odoo). |

**En una frase:** de los 5 comentarios, **4 ya están resueltos** (menú Contabilidad,
estados financieros con marca, guía de almacenes, y el flujo de crear factura aclarado);
solo **la IA de Odoo** queda fuera por ser exclusiva de Enterprise en la nube de Odoo.
