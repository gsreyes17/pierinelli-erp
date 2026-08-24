# Usuarios, roles y permisos

Guía del administrador: **qué ve cada puesto**, cómo se crea un usuario nuevo y
cómo se le asignan permisos. Actualizado el 21 de agosto de 2026, con la matriz
verificada en el sistema.

---

## 1. La matriz de roles

Cada puesto es una combinación de permisos. Estos son los roles configurados,
con el usuario de ejemplo que puedes usar para mostrarlos (contraseña
`pierinelli` en todos).

| Puesto | Usuario demo | Qué apps ve | Qué NO puede |
|---|---|---|---|
| **Gerente General** | `gerente` | Ventas, Inventario, Compras, Contabilidad (todo como administrador) | — (ve costos y márgenes) |
| **Dueño** | `jorge@pierinelli.com` | Igual que gerencia | — |
| **Contadora** | `contabilidad` | Contabilidad completa: asientos, cierres, libros, presupuestos, caja chica | Confirmar ventas, tocar inventario |
| **Asistente contable** | `rosa@pierinelli.com` | Contabilidad de registro: facturas, asientos, controles tributarios | **Aprobar cierres** ni bloquear períodos |
| **Vendedor** | `vendedor`, `valeria@`, `diego@` | Ventas: sus propias cotizaciones y pedidos, catálogo, Vista Comercial de planchas | Ver **costos**, contabilidad, ni pedidos de otros vendedores |
| **Jefe de almacén** | `almacen` | Inventario completo: recepciones, traslados, ajustes, lotes, multi-ubicación | Ventas ni contabilidad |
| **Almacenero** | `carlos@pierinelli.com` | Inventario operativo: recepciones, entregas, planchas | Ajustes de configuración de almacén |
| **Comprador** | `compras` | Compras, proveedores, recepciones | Ventas ni contabilidad |
| **Maestro de producción** | `aquino@pierinelli.com` | Inventario + Fabricación: órdenes de corte | Ventas ni contabilidad |

> **La diferencia que más importa comercialmente:** el vendedor **no ve costos
> ni el kardex valorizado**. Puede vender y reservar planchas, pero el margen
> es información de gerencia. Muéstralo entrando como `vendedor`.

## 2. Crear un usuario nuevo

1. Activa el **modo desarrollador** solo si vas a tocar permisos finos:
   **Ajustes → General → Herramientas de desarrollador → Activar**. Para el
   alta normal no hace falta.
2. Ve a **Ajustes → Usuarios y compañías → Usuarios** → **Nuevo**.
3. Completa: **nombre**, **correo electrónico** (será su usuario de acceso) e
   idioma **Español (PE)**.
4. En la pestaña **Permisos de acceso**, marca los grupos de su puesto
   (siguiente sección).
5. **Guardar**. Odoo envía un correo de invitación; si no hay servidor de
   correo configurado, usa **Acciones → Cambiar contraseña** para asignarle una
   directamente.

> **Tip:** el atajo más seguro es duplicar. Abre un usuario del mismo puesto,
> **Acciones → Duplicar**, y cambia nombre y correo: los permisos vienen ya
> puestos y no se te olvida ninguno.

## 3. Asignar permisos: qué marcar según el puesto

En la pestaña **Permisos de acceso**, cada aplicación tiene un desplegable con
niveles. Estos son los que usa Pierinelli:

| Aplicación | Nivel | Significado |
|---|---|---|
| **Ventas** | *Usuario: solo mostrar documentos propios* | Ve solo sus cotizaciones — el vendedor |
| | *Usuario: mostrar todos los documentos* | Ve las de todo el equipo — jefe comercial |
| | *Administrador* | Además configura listas de precios y equipos |
| **Inventario** | *Usuario* | Opera recepciones, entregas, planchas |
| | *Administrador* | Además ajustes, almacenes, reglas |
| **Contabilidad** | *Usuario* | Registra facturas y asientos |
| | *Administrador* | Además **cierres de período**, plan contable, configuración |
| **Compras** | *Usuario* / *Administrador* | Órdenes de compra / configuración |
| **Fabricación** | *Usuario* | Órdenes de producción y corte |

Y dos casillas sueltas que conviene conocer:

- **Contabilidad analítica** — necesaria para ver y usar **áreas y obras**. Va
  a contabilidad y gerencia.
- **Gestionar números de lote y de serie** — necesaria para operar planchas.
  Va a inventario y producción.
- **Gestionar múltiples ubicaciones** — para traslados entre sedes. Jefe de
  almacén.

## 4. Verificar qué ve realmente un usuario

La forma honesta de comprobarlo, sin adivinar:

1. Entra en una ventana de incógnito con ese usuario.
2. Mira el **menú de aplicaciones**: solo aparecen las suyas.
3. Abre una plancha: si es vendedor, **la columna de costo no está**.

Para revisar sin cambiar de sesión: **Ajustes → Usuarios**, abre el usuario y
usa el botón **Registro de acceso** / revisa su pestaña de permisos.

## 5. Reglas de la casa (por qué está así)

- **Nadie opera con `admin` en el día a día.** `admin` es para configurar; la
  operación va con el usuario de cada persona, para que el sistema registre
  quién hizo qué (cada documento guarda su autor y su historial).
- **Los cierres contables solo los aplica el responsable contable**
  (Contabilidad / Administrador). El asistente registra, no bloquea períodos.
- **Los permisos se agregan, no se quitan a mano.** Si alguien necesita algo
  puntual, mejor añadirle el grupo que corresponde que darle administrador.
- **Al crear la base desde cero**, el `seed_pe.py` deja esta matriz aplicada; y
  si la base ya existía con permisos incompletos, los completa al re-ejecutarse
  (nunca quita los concedidos a mano).

---

*Áreas y centros de costo:
[ÁREAS_Y_PRESUPUESTO.md](AREAS_Y_PRESUPUESTO.md) · demo por requisito:
[../contabilidad/DATOS_DEMO_POR_REQUISITO.md](../contabilidad/DATOS_DEMO_POR_REQUISITO.md)*
