Se espera trabajar con un entorno de inventario apropiado con las caracteristicas que piden
te presento lo que seria basicamente la tabla global con la que trabajaban en un ERP pasado y
que esperan ver en nuestro modulo de inventario. a partir de esta se trabajarian los distintos segmentos o apartados menores, te doy las columnas
y algunos detalles de descripcion:

    Almacen - Cual Almacen esta
    Codigo SAP
    Ubicacion - mayor precision del Almacen, una zona especifica como para ir a buscar el producto
    Descripcion del material - nombre completo del material (cada llegada de producto)

    Codigo interno - (Explicacion: como algunos productos tienen el mismo codigo SAP, significa
    que de un codigo pueden haber n planchas de losa, y para diferenciar por planchas se hace un codigo interno)
        [ Parentesis de como funciona el codigo interno ]
            Ejemplo, se tiene el producto plancha de cuarcita iron green traslucid, el codigo que hizo
            el cliente fue CIG seguido del mes y año que llego 1025 seguido de un punto y enumerando los
            productos que llegaron. Digamos que el lote trae 20 planchas CIG, cada planta se enlista tal que:
            CIG1025.01
            CIG1025.02
            CIG1025.03
            ...
            CIG1025.20
            Esto con el fin de diferenciar y separar los productos de su lote.
            Adicionalmente, y esto se relaciona con el flujo de entradas y salidas: el producto cuando se vende podra venderse una parte, si se aparta
            por ejemplo en m2 este tendria que irse con una  *ORDEN DE PRODUCCION*, el producto saldria del inventario para que sea cortado, y si queda algo
            de material ingresaria denuevo pero con un punto y la cantidad de vueltas del producto, es decir si salio y fue cortado una vez ingresaria ahora
            con el codigo CIG1025.01.01  si fuera su segundo corte CIG1025.01.02 y tambien validando que obviamente tendria altura y dimensiones mas pequeñas por el corte.
        [ Fin del Parentesis ]
    CONDICION - Los productos tienen diversos estados nombrados en CONDICION: Estandar, Oferta, Liquidacion, y Hueso (hueso es cuando tienen mas de un año y falta hacerle alguna gestion, basicamente estan pendientes de ser pasados a oferta o liquidacion)
    LARGO
    ALTO
    M. NETO
    M. BRUTO
    Cantidad - el cliente dice que es para los porcelanatos, y se va alterando acorde a la unidad de medida que quieran darle
    UM - unidad de medida con el que miden el producto, ligado a cantidad, en este caso demostrarian la cantidad de lo que se eliga, como medida en caja(se vende por caja cerrada), m2 y unidades.
    Estado - indica si esta disponible, vendido o si esta reservado.
    SUB FAMILIA - subfamilia del producto, por ejemplo del porcelanato sale vitacer, emotion, atlas etc.
    FAMILIA - familia del producto, por ejemplo porcelatano
    OBSERVACIONES - campo para escribir libremente y opcional la condicion del producto, si tiene algun quiñe, despunte, rayadura o algo importante de colocar
    CLIENTE RESERVA - persona que compra
    ASESOR - vendedor que hizo la venta
    NRO. COMPROBANTE.
    Fecha COMPROBANTE.
    INI. RESERVA - fecha de resevado (regla de negocio las reservas solo duran 7 dias)
    FIN RESERVA.
    RF. IMPT - referencia de la importacion, (el lote) 
    F. Ingreso - fecha de ingreso de la mercaderia
    Antiguedad - Antiguedad del producto 
    Costo kardex- costo promedio de los productos (Tema sensible, aqui acorde al tipo de producto
        se trabaja por promedio, es decir tengo en mi inventario un producto de 100 soles, si ingreso otro de
        120, entonces el precio de todos pasarian a ser 110)
    CODIGO DE BARRA- elemento que aun no existe pero se quisiera implementarlo, integrado por un CRM
    PRECIO

Adicionalmente quisieran que cada producto se le suba una foto especifica de como se ve, ya que
se comercia con productos y algunos de alta gama son piedras con caracteristicas unicas, por lo menos 
plantean que como se venden productos naturales y artificiales, los artificales pueden tener la misma
foto de formato para no malgastar espacio, pero en el caso de las naturales dispondrian de su foto unica.
Toda o casi toda venta es personalizada


---
De la tabla presentada seria la vista global que tiene el ERP, controlable
por el area de operaciones y produccion, sin embargo el area comercial veria un formato mas simple:
    Almacen
    Ubicacion
    COD. SAP
    NRO. PLANCHA (codigo interno)
    CONDICION
    DESCRIPCION DEL MATERIAL
    LARGO
    ALTO
    NETO
    STOCK (cantidad)
    Unidad Medida
    Asesor (quien realizo alguna accion como venta o reserva)
    OBSERVACIONES (texto editable, indica si tiene veta negra, fisura, etc)
Todo para que el comerciante puedan editar del producto separado o vendido, si se vende llenaria los
detalles como numero de comprobante, cliente, fecha comprobante, datos u observaciones. Y si fuese
reservado pues colocar el cliente y asignar las fechas limites. El sistema mostraria que asesor realizo
tal venta o reserva.

---
Relacionado al punto anterior:
El cliente quiere resolver el problema que le dan otros ERPs, problemas como:
    - Usando su antiguo ERP ingresaba por ejemplo por metros cuadrados m2, compraba un contenedor de pisos (planchas) ingresaba
    la factura y se acabo, no tenia opcion a indicar cuantas planchas, las medidas de las planchas ni nada
    - Cuando un vendedor le daba vendido el ERP no indicaba cual plancha se vendia, no habia ese detalle que permite que el
    vendedor le diga al cliente: tenemos el producto con las medidas que desea en stock. Eso llevaba a que quiza otro vendedor
    agarre el mismo producto y exista una confusion terrible.
    - Su poca claridad del ERP hacia que por ejemplo le indicaba que tenia 100 m2 de material, cuando en realidad todo espera
    suma de retazos y por ende producto que ya no sirve.
---
El apartado de mermas: normalmente existen mermas cuando hay venta por metro lineal, en ese caso el cliente asume su merma,
pero luego hay casos donde se pueden cortar por bloques y esa merma se queda de lado del negocio.
En resumen si tiene que existir un entorno donde se registre la merma para ver si hacer un ajuste, o si la merma fue asumida por el cliente.

---
*ORDEN DE PRODUCCION*
Luego de una factura se establece una Orden de produccion, en la orden de produccion estan listados todas las medidas
especificadas para los cortes, aparte de eso se desea anexar una modulacion, basicamente 1 2 o 3 diseños hechos en autocad
que se integrarian dentro del documento. Asi como realizaste los diseños PDF de reportes, poder crear una orden de produccion
con lo que te comenté, y que permita subir los archivos de modulacion como anexos y generar el pdf completo asi evitar tanto
traslado de informacion y se haga todo en uno de inmediato. Basicamente la orden de produccion y el plano en un mismo doc.