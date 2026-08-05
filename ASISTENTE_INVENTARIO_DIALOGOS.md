# Dialogos habilitados del Asistente Pierinelli

El boton dorado de la esquina inferior derecha abre un chat de inventario.
Esta primera version no usa IA externa, no interpreta variantes libres y no
modifica informacion. Responde con datos actuales de Odoo solo cuando recibe
uno de estos cinco mensajes.

Escribelos tal cual. El chat tambien acepta mayusculas/minusculas, tildes y
signos de pregunta de forma indistinta.

1. `Que stock vendible hay actualmente`

   Responde metros cuadrados disponibles, numero de planchas y materiales.

2. `Que reservas vencen hoy o ya vencieron`

   Lista las reservas que requieren ser liberadas.

3. `Que planchas naturales no tienen foto`

   Lista las planchas naturales con stock que aun necesitan una foto individual.

4. `Cuantas mermas hay este mes`

   Indica el numero de mermas y los m2 acumulados desde el primer dia del mes.

5. `Que planchas estan pendientes de revision`

   Lista retazos o planchas que Operaciones debe medir, revisar y habilitar.

## Cuando se escribe otra consulta

El asistente responde que la consulta aun no esta habilitada y deriva a esta
guia. Es intencional: no inventa datos, no tiene acceso para editar inventario
y no envia informacion a servicios externos.

## Siguiente etapa

Cuando se conecte DeepSeek u otro proveedor, estas cinco consultas seguiran
siendo las herramientas seguras de lectura. El proveedor podra entender una
pregunta escrita naturalmente y elegir la herramienta adecuada, sin obtener
acceso directo a PostgreSQL ni permisos para modificar existencias.
