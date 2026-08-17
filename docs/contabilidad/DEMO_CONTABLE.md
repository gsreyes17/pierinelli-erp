# Demo contable: guion y libros

Este documento sirve para dos cosas: conducir una **demostración de 4 a 6
minutos** del recorrido comercial y contable (venta → entrega → factura → pago,
y compra → detracción), y quedar como **referencia de los libros y formatos**
disponibles en **Contabilidad → Reportes → Libros y SIRE**. Debe mostrarse con
un periodo que contenga datos de prueba. El ERP registra y controla la
operación; la presentación electrónica ante SUNAT se habilita en una fase
posterior (ver el alcance tributario al final).

## El guion por escenas

### Escena 1: venta, entrega y factura

1. Ir a **Ventas → Pedidos → Cotizaciones** y abrir una cotización o crear una
   nueva con un cliente con RUC, productos, cantidades y precio.
2. Confirmar el pedido. Abrir el botón de **Entrega**, comprobar cliente,
   almacén de origen, lotes y cantidades, y pulsar **Validar**. Esta operación
   pasa a **Inventario → Operaciones → Entregas** y alimenta la opción **Guías
   de remisión y entregas** del centro de reportes.
3. Volver al pedido y pulsar **Crear factura**. En la factura revisar cliente,
   diario de ventas, RUC, fecha, moneda, base e IGV; seleccionar el tipo de
   comprobante cuando corresponda y pulsar **Confirmar**.
4. Usar **Registrar pago** para asociar el cobro a Caja o Banco y comprobar que
   la factura quede pagada.
5. Cerrar la escena en **Contabilidad → Reportes → Libros y SIRE** mostrando el
   rastro completo de la misma operación:
   - **Registro de Ventas 14.1 / vista RVIE**;
   - **Libro Caja y Bancos 1.2** si se pagó por transferencia;
   - **Guías de remisión y entregas**;
   - **Kardex 13.1** o **Existencias por almacén**.

Qué decir: “La operación nace una sola vez. El pedido desencadena la salida de
almacén; la factura genera el asiento; y el cobro deja trazabilidad financiera.”

Resultado que se debe explicar: una venta produjo pedido, salida de almacén,
trazabilidad logística, factura, asiento, pago, movimiento bancario, registro de
ventas y disminución de existencias.

#### Venta en dólares y tasa contable

1. En la cotización, en **Lista de precios**, elegir **USD**. La lista contiene
   un precio comercial fijo por producto en dólares; por ejemplo, el precio que
   el cliente negocia por m² no cambia si mañana varía la cotización bancaria.
2. Debajo aparece **Tipo de cambio**. Pulsar **Cambiar** y elegir **SUNAT
   venta** o **Corporativa**. La tasa queda registrada en la cotización y se
   copia a la factura.
3. Para revisar o editar las tasas ir a **Contabilidad → Configuración → Tipos
   de Cambio**. El botón **Actualizar desde SUNAT** está siempre visible en la
   lista y trae la tasa del día sin pasos previos. Comercial define el precio
   USD; Contabilidad define o aprueba la tasa que convierte ese documento a
   soles.
4. En la factura USD, el total se conserva en USD y el asiento conserva tanto
   el importe en dólares como su equivalencia en PEN. Si el cliente paga el
   mismo importe en USD, no debería existir diferencia de cambio. Si paga en
   PEN o con una tasa distinta, la diferencia se reconoce al conciliar el pago.

Qué decir: “No confundimos precio y tipo de cambio. El precio USD es el acuerdo
comercial con el cliente; SUNAT o la tasa corporativa define la equivalencia
contable en soles de ese comprobante. Ambas decisiones quedan trazables.”

### Escena 2: tipos de comprobante y notas

1. Ir a **Contabilidad → Configuración → Tipos de Comprobantes** para mostrar
   los tipos internos: factura `01`, boleta `03`, nota de crédito `07`, nota de
   débito `08`, recibo por honorarios, importación y planilla de movilidad.
2. Para una nota de crédito, abrir una factura publicada y usar la acción de
   **Nota de crédito / Revertir**. Revisar el documento resultante antes de
   publicarlo.
3. Para una nota de débito, usar el flujo de nota de débito disponible en la
   factura y revisar el documento tipo `08` antes de publicarlo.

Qué decir: “El tipo de comprobante clasifica el sustento y el flujo Odoo genera
el efecto contable. La emisión electrónica ante SUNAT requiere un conector CPE.”

### Escena 3: compra y detracción

1. Ir a **Compras → Pedidos → Solicitudes de presupuesto**, crear o abrir una
   orden con proveedor, productos, cantidades y moneda, y confirmarla.
2. Abrir la **Recepción**, registrar dimensiones y lotes de planchas y validar.
   Si corresponde, agregar en la recepción **Costos adicionales** como flete,
   seguro o seguridad para preparar el costeo.
3. Desde el pedido usar **Crear factura**; revisar proveedor, moneda, IGV y
   clasificar la compra como mercadería, servicio, gasto o activo fijo.
4. En la factura abrir la pestaña **Control tributario**. Agregar una línea de
   tipo **Detracción**, indicar porcentaje, base, fecha y constancia. El importe
   se calcula automáticamente.
5. Cambiar a **Pagado** solamente después de realizar y comprobar el depósito.
6. Cerrar la escena en **Libros y SIRE** mostrando **Compras 8.1**, **Bancos
   1.2**, **Kardex 13.1** y **Existencias por almacén**.

Qué decir: “La detracción queda controlada contra el comprobante: base,
porcentaje, importe y constancia. El depósito bancario y su integración SUNAT
se activan cuando se implemente el conector tributario.”

Resultado: orden, recepción física, valorización/costeo, cuenta por pagar,
pago, registro de compras e incremento de existencias quedan relacionados.

### Escena 4: entregas y almacén

1. Ir a **Inventario → Operaciones → Entregas** y abrir la entrega creada por
   el pedido. Mostrar origen, destino, cliente, productos y lotes.
2. Ir a **Contabilidad → Reportes → Libros y SIRE**, seleccionar **Guías de
   remisión y entregas** y pulsar **Cargar vista previa**.

Importante: esta opción es un **listado interno de entregas y traslados** que
relaciona pedido, cliente, origen, destino y productos transportados. La **Guía
de Remisión Electrónica (GRE) SUNAT no existe en el sistema**: requiere XML,
firma digital, envío, CDR y representación impresa mediante un conector
autorizado. Presentarla siempre como control logístico del despacho, no como
documento tributario.

Qué decir: “Aquí está la trazabilidad física del despacho. Es una guía interna
de entrega; la GRE SUNAT requiere XML, firma digital, envío y CDR.”

### Escena 5: terceros y asiento manual

1. Ir a **Contabilidad → Contabilidad → Asientos contables → Nuevo**.
2. Elegir un diario misceláneo y, en el campo de cabecera, seleccionar el
   **Contacto / contraparte**. En las líneas se puede elegir un tercero distinto
   cuando la naturaleza del asiento lo requiera.
3. Registrar cuenta, glosa, Debe y Haber; comprobar que ambos totales cuadren y
   publicar solo después de revisión.
4. Para carga masiva ir a **Contabilidad → Contabilidad → Importar asientos**,
   descargar la plantilla y completar **Contacto o RUC** con un contacto ya
   creado. La importación crea borradores, nunca publica automáticamente.

Qué decir: “Todo asiento puede llevar su contraparte. En caja chica el
proveedor o beneficiario ahora se transfiere también al asiento generado.”

### Escena 6: caja chica y contacto

1. Ir a **Contabilidad → Contabilidad → Caja Chica** y abrir una caja.
2. En **Movimientos**, registrar fecha, proveedor o beneficiario, sustento,
   documento, cuenta de gasto e importe. Pulsar **Contabilizar**.
3. Abrir el vínculo del asiento creado y comprobar que el contacto aparece en
   la cabecera y en sus líneas.
4. Registrar el efectivo contado, confirmar arqueo y usar **Cerrar caja**;
   si hay gasto pendiente, usar **Reponer desde banco**.

### Escena 7: Libro Diario, Mayor y Balance

Hay dos niveles complementarios: **Contabilidad → Contabilidad → Transacciones
→ Asientos contables** abre la vista estándar de Odoo para entrar a un asiento
y revisar o modificar sus líneas según permiso y estado; **Contabilidad →
Reportes → Libros y SIRE** ofrece tablas preparadas para exposición y descarga.

1. En **Libros y SIRE**, elegir **Libro Diario clásico**, seleccionar el
   periodo y pulsar **Cargar vista previa**. Cada fila es un apunte real de
   `account.move.line`; las líneas de un mismo asiento quedan visualmente
   agrupadas y la última columna muestra la **Suma del asiento** (Debe y Haber
   deben ser iguales). Mostrar: contacto/contraparte, cuenta, glosa, Debe,
   Haber, impuesto aplicado, importe de impuesto, cuenta de impuesto y, si
   existe, detracción/constancia.
2. Explicar que el monto de IGV se muestra solo en la línea tributaria para no
   duplicarlo; la columna **Cuenta de impuesto** revela la cuenta PCGE de esa
   línea. El control de detracción vinculado al comprobante se presenta una vez
   al inicio del asiento con porcentaje, importe y constancia; no se inventa una
   línea Debe/Haber si todavía no existe el pago real. El Diario no presenta
   saldo acumulado porque ese dato es propio del Mayor.
3. Elegir **Libro Mayor clásico**, seleccionar opcionalmente una **Cuenta
   contable** y cargar la vista. La primera fila de cada cuenta es **Saldo
   anterior**; luego los movimientos se ordenan por fecha y asiento, con saldos
   siempre positivos en **Saldo deudor** o **Saldo acreedor**. La cabecera
   resume saldo anterior, Debe, Haber y saldo de cierre.
4. Elegir **Balance de Comprobación**, con las columnas **Saldos Iniciales
   (Deudor/Acreedor) | Movimientos (Debe/Haber) | Saldos Finales
   (Deudor/Acreedor)**, siempre como importes positivos (una cuenta de
   patrimonio acreedora aparece en positivo en la columna Acreedor). Para cada
   cuenta se controla que `saldo final = saldo inicial + debe - haber`.
5. Usar **Excel** o **PDF** para revisión y exposición. El botón **TXT PLE**
   genera un archivo plano de demostración estructurada con la nomenclatura de
   nombre PLE; no reproduce la estructura oficial de campos RVIE/RCE y no debe
   cargarse en SIRE.

Frases cortas según la pantalla:

- **Libro Diario clásico:** “Aquí vemos el origen de cada asiento: cuenta,
  glosa, impuestos, Debe y Haber. El total siempre queda cuadrado.”
- **Libro Mayor clásico:** “Si quiero entender una cuenta, aquí sigo cada
  movimiento y su saldo acumulado.”
- **Balance de Comprobación:** “Esta es la foto de control del periodo: suma
  movimientos, muestra saldos y permite validar el cierre contable.”
- **Kardex y almacén:** “El inventario no es una cifra estimada: se sustenta en
  entradas, entregas, lotes y ubicaciones.”
- **Ventas, compras y bancos:** “La información se conecta desde el documento
  comercial hasta el impacto financiero, sin doble registro.”

### Mensaje de cierre

> “El sistema conecta venta, compra, almacén, caja y contabilidad. Cada
> documento deja su asiento, tercero, cuentas e impuestos identificables; los
> libros permiten revisarlo por movimiento o por cuenta. Excel y PDF dan una
> salida clara para control. La última milla tributaria —CPE, GRE, validación
> PVSIRE, envío y CDR— se implementa con la configuración y credenciales reales
> de la empresa.”

## Catálogo de libros y formatos

En **Contabilidad → Reportes → Libros y SIRE** se elige un periodo, se genera
una vista previa y se descarga en **PDF**, **Excel** o **TXT referencial**.

| Selección | Fuente real en Odoo | Uso en la demostración |
|---|---|---|
| Registro de Ventas 14.1 / vista RVIE | Facturas y notas de crédito de clientes | Revisar cliente, RUC, documento, productos, cantidad, base, IGV y total |
| Registro de Compras 8.1 / vista RCE | Facturas y notas de crédito de proveedores domiciliados | Revisar proveedor, documento, cantidad, moneda, base, IGV y total |
| Registro de Compras 8.2 | Facturas de proveedores extranjeros | Mostrar la compra no domiciliada en moneda extranjera |
| Libro Caja y Bancos 1.1 | Líneas publicadas de diarios tipo Efectivo | Entradas, salidas y saldo de caja |
| Libro Caja y Bancos 1.2 | Líneas publicadas de diarios tipo Banco | Transferencias, cobros y pagos bancarios |
| Inventarios y Balances | Saldos de cuentas PCGE clases 1 a 5 | Resumen de revisión del cierre; no reemplaza todos los anexos 3.x |
| Activos Fijos 7.1 | Compras contabilizadas en cuentas 33 | Base para activo, costo y documento; la depreciación acumulada se muestra en 0.0 porque no hay motor de activos; vida útil y depreciación se completan antes de declarar |
| Kardex 13.1 | Movimientos realizados de inventario | Entradas, salidas, transferencias, cantidades y valores |
| Guías de remisión y entregas | Entregas y traslados internos | Listado interno del despacho: pedido, cliente, origen, destino y productos; no es GRE electrónica |
| Existencias por almacén | Quants actuales por almacén, ubicación y lote | Stock físico, reservado, disponible y valorizado |
| Libro Diario clásico | Apuntes de asientos publicados | Ver diario, asiento, cuenta, glosa, Debe, Haber y la suma cuadrada de cada asiento |
| Libro Mayor clásico | Apuntes agrupados por cuenta | Seguir el saldo anterior, movimientos y saldo acumulado de cada cuenta |
| Balance de Comprobación | Saldos iniciales, movimientos y saldos finales por cuenta | Cuadrar el periodo sin mostrar saldos con signo negativo |

### Aclaración de formatos

- **7.1** es Registro de Activos Fijos, no Inventarios y Balances. Al
  presentarlo, decir que la depreciación acumulada aparece en **0.0**: el
  sistema no tiene motor de activos y esos datos se aprueban contablemente.
- **8.1** es Registro de Compras para operaciones domiciliadas.
- **8.2** es Registro de Compras para operaciones con sujetos no domiciliados.
- **13.1** es Inventario Permanente Valorizado.
- **14.1** es Registro de Ventas e Ingresos.
- El Libro de Inventarios y Balances se divide en formatos **3.x**. La opción
  actual es un resumen contable de control, no todos los anexos oficiales.
- RCE y RVIE de SIRE usan las estructuras vigentes de archivos de reemplazo de
  SUNAT. No debe asumirse que un TXT 8.1 o 14.1 histórico se puede subir sin
  mapear y validar su versión actual.

## Qué significa cada descarga

### Excel

Es la mejor salida para revisar y demostrar. Contiene:

- hoja **Reporte** con filtros, datos y montos numéricos;
- hoja **Diccionario y estado** con las etapas del pipeline;
- fechas `dd/mm/aaaa`, encabezados en español y montos editables como números;
- advertencia visible de que es un borrador no presentado.

### PDF

Es la representación legible para entregar a gerencia o usar en la exposición.
Incluye empresa, RUC, periodo, detalle, cantidades y totales de control. En
Render funciona con `wkhtmltopdf`, incluido en la imagen oficial `odoo:19.0`.

### TXT referencial

Sirve para enseñar la composición y revisar el mapeo. Usa UTF-8 y separador
`|`. Para conservar el formato de archivo PLE, no incluye una fila de
encabezados:

```text
1|13/08/2026|01|F001|00000184|Canteras del Sur|6|20123456789|Mármol Carrara|12.50|USD|4000.00|720.00|4720.00|Publicado|OC00018
```

El TXT usa la nomenclatura PLE de 33 caracteres antes de la extensión, por
ejemplo `LE2020500600220260700080100001111.txt`, lo que permite demostrar el
flujo completo de generación. Su contenido es una **demostración
estructurada**: no reproduce la estructura oficial de campos RVIE/RCE y **no
debe cargarse en SIRE**; antes de cualquier uso oficial debe mapearse a la
estructura vigente y validarse con PVSIRE.

## Pipeline correcto de SIRE

```text
Factura/nota en Odoo
        ↓
Documento publicado + asiento balanceado
        ↓
Control de RUC, fecha, tipo, serie, moneda, base, IGV y total
        ↓
Excel/PDF de revisión + TXT referencial
        ↓
Mapeo al archivo de reemplazo vigente
        ↓
Validación con PVSIRE
        ↓
Comparar/complementar propuesta RCE o RVIE en SIRE
        ↓
Generar registro y guardar CDR/constancia
```

El sistema implementado llega hasta la preparación y revisión. Sin credenciales
SOL no acepta propuestas, no presenta declaraciones y no genera un CDR. La
constancia es la evidencia; descargar un Excel o TXT desde Odoo no equivale a
declarar.

Fuentes de consulta oficial:

- [SIRE](https://sire.sunat.gob.pe/)
- [Estructuras de archivos SIRE](https://cpe.sunat.gob.pe/estructura-de-archivos)
- [Programa Validador PVSIRE](https://cpe.sunat.gob.pe/programa-validador-sire-pvsire)
- [Libros electrónicos PLE](https://emprender.sunat.gob.pe/comprobantes-libros/registros-libros-electronicos/programa-libros-electronicos-ple)

## Casos precargados del seed

El seed versión 16 agrega, sin duplicar:

- **DEMO-8.2-NO-DOMICILIADO**: proveedor italiano, comprobante tipo 91, USD,
  cantidad 12.5 y monto USD 4,000;
- **DEMO-7.1-ACTIVO**: pulidora industrial registrada en cuenta 3361000 para
  mostrar la base del Registro de Activos Fijos. En el formato 7.1 la
  depreciación acumulada aparece en 0.0 (no hay motor de activos); el caso no
  inventa vida útil ni tasa de depreciación: esos datos deben aprobarse
  contablemente.

Ambos están identificados como Demo.

Convención del PCGE configurado: la cuenta **4211000** corresponde a
comprobantes por pagar *no emitidos / por recibir* y la **4212000** se muestra
como **Facturas, boletas y otros comprobantes por pagar - Emitidas**.

## Lista de control antes de mostrarlo

- Actualizar el módulo `pierinelli_reportes` después del despliegue.
- Esperar que el seed termine y confirme versión 16.
- Ingresar como `admin` o `contabilidad`.
- Elegir un periodo que incluya las operaciones de demostración.
- Generar primero la vista previa; después descargar.
- En local, instalar `wkhtmltopdf` si se desea probar el PDF. Excel y TXT no lo
  requieren. Render usa la imagen oficial que ya lo incluye.
- No decir “declarado” hasta tener CDR/constancia de SUNAT.

## Alcance tributario que no se debe prometer

- El TXT es demostración estructurada: no sigue la estructura oficial de campos
  RVIE/RCE y no debe cargarse en SIRE sin adaptar todos los campos y reglas
  vigentes de SUNAT, y validarlo con PVSIRE.
- No existe emisión de factura, boleta, nota, GRE ni detracción electrónica
  ante SUNAT/OSE; tampoco recepción de CDR. La opción "Guías de remisión y
  entregas" es un listado interno de despacho.
- La detracción actual es control operativo. No genera por sí sola el depósito
  al Banco de la Nación ni un asiento automático de pago.
