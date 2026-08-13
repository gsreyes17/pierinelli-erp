# Guía de demostración: guías, almacén, libros y SIRE

## 1. Qué quedó disponible

Ir a **Contabilidad → Reportes → Libros y SIRE**. El centro permite elegir un
periodo, generar una vista previa y descargarla en **PDF**, **Excel** o **TXT
referencial**.

| Selección | Fuente real en Odoo | Uso en la demostración |
|---|---|---|
| Registro de Ventas 14.1 / vista RVIE | Facturas y notas de crédito de clientes | Revisar cliente, RUC, documento, productos, cantidad, base, IGV y total |
| Registro de Compras 8.1 / vista RCE | Facturas y notas de crédito de proveedores domiciliados | Revisar proveedor, documento, cantidad, moneda, base, IGV y total |
| Registro de Compras 8.2 | Facturas de proveedores extranjeros | Mostrar la compra no domiciliada en moneda extranjera |
| Libro Caja y Bancos 1.1 | Líneas publicadas de diarios tipo Efectivo | Entradas, salidas y saldo de caja |
| Libro Caja y Bancos 1.2 | Líneas publicadas de diarios tipo Banco | Transferencias, cobros y pagos bancarios |
| Inventarios y Balances | Saldos de cuentas PCGE clases 1 a 5 | Resumen de revisión del cierre; no reemplaza todos los anexos 3.x |
| Activos Fijos 7.1 | Compras contabilizadas en cuentas 33 | Base para activo, costo y documento; vida útil y depreciación se completan antes de declarar |
| Kardex 13.1 | Movimientos realizados de inventario | Entradas, salidas, transferencias, cantidades y valores |
| Guías de remisión y entregas | Entregas y traslados internos | Relacionar pedido, cliente, origen, destino y productos transportados |
| Existencias por almacén | Quants actuales por almacén, ubicación y lote | Stock físico, reservado, disponible y valorizado |
| Libro Diario clásico | Apuntes de asientos publicados | Ver diario, asiento, cuenta, glosa, Debe, Haber y la suma cuadrada de cada asiento |
| Libro Mayor clásico | Apuntes agrupados por cuenta | Seguir el saldo anterior, movimientos y saldo acumulado de cada cuenta |
| Balance de Comprobación | Saldos iniciales, movimientos y saldos finales por cuenta | Cuadrar el periodo sin mostrar saldos con signo negativo |

## Vista clásica de asientos

Hay dos niveles complementarios:

1. **Contabilidad → Contabilidad → Transacciones → Asientos contables** abre
   la vista estándar de Odoo para entrar a un asiento, modificarlo si el permiso
   y el estado lo permiten, y revisar sus líneas.
2. **Contabilidad → Reportes → Libros y SIRE** permite elegir **Libro Diario
   clásico**, **Libro Mayor clásico** o **Balance de Comprobación** para una
   tabla preparada para exposición y descarga Excel/PDF/TXT.

En Diario cada fila es un apunte real de `account.move.line`. Las líneas de un
mismo asiento quedan visualmente agrupadas, y la última columna muestra la
**Suma del asiento**: Debe y Haber deben ser iguales. El Diario no presenta un
saldo acumulado porque ese es un dato propio del Mayor.

Además, el Diario muestra **Contacto / contraparte** cuando el asiento lo tiene,
la tasa o nombre del impuesto y el **importe monetario** solo en la línea de
impuesto que generó Odoo. La columna **Cuenta de impuesto** identifica la cuenta
PCGE usada por esa línea. Cuando existe un control de detracción vinculado al
comprobante, se presenta una vez al inicio del asiento con porcentaje, importe
y constancia; no se inventa una línea Debe/Haber si todavía no existe el pago o
asiento real de detracción.

En Mayor, seleccionar opcionalmente una **Cuenta contable** antes de cargar la
vista. La primera fila de cada cuenta es **Saldo anterior**; luego los
movimientos se ordenan por fecha y asiento. Los saldos se muestran como importes
positivos en **Saldo deudor** o **Saldo acreedor**, según corresponda. La
cabecera resume saldo anterior, Debe, Haber y saldo de cierre de la cuenta
elegida.

El Balance de Comprobación usa las columnas estándar: **Saldos Iniciales
(Deudor/Acreedor) | Movimientos (Debe/Haber) | Saldos Finales
(Deudor/Acreedor)**. No se muestran saldos negativos: por ejemplo, una cuenta
de patrimonio con naturaleza acreedora aparece con un importe positivo en la
columna Acreedor. Para cada cuenta se controla que `saldo final = saldo inicial
+ debe - haber`.

En el PCGE configurado, la cuenta **4211000** corresponde a comprobantes por
pagar *no emitidos / por recibir* y la **4212000** se muestra como
**Facturas, boletas y otros comprobantes por pagar - Emitidas**.

### Aclaración de formatos

- **7.1** es Registro de Activos Fijos, no Inventarios y Balances.
- **8.1** es Registro de Compras para operaciones domiciliadas.
- **8.2** es Registro de Compras para operaciones con sujetos no domiciliados.
- **13.1** es Inventario Permanente Valorizado.
- **14.1** es Registro de Ventas e Ingresos.
- El Libro de Inventarios y Balances se divide en formatos **3.x**. La opción
  actual es un resumen contable de control, no todos los anexos oficiales.
- RCE y RVIE de SIRE usan las estructuras vigentes de archivos de reemplazo de
  SUNAT. No debe asumirse que un TXT 8.1 o 14.1 histórico se puede subir sin
  mapear y validar su versión actual.

## 2. Qué significa cada descarga

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

Ejemplo conceptual:

El TXT usa la nomenclatura PLE de 33 caracteres antes de la extensión, por
ejemplo `LE2020500600220260700080100001111.txt`. Esto permite demostrar el
flujo completo de generación. Su contenido sigue siendo de demostración: antes
de usarlo en un proceso oficial se valida contra la estructura vigente y los
catálogos aplicables de SUNAT.

## 3. Pipeline correcto de SIRE

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

## 4. Puesta en escena de un negocio real

### Parte A: cerrar una venta

1. Ir a **Ventas → Pedidos → Cotizaciones → Nuevo**.
2. Elegir un cliente con RUC, agregar el material, cantidad, precio y confirmar.
3. Abrir el pedido confirmado y pulsar la operación de **Entrega**.
4. En la entrega comprobar cliente, almacén de origen, productos, lotes y
   cantidades. Pulsar **Validar**.
5. Esta operación pasa a **Inventario → Operaciones → Entregas** y alimenta la
   opción **Guías de remisión y entregas** del centro.
6. Volver al pedido y pulsar **Crear factura**. Revisar tipo de comprobante,
   RUC, fecha, moneda, base e IGV; pulsar **Confirmar**.
7. En la factura pulsar **Registrar pago**, elegir Banco o Efectivo, confirmar
   y comprobar que la factura quede pagada.
8. Ir a **Contabilidad → Reportes → Libros y SIRE**:
   - seleccionar **Registro de Ventas 14.1 / vista RVIE** y generar vista;
   - seleccionar **Libro Caja y Bancos 1.2** si se pagó por transferencia;
   - seleccionar **Guías de remisión y entregas**;
   - seleccionar **Kardex 13.1** o **Existencias por almacén**.

Resultado que se debe explicar: una venta produjo pedido, salida de almacén,
trazabilidad logística, factura, asiento, pago, movimiento bancario, registro de
ventas y disminución de existencias.

> La entrega de Odoo y su PDF interno sirven para controlar el despacho. No son
> todavía una **Guía de Remisión Electrónica SUNAT**. La GRE real requiere XML,
> firma, envío, CDR y representación impresa mediante un conector autorizado.

### Parte B: cerrar una compra

1. Ir a **Compras → Pedidos → Solicitudes de presupuesto → Nuevo**.
2. Elegir proveedor, productos, cantidades y moneda; confirmar el pedido.
3. Abrir **Recepción**, registrar dimensiones/lotes de planchas y validar.
4. Si corresponde, en la recepción agregar **Costos adicionales** como flete,
   seguro o seguridad y preparar el costeo.
5. Volver al pedido, crear la factura, revisar IGV y confirmar.
6. Registrar el pago desde la factura.
7. Ir a **Contabilidad → Reportes → Libros y SIRE** y enseñar:
   **Compras 8.1**, **Bancos 1.2**, **Kardex 13.1** y **Existencias por almacén**.

Resultado: orden, recepción física, valorización/costeo, cuenta por pagar, pago,
registro de compras e incremento de existencias quedan relacionados.

## 5. Casos de demostración precargados

El seed versión 16 agrega, sin duplicar:

- **DEMO-8.2-NO-DOMICILIADO**: proveedor italiano, comprobante tipo 91, USD,
  cantidad 12.5 y monto USD 4,000;
- **DEMO-7.1-ACTIVO**: pulidora industrial registrada en cuenta 3361000 para
  mostrar la base del Registro de Activos Fijos.

Ambos están identificados como Demo. El caso 7.1 no inventa automáticamente
vida útil ni tasa de depreciación: esos datos deben aprobarse contablemente.

## 6. Guion breve de exposición

> “No estamos viendo reportes aislados: estamos viendo una misma operación
> recorriendo toda la empresa. La venta genera la entrega; la entrega actualiza
> almacén y Kardex; la factura genera el asiento; el cobro queda en Banco; y el
> resultado aparece en Ventas, Caja y Bancos, Mayor y Balance de Comprobación.
> Esto permite que gerencia, ventas, almacén y contabilidad consulten la misma
> información, sin volver a digitarla ni depender de archivos separados.
>
> En esta pantalla se puede revisar la operación al detalle y descargarla en
> Excel o PDF para análisis y control. El sistema ya deja ordenada la información
> para la siguiente etapa tributaria, que se habilita con la configuración y
> validación formal de producción.”

### Frases cortas según la pantalla

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

## 7. Lista de control antes de mostrarlo

- Actualizar el módulo `pierinelli_reportes` después del despliegue.
- Esperar que el seed termine y confirme versión 16.
- Ingresar como `admin` o `contabilidad`.
- Elegir un periodo que incluya las operaciones de demostración.
- Generar primero la vista previa; después descargar.
- En local, instalar `wkhtmltopdf` si se desea probar el PDF. Excel y TXT no lo
  requieren. Render usa la imagen oficial que ya lo incluye.
- No decir “declarado” hasta tener CDR/constancia de SUNAT.
