# Speech de 5 minutos — puntos fuertes y novedades

Narración lista para decir en voz alta (~650 palabras ≈ 5 minutos a ritmo
tranquilo). Las marcas *[cursivas]* son acciones en pantalla mientras hablas —
todas usan datos que ya existen en la base. Los tiempos son orientativos: si te
atrasas, el bloque 4 es el único recortable.

---

## [0:00] El gancho — el problema que nadie les resolvía

> Les voy a contar esto empezando por el problema. En el sistema anterior,
> Pierinelli compraba un contenedor de planchas y el ERP registraba "120 metros
> cuadrados de granito". Nada más. No sabía cuántas planchas eran, ni sus
> medidas, ni cuál era cuál. Y pasaba lo peor: dos vendedores le prometían **la
> misma plancha** a dos clientes distintos. Ese es el problema que este sistema
> mata de raíz.

*[Ten abierto el login. Entra durante la última frase.]*

## [0:40] La plancha única — el corazón

> Aquí cada plancha física es una ficha con nombre propio. *[Inventario abre
> solo en el Panorama: señala las 5 sedes, el mapa, el valor total]* Esto es lo
> primero que ve gerencia: cuánto hay, dónde está, cuánto vale — en tiempo
> real.
>
> *[Planchas → Tabla de Operaciones → abre una natural con foto]* Código,
> medidas, foto de SU veta — porque el cliente elige su plancha por la veta —,
> condición, y si está libre o reservada. Cuando un vendedor la aparta, queda a
> nombre de su cliente por siete días. Si otro vendedor la intenta, el sistema
> lo bloquea. Ese conflicto ya no puede existir.

## [1:40] El flujo completo — de la venta al asiento sin recapturar nada

> Y la operación nace una sola vez. *[Abre una cotización confirmada]* La
> cotización aparta la plancha; la entrega despacha exactamente esa plancha; la
> factura sale con IGV y numeración peruana; y el asiento contable se genera
> solo. Si la venta es en dólares, el vendedor elige la tasa — la de SUNAT o la
> corporativa — y esa elección queda grabada y **manda sobre el asiento en
> soles**. Precio comercial y tipo de cambio son dos decisiones separadas, y
> las dos quedan trazadas.
>
> ¿Y si hay que cortar? *[Abre la OP-00007]* Esta orden tiene **dos planchas a
> la vez** — es de las mejoras de esta semana. Cada una con sus cortes, su
> retorno que vuelve a stock con código de hija, y su merma con destino propio:
> mira, en esta misma orden una merma la asume el cliente y la otra es pérdida
> del negocio. Y el PDF sale con los planos de AutoCAD anexados: un solo
> documento para producción.

## [2:50] La contabilidad peruana completa

> Del lado contable: PCGE completo, caja chica en soles con arqueo físico y
> reposición, detracciones y retenciones controladas contra cada comprobante,
> y el cuadre diario de lo que entró en efectivo. *[Contabilidad → Libros y
> SIRE]* Y los libros: Diario, Mayor, Balance de Comprobación, el 13.1 de
> inventario valorizado, los registros 14.1, 8.1, 8.2 — todos en pantalla,
> Excel y PDF con la marca. *[Carga la vista previa del Diario y descarga un
> Excel en vivo]*

## [3:40] El control de gestión — obras, presupuesto, kardex

> Y esto es lo que convierte datos en decisiones. Cada movimiento puede llevar
> la etiqueta de su obra. *[Abre Condominio Trujillo]* Este proyecto tiene 9
> pedidos y 7 facturas — un clic y los ves todos. Ingresos y costos con la
> misma etiqueta: rentabilidad por proyecto, y el presupuesto avisa si nos
> pasamos.
>
> *[Ficha de un producto → botón Kardex]* Y el kardex que pidió el contador —
> otra novedad de esta semana: físico y valorizado, movimiento por movimiento,
> con saldo corriente que cuadra al céntimo con el stock real. Una rotura se
> registra con su motivo, se valoriza, y aparece aquí mismo.

## [4:20] El cierre — control y honestidad

> Y todo esto con control: cada rol ve solo lo suyo — el vendedor no ve costos
> —, los períodos se bloquean con cierre auditado, y el cierre anual ya está
> preparado en borrador esperando la aprobación del contador. *[Si te da el
> tiempo: publica DEMO-CIERRE-ANUAL-2026 en vivo]*
>
> Una cosa la digo yo antes de que me la pregunten: la última milla electrónica
> — la factura electrónica ante SUNAT, la guía de remisión con firma, el envío
> al SIRE — se activa en producción con el certificado y las credenciales de la
> empresa. El sistema ya deja todo listo para ese conector; lo que ven hoy es
> todo lo demás, funcionando.

## [4:50] La frase final

> En resumen: un sistema que se ve como Pierinelli y opera como Pierinelli.
> La plancha única, el flujo sin recapturas, la contabilidad peruana y el
> control por proyecto — conectados. Cada documento deja su asiento, su
> tercero y sus impuestos identificables. Eso es lo que hoy está en sus manos.

---

## Chuleta de novedades (por si preguntan "¿qué es lo último?")

- **Orden de corte multi-plancha**: varias planchas en una orden, cada una con
  sus cortes, retorno y destino de merma; PDF unificado con planos.
- **Kardex de producto físico y valorizado**, con botón directo en la ficha.
- **La tasa elegida manda**: SUNAT/corporativa se hereda de la cotización a la
  factura y define el asiento en soles (corregido y verificado al céntimo).
- **Obras con botones propios**: desde la ficha del proyecto, sus pedidos y
  facturas en un clic.
- **Cierre/apertura anual, destino 6→9 e IGV de título gratuito** resueltos
  con plantillas — los borradores demo esperan en Asientos contables.
- **Losas pre-cortadas**: planchas que se venden por pieza, con su filtro.

*Antes de hablar: el ritual del paso 0 de la
[chuleta](CHULETA_DEMO.md) — servidor arriba, tasa del día cargada, Ctrl+F5.
Los nombres exactos de cada registro demo están en
[DATOS_DEMO_POR_REQUISITO.md](../contabilidad/DATOS_DEMO_POR_REQUISITO.md).*
