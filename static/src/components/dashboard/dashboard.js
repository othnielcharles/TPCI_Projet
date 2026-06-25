/** @odoo-module */

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, onMounted, useRef, useState } from "@odoo/owl";
import { loadJS } from "@web/core/assets";

export class ItParcDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.chartRef = useRef("chart");
        
        this.state = useState({
            stats: {
                total_equipments: 0,
                in_maintenance: 0,
                active_contracts: 0,
                total_maintenance_cost: 0,
                chart_data: { labels: [], values: [] }
            }
        });

        onWillStart(async () => {
            await this.loadData();
            try {
                // Try loading Chart.js from Odoo's internal libs
                await loadJS("/web/static/lib/Chart/Chart.js");
            } catch (e) {
                console.warn("Chart.js failed to load from /web/static/lib/Chart/Chart.js, it might already be loaded.");
            }
        });

        onMounted(() => {
            this.renderChart();
        });
    }

    async loadData() {
        const stats = await this.orm.call("it.equipment", "get_statistics", []);
        this.state.stats = stats;
    }

    renderChart() {
        if (!this.chartRef.el) {
            return;
        }
        
        // Ensure Chart is available globally
        if (typeof Chart === 'undefined') {
            console.error("Chart.js is not loaded!");
            return;
        }
        
        const ctx = this.chartRef.el.getContext('2d');
        const data = this.state.stats.chart_data;
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Équipements par catégorie',
                    data: data.values,
                    backgroundColor: [
                        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
                    ],
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                    }
                }
            }
        });
    }
    
    // Actions for clicking on KPIs
    openEquipments() {
        this.action.doAction("it_parc.action_it_equipment");
    }
    
    openMaintenance() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Équipements en Maintenance',
            res_model: 'it.equipment',
            view_mode: 'list,form',
            domain: [['state', '=', 'maintenance']],
        });
    }
    
    openContracts() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Contrats Actifs',
            res_model: 'it.contract',
            view_mode: 'list,form',
            domain: [['state', '=', 'active']],
        });
    }
}

ItParcDashboard.template = "it_parc.Dashboard";
registry.category("actions").add("it_parc_dashboard", ItParcDashboard);
