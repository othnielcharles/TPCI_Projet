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
        
        // Define today's date formatted
        const today = new Date();
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        
        this.state = useState({
            today_date: today.toLocaleDateString('fr-FR', options),
            stats: {
                total_equipments: 0,
                in_maintenance: 0,
                active_contracts: 0,
                total_maintenance_cost: 0,
                availability_rate: 100,
                avg_intervention_cost: 0,
                status_counts: {},
                chart_data: { labels: [], values: [] },
                recent_interventions: [],
                expiring_contracts: []
            }
        });

        onWillStart(async () => {
            await this.loadData();
            try {
                await loadJS("/web/static/lib/Chart/Chart.js");
            } catch (e) {
                console.warn("Chart.js failed to load, might already be loaded.");
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
        if (!this.chartRef.el || typeof Chart === 'undefined') {
            return;
        }
        
        const ctx = this.chartRef.el.getContext('2d');
        const data = this.state.stats.chart_data;
        
        // Création de dégradés (gradients) pour un look ultra premium
        const createGradient = (color1, color2) => {
            const gradient = ctx.createLinearGradient(0, 0, 0, 400);
            gradient.addColorStop(0, color1);
            gradient.addColorStop(1, color2);
            return gradient;
        };

        const premiumColors = [
            createGradient('#4f46e5', '#818cf8'), // Indigo
            createGradient('#0ea5e9', '#38bdf8'), // Sky
            createGradient('#10b981', '#34d399'), // Emerald
            createGradient('#f59e0b', '#fbbf24'), // Amber
            createGradient('#ef4444', '#f87171'), // Red
            createGradient('#8b5cf6', '#a78bfa'), // Violet
            createGradient('#ec4899', '#f472b6'), // Pink
            createGradient('#64748b', '#94a3b8')  // Slate
        ];
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Équipements par catégorie',
                    data: data.values,
                    backgroundColor: premiumColors.slice(0, data.labels.length),
                    borderWidth: 0,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutoutPercentage: 75, // Makes the doughnut thinner and more modern
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: {
                                family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto",
                                size: 13
                            }
                        }
                    }
                },
                layout: {
                    padding: 20
                }
            }
        });
    }
    
    // Actions de Navigation Rapide
    openEquipments() {
        this.action.doAction("it_parc.action_it_equipment");
    }
    
    openMaintenance() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Équipements en Maintenance',
            res_model: 'it.equipment',
            views: [[false, 'list'], [false, 'form']],
            domain: [['state', '=', 'maintenance']],
        });
    }
    
    openContracts() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Contrats Actifs',
            res_model: 'it.contract',
            views: [[false, 'list'], [false, 'form']],
            domain: [['state', '=', 'active']],
        });
    }
}

ItParcDashboard.template = "it_parc.Dashboard";
registry.category("actions").add("it_parc_dashboard", ItParcDashboard);
