# Áreas (centros de costo) y presupuesto por área

Cómo se crean y gestionan las áreas de la empresa, y cómo se reparte el
presupuesto entre ellas. Configurado y verificado el 21 de agosto de 2026.

---

## 1. Qué es un área aquí

Un **área** (o centro de costo) es una unidad de la empresa a la que se le
imputan gastos: Finanzas, Marketing, Tecnología, Comercial… Es una **etiqueta
con monto** que viaja pegada al asiento contable: no cambia el balance, pero
permite responder *"¿cuánto gastó Marketing este año?"*.

En el sistema son **cuentas analíticas** dentro del plan **"Áreas / Centros de
Costo"**, separado del plan "Obras / Proyectos". Estar en planes distintos es
lo que permite que **un mismo gasto lleve las dos etiquetas a la vez**:
*"publicidad de Marketing para la obra Condominio Trujillo"*.

## 2. Las áreas configuradas

`Contabilidad → Configuración → Áreas / Centros de Costo`

| Código | Área |
|---|---|
| AREA-FIN | Finanzas y Contabilidad |
| AREA-MKT | Marketing |
| AREA-TEC | Tecnología / Sistemas |
| AREA-COM | Comercial y Ventas |
| AREA-OPE | Operaciones y Almacén |
| AREA-PRO | Producción y Cortes |
| AREA-RRHH | Recursos Humanos |
| AREA-GER | Gerencia General |

## 3. Crear o modificar un área

1. Ve a **Contabilidad → Configuración → Áreas / Centros de Costo**.
2. Pulsa **Nuevo** — la lista es editable, escribes directo en la fila.
3. Completa **Código** (ej. `AREA-LOG`) y **Área** (ej. `Logística`).
4. Guarda. Ya está disponible en presupuestos y en la distribución analítica.

> No hace falta tocar "planes analíticos": esta pantalla ya filtra y asigna el
> plan de Áreas automáticamente.

## 4. Imputar un gasto a un área

En cualquier línea de factura de proveedor, asiento manual o gasto de caja
chica, usa el campo **Distribución analítica**:

- `Marketing 100%` — todo el gasto es del área.
- `Marketing 60% · Comercial 40%` — se reparte entre dos áreas.
- `Marketing 100%` **y** `Condominio Trujillo 100%` — el gasto es de Marketing
  *y* de esa obra (una cuenta de cada plan).

## 5. Repartir el presupuesto por área

`Contabilidad → Presupuestos` → **Nuevo**

1. Nombre y período (ej. *Presupuesto por Áreas 2026*, del 01-ene al 31-dic).
2. Una línea por área: **Cuenta contable** (la de gasto), **Área**, y el
   **monto presupuestado**. Deja *Obra* vacío si el presupuesto es del área
   completa.
3. **Aprobar**.

El sistema compara solo contra los gastos **contabilizados** de esa cuenta
imputados a esa área. Si además pones una obra, la línea cuenta únicamente lo
que lleva **ambas** etiquetas.

### El ejemplo cargado en la base

**Presupuesto por Áreas 2026** — S/ 510,000 repartidos, con gasto real
imputado a cada área:

| Área | Presupuesto | Ejecutado | Saldo | % |
|---|---:|---:|---:|---:|
| Comercial y Ventas | 120,000 | 31,500 | 88,500 | 26.2% |
| Operaciones y Almacén | 90,000 | 24,800 | 65,200 | 27.6% |
| Marketing | 72,000 | 18,400 | 53,600 | 25.6% |
| Producción y Cortes | 60,000 | 13,900 | 46,100 | 23.2% |
| Recursos Humanos | 54,000 | 11,200 | 42,800 | 20.7% |
| Finanzas y Contabilidad | 48,000 | 9,200 | 38,800 | 19.2% |
| Tecnología / Sistemas | 36,000 | 7,600 | 28,400 | 21.1% |
| Gerencia General | 30,000 | 5,400 | 24,600 | 18.0% |
| **TOTAL** | **510,000** | **122,000** | | |

## 6. Ver el gasto por área

- **Presupuesto vs ejecutado:** el propio presupuesto, columna por columna.
- **Detalle de movimientos:** `Contabilidad → Contabilidad → Apuntes
  analíticos`, agrupando por la columna *Áreas / Centros de Costo*.
- **Consolidado:** `Contabilidad → Reportes → Gestión → Reporte analítico`
  (vista pivote) — cruza área contra período o contra obra.
- **Desde el área:** abre el área y usa sus botones **Pedidos** y **Facturas**
  para ver los documentos que la llevan.

## 7. Áreas vs obras: cuándo usar cada una

| | Área | Obra / proyecto |
|---|---|---|
| Responde | ¿Qué departamento gastó? | ¿De qué proyecto fue? |
| Vive | Todo el año, es fija | Empieza y termina |
| Ejemplo | Marketing, Tecnología | Condominio Trujillo |
| Se usa para | Presupuesto anual, control de gasto | Rentabilidad del proyecto |

Se pueden combinar libremente — es justo la ventaja de tenerlas en planes
separados.

---

*Roles y permisos: [USUARIOS_Y_PERMISOS.md](USUARIOS_Y_PERMISOS.md)*
