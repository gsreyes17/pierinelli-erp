# Guía de los 20 puntos de contabilidad solicitados

Documento práctico basado en los puntos 1 al 20 de `verificacion_cliente.md`. Las rutas se indican para el usuario **Administrador**; el usuario **contabilidad** tiene acceso operativo, pero la configuración sensible y los cierres se reservan al responsable/Administrador.

Leyenda:

- **Operativo:** se puede realizar en el ERP actual.
- **Con configuración:** funciona cuando el contador aprueba cuentas, diarios o reglas.
- **Pendiente de integración:** requiere SUNAT/OSE/PSE, una API o un desarrollo adicional; no debe prometerse como activo todavía.

## 1. Plan de cuentas, reportes y diferencia de cambio

**Estado: Operativo con configuración.**

1. Entre a **Contabilidad → Configuración → Contabilidad → Plan de cuentas**.
2. Pulse **Nuevo** para una cuenta o abra una existente para modificarla.
3. Complete código, nombre, tipo de cuenta y opciones de conciliación según el PCGE aprobado.
4. Para reportes, vaya a **Contabilidad → Reportes** y elija Balance, Estado de resultados, Mayor o Balance de comprobación. Los reportes usan la clasificación/tipo de las cuentas y los saldos contabilizados.
5. Para diferencia de cambio, el contador debe revisar las cuentas de ganancia y pérdida cambiaria en la configuración contable y probar un pago PEN de una factura USD antes de operar en producción.

No se debe cambiar cuentas ya usadas sin criterio contable ni borrar cuentas con movimientos.

## 2. Centros de costo y dimensiones

**Estado: Operativo mediante analítica.**

1. Entre a **Contabilidad → Configuración → Dimensiones Analíticas**.
2. Cree un plan para cada dimensión requerida: `Área`, `Subárea`, `Proyecto`, `Sucursal` o `Presupuesto`.
3. Dentro de cada plan cree las cuentas analíticas, por ejemplo: Área Comercial, Área Operaciones, Proyecto Obra A o Sucursal Lima.
4. Al registrar una factura o asiento, distribuya la línea contable entre las dimensiones correspondientes.
5. Para presupuestar por centro de costo, vaya a **Contabilidad → Presupuestos → Nuevo**, agregue cuenta, centro de costo e importe; luego pulse **Aprobar**.

El presupuesto toma únicamente la parte efectivamente distribuida al centro de costo indicado.

## 3. Tipos de comprobante y planilla de movilidad

**Estado: Operativo.**

1. Entre a **Contabilidad → Configuración → Tipos de Comprobantes**.
2. Revise los tipos iniciales: Factura, Boleta, Nota de crédito, Nota de débito, Recibo por honorarios, DAM/Importación y `PM · Planilla de movilidad`.
3. Pulse **Nuevo** si necesita uno adicional; indique código, alcance, si requiere RUC y si permite crédito fiscal según el contador.
4. En una factura, use el bloque **Control interno → Tipo de comprobante**.
5. En **Caja Chica → Movimientos**, use **Tipo de sustento**. Para una planilla de movilidad seleccione `PM · Planilla de movilidad`.

El tipo es un control interno: no sustituye una validación o emisión electrónica SUNAT.

## 4. Tipo de cambio SUNAT y tipo de cambio corporativo/caja

**Estado: Operativo.**

1. Como Administrador, vaya a **Contabilidad → Configuración → Tipos de Cambio**.
2. Para traer la última tasa pública, pulse **Actualizar desde SUNAT → Consultar SUNAT**.
3. El sistema crea o actualiza la tasa con origen **SUNAT** y conserva una tasa del mismo día que haya sido ingresada manualmente.
4. Para la tasa propia de caja/corporativa, pulse **Nuevo**, elija origen **Corporativa**, fecha, compra y venta.
5. En una factura USD en borrador, abra el bloque **Tipo de cambio** y elija SUNAT venta, SUNAT compra, Corporativa o Manual.

La actualización diaria automática está disponible pero desactivada por seguridad hasta comprobar el botón desde Render: **Ajustes → Técnico → Automatización → Acciones planificadas → SUNAT: actualizar tipo de cambio**.

## 5. Guías de remisión electrónica y estado SUNAT

**Estado: Pendiente de integración.**

El ERP controla entregas y transferencias en **Inventario → Operaciones → Entregas / Transferencias**, pero todavía no emite una GRE electrónica ni consulta su CDR/estado en SUNAT.

Para activarlo se requiere una fase de integración: RUC, Clave SOL secundaria, certificado digital, series por sucursal, XML UBL, firma, envío, CDR y trazabilidad. Consulte [SUNAT_PRUEBAS.md](SUNAT_PRUEBAS.md).

## 6. Asientos tipo recurrentes

**Estado: Operativo.**

1. Entre a **Contabilidad → Contabilidad → Plantillas de Asientos**.
2. Pulse **Nuevo**, complete nombre, diario y descripción.
3. En líneas, agregue cuenta, glosa, Debe/Haber y monto fijo o porcentaje del importe base.
4. Pulse **Generar asiento**, indique fecha, referencia e importe base.
5. Revise el borrador generado y publíquelo cuando cuadre y sea aprobado.

Úselo para provisiones, planillas, depreciación manual, seguros, destinos u otros procesos repetitivos.

## 7. Asientos manuales y provisiones mensuales

**Estado: Operativo.**

1. Abra **Contabilidad → Contabilidad → Asientos contables → Nuevo**.
2. Elija diario general, fecha y referencia.
3. Agregue líneas; el total Debe debe ser igual al total Haber.
4. En **Control interno**, seleccione **Tipo de operación: Provisión** si corresponde.
5. Pulse **Publicar** solo después de la revisión contable.

Para una provisión recurrente es preferible crear antes una plantilla del punto 6.

## 8. Asientos de destino, clase 6 y clase 9

**Estado: Operativo con diseño contable.**

1. El contador define el mapa exacto de cuentas: origen clase 6, destino clase 9, centro de costo, criterio y periodicidad.
2. Cree una plantilla en **Contabilidad → Contabilidad → Plantillas de Asientos** con las cuentas aprobadas.
3. Genere el borrador mensual desde la plantilla, revise la distribución analítica y publique.

No se automatiza una regla universal 6→9 porque depende de la política de costos de la empresa; la plantilla evita repetir el asiento y conserva el control de aprobación.

## 9. Libros SIRE y cruce SUNAT

**Estado: Pendiente de integración.**

Los reportes internos están disponibles, pero no se ha conectado la API SIRE ni se envían/aceptan propuestas en SUNAT. SIRE usa OAuth 2.0 y credenciales API generadas en SOL.

Mientras tanto, use **Contabilidad → Reportes** para control interno y compare manualmente con SOL. La integración requiere credenciales, decisión del contador y pruebas por periodo.

## 10. Libros PRICO, régimen general y contabilidad completa

**Estado: Operativo como reportes internos; electrónico oficial pendiente.**

1. Vaya a **Contabilidad → Reportes**.
2. Seleccione el reporte: Libro Diario, Libro Mayor, Balance de comprobación, Situación financiera, Resultados, Flujo de efectivo, antigüedad CxC/CxP o resumen IGV.
3. Ingrese el rango de fechas y genere el PDF/resultado.

El ERP no genera todavía los archivos oficiales PLE/SIRE ni el Registro de Activos Fijos o Registro de Costos electrónico oficial. Esos son proyectos de localización/integración adicionales.

## 11. Reportes de gastos por dimensiones

**Estado: Operativo con uso disciplinado de analítica.**

1. Al contabilizar compra, caja o asiento, distribuya cada gasto por Área/Proyecto/Sucursal según corresponda.
2. Abra **Contabilidad → Reportes → Reporte analítico** para revisar movimientos por dimensión.
3. Para comparar gasto contra presupuesto, abra **Contabilidad → Presupuestos**, ingrese al período y revise ejecutado, saldo y porcentaje en las líneas.

Sin distribución analítica en la línea, un gasto no se puede atribuir correctamente a una dimensión.

## 12. Contabilidad PEN y reportes PEN/USD

**Estado: Operativo con configuración.**

1. Mantenga PEN como moneda de la compañía en **Contabilidad → Configuración → Monedas**.
2. Active USD y configure sus tasas mediante el punto 4.
3. Emita compras y ventas USD eligiendo la moneda en el documento.
4. En informes, use los importes en PEN como base contable; los importes de moneda extranjera se consultan desde cada documento y sus líneas.

La presentación consolidada de todos los reportes financieros en USD no está automatizada como reporte oficial; debe definirse la tasa y metodología de conversión con el contador.

## 13. Traslado entre sucursales con costos de transporte

**Estado: Operativo.**

1. Abra **Inventario → Operaciones → Transferencias** y cree/valide el traslado entre ubicaciones o sucursales.
2. Abra la transferencia validada y vaya a la pestaña **Costos adicionales**.
3. Agregue Flete, Seguridad, Seguro, Maniobra u Otro, con su importe y detalle.
4. Pulse **Preparar costeo**, revise el costo en destino creado, pulse **Calcular** y luego **Validar**.

Esto añade el costo al valor del inventario cuando los productos/configuración de valoración sean compatibles.

## 14. Rotura, diferencias y reclamos al seguro

**Estado: Operativo base; cuentas y asientos por aprobar.**

1. Registre el ajuste físico en **Inventario → Operaciones → Ajustes de inventario** o use el flujo de merma/corte cuando corresponda.
2. Identifique claramente el motivo en la referencia o glosa: rotura, diferencia, reclamo al seguro, etc.
3. Cuando el contador apruebe las cuentas, use una plantilla en **Contabilidad → Contabilidad → Plantillas de Asientos** para el asiento de rotura, pérdida o reclamo.
4. Genere, revise y publique el asiento.

Las cuentas de inventario, pérdida y recupero/seguro deben ser definidas por el contador antes de contabilizar un caso real.

## 15. Importar, exportar, predeterminar, duplicar, anular y eliminar asientos

**Estado: Operativo, con control contable.**

1. Abra **Contabilidad → Contabilidad → Asientos contables**.
2. Para una carga segura, pulse **Plantilla Excel**, descargue el archivo y lea la hoja **Instrucciones**. Elimine las filas grises de ejemplo y complete una línea por apunte.
3. Pulse **Importar asientos**, suba el Excel y elija **Validar e importar**. El sistema verifica antes los encabezados, diarios, cuentas, fechas y el cuadre de cada referencia; solo crea borradores.
4. Para la importación genérica o para exportar, use el menú de acciones de la lista y seleccione **Importar registros** / **Exportar**.
5. Para predeterminados, use **Plantillas de Asientos** (punto 6).
6. Para duplicar un borrador, use **Acción → Duplicar** en el formulario.
7. Un borrador se puede cancelar/eliminar según permisos. Un asiento publicado no se borra: se corrige con un asiento de reversión o una nota de crédito.

Pruebe importaciones en una copia de la base antes de cargar información real en volumen.

## 16. Reportes de guías/facturas y costos de servicios

**Estado: Parcial.**

- Entregas y transferencias: **Inventario → Operaciones → Entregas / Transferencias**. Use filtros por fecha, cliente, estado u origen para identificar entregas facturadas o pendientes.
- Facturas: **Contabilidad → Clientes → Facturas**; filtre por estado, fecha, cliente y referencia de pedido/entrega.
- Costos de servicios: clasifique las facturas de proveedor como **Servicios** en **Control interno** y use cuentas/dimensiones para analizarlos.

No existe aún un reporte único y automático que cruce guía facturada, factura despachada, servicio realizado y costo diferido. Para construirlo correctamente se debe definir qué campos, fechas y cuentas determinan cada concepto.

## 17. Cierres mensuales y anuales

**Estado: Operativo.**

1. Como Administrador o responsable, complete conciliaciones, caja, impuestos, provisiones y revisiones.
2. Entre a **Contabilidad → Contabilidad → Cierres Contables → Nuevo**.
3. Indique nombre, tipo de cierre (Contable, Tributario o Ventas), fecha a bloquear y el sustento.
4. Pulse **Aplicar bloqueo**.
5. El sistema impide registrar o modificar documentos en el período bloqueado según el tipo elegido.

La opción **Revertir bloqueo** es excepcional, solo para responsable/Administrador, y queda registrada.

## 18. Balance de comprobación según SUNAT

**Estado: Operativo como formato interno.**

1. Abra **Contabilidad → Reportes → Balance de comprobación**.
2. Indique la fecha/rango solicitado y genere el reporte.
3. Revise sumas, saldos y que no existan borradores que alteren la lectura.

El reporte es útil para control y revisión contable. La generación/presentación del archivo oficial requerido por SUNAT sigue pendiente de la definición PLE/SIRE aplicable.

## 19. Asientos de cierre y apertura anual

**Estado: Operativo manual con plantilla; automatización pendiente.**

1. El contador determina cuentas de resultado, patrimonio y saldos de apertura.
2. Cree una plantilla en **Contabilidad → Contabilidad → Plantillas de Asientos**, por ejemplo `Cierre anual 2026` o `Apertura 2027`.
3. Genere el asiento en borrador, revise cada línea y publíquelo.
4. Aplique el cierre de período del punto 17 una vez aprobados los asientos.

No se debe automatizar el cierre anual sin revisar resultados acumulados, impuestos, ajustes y el criterio contable del ejercicio.

## 20. Niveles de usuario y control de ingreso

**Estado: Operativo.**

1. Como Administrador vaya a **Ajustes → Usuarios y compañías → Usuarios**.
2. Abra el usuario y asigne solo los módulos/niveles que necesita: Ventas, Compras, Inventario, Contabilidad, Analítica o Administración.
3. Use `contabilidad` para operación contable; reserve Administrador para configuración, cierres, tipos de comprobante y tareas programadas.
4. Evite compartir usuarios y mantenga contraseñas individuales.

En este entorno de prueba existen usuarios demostrativos. Antes de producción cambie contraseñas, elimine accesos no requeridos y valide una matriz de permisos con el cliente.

## Referencias relacionadas

- [Implementación frente a requisitos actualizados](IMPLEMENTACION_REQUISITOS_2026-08-12.md)
- [Guía de contabilidad operativa](GUIA_CONTABILIDAD_OPERATIVA.md)
- [Pruebas SUNAT](SUNAT_PRUEBAS.md)
