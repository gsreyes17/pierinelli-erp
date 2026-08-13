/** @odoo-module **/
import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class Panel extends Component {
    static template = "pierinelli_contabilidad_operativa.Panel";
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.state = useState({
            data: {
                borradores: 0,
                por_cobrar: 0,
                por_pagar: 0,
                cajas_abiertas: 0,
                tributos_pendientes: 0,
                presupuestos_abiertos: 0,
                arqueos_pendientes: 0,
            },
            loading: false,
            error: false,
        });
        onWillStart(() => this.load());
    }
    async load() {
        this.state.loading = true;
        this.state.error = false;
        try {
            this.state.data = await this.orm.call("pierinelli.panel.contable", "get_data", []);
        } catch {
            this.state.error = true;
            this.notification.add("No se pudo actualizar el Centro Financiero. Intenta nuevamente.", {
                type: "danger",
            });
        } finally {
            this.state.loading = false;
        }
    }
    async openAction(actionId) {
        try {
            await this.action.doAction(actionId);
        } catch {
            this.notification.add("No se pudo abrir esta sección. Verifica tus permisos e inténtalo nuevamente.", {
                type: "danger",
            });
        }
    }
    openDrafts() { return this.openAction("account.action_move_journal_line"); }
    openReceivables() { return this.openAction("account.action_move_out_invoice_type"); }
    openPayables() { return this.openAction("account.action_move_in_invoice_type"); }
    openCash() { return this.openAction("pierinelli_contabilidad_operativa.action_caja_chica"); }
    openTaxes() { return this.openAction("pierinelli_contabilidad_operativa.action_control_tributario"); }
    openReconciliations() { return this.openAction("pierinelli_contabilidad_operativa.action_arqueo_cobranza"); }
    openBudgets() { return this.openAction("pierinelli_contabilidad_operativa.action_presupuesto"); }
    openTemplates() { return this.openAction("pierinelli_reportes.action_plantilla_asiento"); }
}
registry.category("actions").add("pierinelli_contabilidad_operativa.panel", Panel);
