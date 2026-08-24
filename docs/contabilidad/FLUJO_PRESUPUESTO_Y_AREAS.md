# Flujo contable: presupuesto, áreas y ejecución

Guía para explicar el control por áreas o centros de costo en el entorno de
demostración. Los nombres de menús corresponden a los perfiles `admin` y
`contabilidad`.

## Idea central

El presupuesto **no es una cuenta bancaria ni una bolsa de dinero**. Es el
importe aprobado para una cuenta contable, una área y un período. El consumo
ocurre cuando se publica una factura o un asiento con la misma cuenta y la
misma distribución analítica.

```text
Presupuesto aprobado
        ↓
Orden de compra (compromiso, sin asiento)
        ↓
Recepción de material (movimiento físico)
        ↓
Factura de proveedor + área analítica
        ↓
Publicar factura (asiento y ejecución presupuestal)
        ↓
Pago por banco o caja (liquida la deuda; no duplica el gasto)
```

## 1. Mostrar las áreas existentes

1. Ingresar como `contabilidad` o `admin`.
2. Ir a **Contabilidad → Configuración → Áreas / Centros de Costo**.
3. Mostrar, por ejemplo, `AREA-MKT Marketing`, `AREA-OPE Operaciones y
   Almacén` o `AREA-PRO Producción y Cortes`.

Las áreas son dimensiones analíticas permanentes de la empresa. No son
cuentas de caja ni reemplazan el plan contable. Responden la pregunta: **¿qué
parte del negocio originó este ingreso o gasto?**

Si se requiere control específico de abastecimiento, crear el área
`AREA-CMP Compras / Abastecimiento` desde esa misma pantalla.

## 2. Crear un presupuesto por área

1. Ir a **Contabilidad → Presupuestos → Nuevo**.
2. Completar:
   - **Nombre:** `Presupuesto de Compras - 2026`.
   - **Inicio / fin:** el período que se desea controlar.
3. En las líneas agregar una o varias combinaciones de:
   - **Cuenta contable:** la cuenta que realmente se moverá al contabilizar.
   - **Área / centro de costo:** `Compras / Abastecimiento`.
   - **Presupuestado:** por ejemplo, `300,000.00`.
   - **Obra (opcional):** sólo si se quiere limitar el presupuesto a un
     proyecto concreto.
4. Pulsar **Aprobar**.

Para compras de inventario debe revisarse la cuenta que usa la configuración
contable del producto: puede ser una cuenta de inventario o una cuenta
transitoria de existencias. La línea presupuestal debe usar esa misma cuenta
para que el ejecutado sea consistente. Flete, seguro y otros gastos se pueden
controlar con líneas presupuestales separadas.

## 3. Ejecutar una compra sin duplicar el gasto

1. Ir a **Compras → Órdenes → Solicitudes de cotización** y crear la orden.
2. Confirmarla. La orden es un compromiso comercial; todavía no crea asiento
   ni consume presupuesto.
3. Abrir la recepción y validar el material si corresponde. En planchas, se
   registran las planchas recibidas y sus dimensiones.
4. Volver al pedido de compra y pulsar **Crear factura**.
5. En la factura de proveedor, revisar proveedor, fecha, moneda, cuenta y
   monto. En cada línea relevante completar **Distribución analítica** con
   `Compras / Abastecimiento: 100%`.
6. Pulsar **Publicar**. Ese es el punto en el que se crea el asiento y el
   presupuesto calcula su importe ejecutado.
7. Usar **Registrar pago** y escoger Banco o Caja cuando se realice el pago.
   El pago cancela la cuenta por pagar; no debe volver a incrementar el gasto
   del presupuesto.

Ejemplo de lectura: presupuesto S/ 300,000 y factura publicada por S/ 75,000
en la misma cuenta y área: **Ejecutado S/ 75,000**, **Saldo S/ 225,000** y
**25% consumido**.

## 4. Ver el resultado y sustento

- **Contabilidad → Presupuestos:** abrir el presupuesto. Cada línea muestra
  Presupuestado, Ejecutado, Saldo y porcentaje.
- **Contabilidad → Contabilidad → Apuntes analíticos:** filtrar o agrupar por
  **Áreas / Centros de Costo** para revisar cada movimiento que compone el
  importe.
- **Contabilidad → Reportes → Gestión → Reporte analítico:** usar vista pivote
  para cruzar área, cuenta y período; desde el ícono de gráfico se puede usar
  barras o líneas.
- **Contabilidad → Configuración → Áreas / Centros de Costo:** abrir un área
  y usar sus botones **Pedidos** o **Facturas** para consultar los documentos
  relacionados.

## 5. Área y obra: dos preguntas distintas

Una misma factura puede llevar ambas dimensiones:

- **Área:** Marketing, Operaciones, Compras, Producción. Responde: “¿quién
  consumió el recurso?”.
- **Obra / proyecto:** Condominio Trujillo, sala de exhibición, etc. Responde:
  “¿para qué proyecto se consumió?”.

Ejemplo: una factura de publicidad puede llevar `Marketing 100%` y
`Proyecto Showroom 100%`. Un presupuesto con ambos filtros sólo contabiliza
movimientos que tengan las dos dimensiones.

## Guion de un minuto

> “Primero definimos las áreas que queremos controlar. Aquí Compras tiene su
> propia dimensión analítica. Luego aprobamos un presupuesto de S/ 300 mil,
> asociado a la cuenta contable que se utilizará realmente. La orden de compra
> es un compromiso; el presupuesto se ejecuta recién al publicar la factura.
> En esa factura imputamos el gasto a Compras y el sistema compara en tiempo
> real presupuesto, ejecutado y saldo. Finalmente, el pago por banco liquida
> la deuda, pero no duplica el gasto. Así podemos ver quién consumió el dinero,
> en qué cuenta y en qué período.”

## Alcance actual

El sistema controla ejecución de documentos **publicados** y permite analizarla
por área, obra, cuenta y período. No bloquea todavía la confirmación de una
orden o factura que exceda el presupuesto: esa sería una futura regla de
control preventivo, no una limitación del registro contable.

