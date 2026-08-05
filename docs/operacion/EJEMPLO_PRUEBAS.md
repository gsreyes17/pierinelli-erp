# Ejemplo exacto: compra, corte, merma y asistente

Este caso sirve para probar el flujo completo sin usar datos reales. Las
unidades de largo y alto estan en metros; el espesor esta en centimetros.

## 1. Crear el material

1. Entre a **Inventario -> Productos -> Productos**.
2. Pulse **Nuevo**.
3. En **Nombre del producto**, escriba `Cuarcita Azul Prueba`.
4. En **Tipo de producto**, elija **Almacenable**.
5. En **Unidad de medida**, elija `m2`.
6. En la pestana de datos de Pierinelli, complete:
   - **Prefijo de plancha:** `CAP`.
   - **Tipo de material:** `Natural`.
   - **Precio de venta:** `450`.
7. Pulse **Guardar**.

## 2. Comprar y recibir cinco planchas

1. Abra **Compras -> Pedidos -> Solicitudes de presupuesto** y pulse **Nuevo**.
2. Seleccione cualquier proveedor de prueba.
3. En **Agregar un producto**, elija `Cuarcita Azul Prueba`.
4. En **Cantidad**, escriba `25`. Es el total en m2, no el numero de
   planchas.
5. En **Precio unitario**, escriba `250` y pulse **Confirmar pedido**.
6. Pulse el boton inteligente **Recepcion**.
7. Pulse **Registrar planchas recibidas**.
8. En la linea creada, complete exactamente:
   - **Producto de la recepcion:** `Cuarcita Azul Prueba`.
   - **Cantidad de planchas:** `5`.
   - **Largo:** `2.50`.
   - **Alto:** `2.00`.
   - **Espesor:** `2`.
   - **Ubicacion:** `Zona A - Rack 1`.
   - **Referencia de importacion:** `CONT-PRUEBA-01`.
9. Verifique que el total sea `25.00 m2`, pulse **Registrar planchas** y luego
   pulse **Validar** en la recepcion.
10. Abra **Inventario -> Planchas -> Operaciones**, busque `CAP` y abra la
    plancha `CAP0826.01` (el codigo usa el mes y anio de la recepcion). Cargue una foto
    individual en el campo de imagen y pulse **Guardar**.

## 3. Vender, cortar y registrar merma

1. Entre a **Ventas -> Pedidos -> Presupuestos** y pulse **Nuevo**.
2. Seleccione un cliente de prueba.
3. Agregue el producto `Cuarcita Azul Prueba`, con cantidad `3.00` m2.
4. En la misma linea, elija la plancha `CAP0826.01`, active **Requiere corte**
   y guarde.
5. Pulse **Confirmar** y luego **Crear Orden de Corte**.
6. En la pestana **Cortes**, pulse **Agregar una linea** e indique:
   - **Pieza:** `Encimera de prueba`.
   - **Cantidad:** `1`.
   - **Largo:** `2.00`.
   - **Alto:** `1.50`.
7. En **Retorno y merma**, complete **Retorno: largo** con `1.00` y
   **Retorno: alto** con `1.00`. El sistema mostrara `1.00 m2` de retorno y
   `1.00 m2` de merma.
8. En **Destino de la merma**, elija **Perdida del negocio**.
9. Pulse **Imprimir OP + Modulacion** si desea revisar el documento y, al
   terminar el corte fisico, pulse **Ejecutar corte** y confirme.

Resultado: la OP queda en **Hecho**, el retorno aparece como
`CAP0826.01.01` y la merma aparece en **Inventario -> Planchas -> Mermas**.

## 4. Reingresar una merma aprovechable

1. Entre a **Inventario -> Planchas -> Mermas**.
2. Abra la merma de `CAP0826.01` creada en el paso anterior.
3. Pulse **Reingresar** y confirme.
4. En la lista aparecera el enlace **Plancha de reingreso**. Abralo.

La nueva ficha tendra el codigo `CAP0826.01.02` si ya existe el retorno
`.01`; si no habia una hija anterior, sera `CAP0826.01.01`. Esto evita repetir
codigos. La ficha queda como **Pendiente de revision**: complete sus medidas
reales, cargue una foto si es natural y cambie **Aptitud comercial** a
**Vendible** o **Liquidacion** antes de ofrecerla.

## 5. Consultar el asistente de inventario (MCP inicial)

1. Abra **Inventario -> Planchas -> Asistente de Inventario (MCP)**.
2. En **Consulta**, seleccione una de estas tres preguntas:
   - **Que stock vendible hay actualmente?**
   - **Que reservas vencen hoy o ya vencieron?**
   - **Que planchas naturales no tienen foto?**
3. Pulse **Consultar**.

El resultado usa solo datos de Odoo y no modifica inventario. Esta es la base
segura para conectar posteriormente un chat con DeepSeek mediante MCP/API.
