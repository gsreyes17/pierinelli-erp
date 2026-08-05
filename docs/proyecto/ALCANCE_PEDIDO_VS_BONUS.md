# Alcance: lo que pidió el cliente vs. lo que damos de bonus

> Conceptos bien definidos para la negociación y la presentación: qué parte del
> sistema responde a un **pedido explícito** del cliente, qué fue **propuesto
> por nosotros y aprobado**, y qué es **bonus de iniciativa propia** (valor
> agregado que no estaba en ningún requerimiento).
>
> Actualizado: 31 jul 2026.

---

## 1. Pedido explícito del cliente ✅

Lo que el cliente pidió con sus palabras (tabla de 28 columnas de su ERP
anterior, reuniones y comentarios). Todo esto está **entregado**:

| Pedido | Dónde quedó |
|---|---|
| Tabla global de inventario (28 columnas: código interno, medidas, condición, estado, reserva, comprobante, kardex...) | Inventario → Planchas → Tabla de Operaciones |
| Vista comercial reducida y editable (sin costos) | Ventas → Planchas |
| Código interno por plancha `CIG1025.01`, y `.01.01` tras cada corte | Automático al recibir/cortar |
| Condición: Estándar / Oferta / Liquidación / Hueso | Campo en la ficha de plancha |
| Estado: disponible / reservado / vendido | Calculado, nadie lo digita |
| Medidas largo/alto, m² neto y bruto | Ficha de plancha |
| Foto única por producto natural; compartida en artificiales | Ficha (naturales avisan si falta foto) |
| Reserva de 7 días con cliente, asesor y fechas | Botón Reservar + liberación automática |
| Asesor que vendió o reservó | En la plancha y en el pedido |
| N° y fecha de comprobante en la plancha | Se escribe al facturar |
| Familia / Subfamilia | Jerarquía Naturales/Artificiales |
| Ubicación referencial ("para ir a buscar el producto") | Texto libre en la ficha |
| Ref. importación, fecha ingreso, antigüedad | Ficha de plancha |
| **Costo kardex promedio** ("100+120→110") | AVCO activo y verificado |
| Cantidad + UM (m², cajas) | m² base; caja definible por producto |
| Registro de mermas: ¿la asume el cliente o el negocio? | Zona de Mermas + destino + valor |
| **Orden de producción tras la factura, con medidas de corte y modulación (AutoCAD) anexa en un solo documento** | Orden de Corte + "Imprimir OP + Modulación" |
| Ligar la factura con la orden de producción | Botones inteligentes en factura y pedido |
| Tipo de cambio SUNAT / propio, elegible y registrado, configurable | Contabilidad → Tipos de Cambio + panel en factura |
| Plantillas de asientos contables | Contabilidad → Plantillas de Asientos |
| Que "Facturación" se vea como **Contabilidad** (estilo premium) | Menú renombrado + tablero de inicio |
| Explicar/bloquear el error de "subir factura" | Bloqueo amable con instrucciones |
| Vistas separadas por tipo de usuario | Perfiles: almacenero, comercial, contador, gerencia |
| 5 sedes reales multi-almacén | Configuradas desde el inicio |
| IGV 18%, RUC, comprobantes peruanos (simulación SUNAT) | Localización activa |
| Código de barras | **Aplazado por el cliente** ("puede esperar") — apartado preparado |

## 2. Propuesto por nosotros, aprobado por el cliente 🤝

Ideas nuestras que se validaron antes de construir (quedaron registradas en el
[PLAN_INVENTARIO_V2.md](PLAN_INVENTARIO_V2.md) §11):

| Propuesta | Por qué se propuso |
|---|---|
| Alerta de retazo < 0.5 m tras un corte | Reemplaza el "rendimiento por piedra" que el cliente descartó por impreciso; ataca su problema real ("100 m² que eran retazos") |
| Merma como **zona propia** fuera de la vista de ventas | El cliente definió el criterio; nosotros el mecanismo |
| Corrección a costo promedio + valorización en tiempo real | El cliente creía tener promedio; detectamos que corría en estándar y lo planteamos |
| Prefijo del código generado por iniciales, editable | El cliente dio el formato; la automatización fue propuesta y aceptada |
| Mantener datos demo pero generando ~300 planchas reales | Acordado en la revisión del plan |

## 3. Bonus de iniciativa propia 🎁

Nadie lo pidió — es valor agregado que diferencia la propuesta:

| Bonus | Qué aporta |
|---|---|
| **17 reportes PDF con la marca** (10 contables + 7 de almacén) | Balance, EE.RR., Flujo de Caja, Indicadores, IGV estilo PDT 621, kardex, rotación... Community no trae ninguno |
| **Dashboard "Panorama de Almacenes"** con el mapa real del Perú | Las 5 sedes con valor, ocupación y ranking, sobre la frontera geográfica oficial |
| **Anti-conflicto de vendedores** con mensaje explicativo | El cliente contó el problema; el bloqueo proactivo con "quién la tiene y hasta cuándo" es diseño nuestro |
| **Alta masiva de planchas** ("20 planchas de 3.40×1.65" → códigos y stock de golpe) | Sin esto, la recepción plancha por plancha sería un castigo |
| Marcado **automático** de Hueso (>1 año) + liberación **automática** de reservas vencidas | El cliente definió las reglas; que el sistema las ejecute solo es bonus |
| **Motivo obligatorio en ajustes de inventario** | Deriva de su "ser accesibles con el control"; ningún m² desaparece sin explicación |
| Reingreso de mermas valorizado + reporte PDF de mermas | Cierra el ciclo completo del material |
| Fusión real de PDFs (OP + planos en un archivo) | Lo pedido era anexar; entregamos un solo documento imprimible |
| Tablero de Contabilidad como pantalla de inicio (estilo Enterprise) | Pedían el título; dimos la experiencia completa |
| Panel de tipo de cambio con radio buttons + kanban de tasas | Pedían la función; el diseño limpio es bonus |
| **Deploy auto-reparable en Render** | La nube se limpia e instala sola en cada push |
| Documentación completa (guías, plan, contexto, presentación con marca en HTML+PDF) | Transferencia de conocimiento incluida |
| Usuarios demo por rol con datos coherentes (S/ 791 mil que cuadran al centavo entre almacén, dashboard y contabilidad) | La demo se defiende sola ante un contador |

---

## Cómo usarlo en la conversación con el cliente

- **La sección 1 responde**: "todo lo que ustedes pidieron, está — y así se llama
  en el sistema".
- **La sección 2 muestra método**: no improvisamos; proponemos, ellos deciden.
- **La sección 3 es el argumento de valor**: lo que recibieron por encima de lo
  contratado. Útil si aparece la pregunta "¿y esto cuánto costaría con otro
  proveedor / con Enterprise?".

Pendientes honestos (siempre decirlos junto al bonus): envío real a SUNAT
(requiere OSE/PSE), OCR de PDF (Enterprise), escaneo móvil (Enterprise; hay
alternativa con lector USB), API automática de tasa SUNAT (mejora corta ya
diseñada).
