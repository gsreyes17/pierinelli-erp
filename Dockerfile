# Imagen Pierinelli ERP — basada en la imagen oficial de Odoo 19
FROM odoo:19.0

LABEL maintainer="Pierinelli"

USER root

# Configuracion (proxy, addons, data_dir, workers)
COPY ./config/odoo.conf /etc/odoo/odoo.conf

# Modulos personalizados -> ruta que la imagen oficial ya incluye en addons_path
COPY ./custom_addons /mnt/extra-addons

# Script de arranque auto-inicializador (crea BD + demo en el 1er deploy)
COPY ./entrypoint.sh /usr/local/bin/pierinelli-entrypoint.sh
RUN sed -i 's/\r$//' /usr/local/bin/pierinelli-entrypoint.sh \
    && chmod +x /usr/local/bin/pierinelli-entrypoint.sh \
    && chown -R odoo /mnt/extra-addons

USER odoo

EXPOSE 8069

ENTRYPOINT ["/usr/local/bin/pierinelli-entrypoint.sh"]
CMD []
