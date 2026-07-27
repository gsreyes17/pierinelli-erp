/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";

/**
 * Panorama de Almacenes: tablero visual de las sedes de Pierinelli.
 * Carga los datos desde el modelo pierinelli.warehouse.dashboard y los
 * pinta como tarjetas por sede, un mapa del Peru y un ranking de productos.
 */
export class WarehouseDashboard extends Component {
    static template = "pierinelli_almacenes.WarehouseDashboard";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            sedes: [],
            productos: [],
            totales: {},
            moneda: "S/",
            sedeActiva: null,
        });

        onWillStart(async () => {
            await this.load();
        });
    }

    async load() {
        const data = await this.orm.call(
            "pierinelli.warehouse.dashboard",
            "get_dashboard_data",
            []
        );
        Object.assign(this.state, data);
        this.state.loading = false;
    }

    /** Formatea un numero como monto: 1234567.8 -> "1,234,568" */
    fmtMoney(v) {
        return (v || 0).toLocaleString("es-PE", { maximumFractionDigits: 0 });
    }

    fmtM2(v) {
        return (v || 0).toLocaleString("es-PE", { maximumFractionDigits: 0 });
    }

    /** Color de la barra de ocupacion segun el nivel. */
    ocupClass(pct) {
        if (pct >= 80) return "o_pier_bar_high";
        if (pct >= 55) return "o_pier_bar_mid";
        return "o_pier_bar_low";
    }

    hoverSede(code) {
        this.state.sedeActiva = code;
    }
    leaveSede() {
        this.state.sedeActiva = null;
    }

    /** Abrir el inventario (existencias) de una sede concreta. */
    openSede(sede) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: sede.name,
            res_model: "stock.quant",
            views: [[false, "list"], [false, "form"]],
            domain: [["location_id.warehouse_id", "=", sede.id], ["quantity", ">", 0]],
            context: { search_default_internal_loc: 1 },
        });
    }

    /** Abrir la ficha de un producto del ranking. */
    openProducto(prod) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "product.product",
            res_id: prod.id,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("pierinelli_almacenes.dashboard", WarehouseDashboard);
