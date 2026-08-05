/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class InventoryFloatingChat extends Component {
    static template = "pierinelli_mcp_inventario.InventoryFloatingChat";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            open: false,
            loading: false,
            draft: "",
            messages: [{
                id: 1,
                author: "assistant",
                text: "Hola, soy el asistente de inventario. ¿En qué te ayudo?",
            }],
        });
    }

    toggle() {
        this.state.open = !this.state.open;
    }

    updateDraft(event) {
        this.state.draft = event.target.value;
    }

    async send() {
        const text = this.state.draft.trim();
        if (!text || this.state.loading) {
            return;
        }
        this.state.messages.push({ id: Date.now(), author: "user", text });
        this.state.draft = "";
        this.state.loading = true;
        try {
            const answer = await this.orm.call(
                "pierinelli.mcp.inventory.assistant", "get_chat_answer", [text]
            );
            this.state.messages.push({
                id: Date.now() + 1,
                author: "assistant",
                text: answer,
            });
        } catch {
            this.state.messages.push({
                id: Date.now() + 1,
                author: "assistant",
                text: "No pude consultar el inventario en este momento. Intenta nuevamente.",
            });
        } finally {
            this.state.loading = false;
        }
    }
}

registry.category("main_components").add("pierinelli_mcp_inventory_chat", {
    Component: InventoryFloatingChat,
});
