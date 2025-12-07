<template>
    <div class="dashboard-content">
        <!-- Header Section -->
        <section class="mb-4">
            <div class="card border-0 shadow text-white welcome-card p-4">
                <div class="card-body p-0 d-flex justify-content-between align-items-center flex-wrap gap-3">
                    <div>
                        <h2 class="fw-bold mb-2 display-6">Product Manager Dashboard</h2>
                        <p class="mb-0 opacity-75 fs-5">Overview of projects and client information</p>
                    </div>
                    <button type="button" class="btn btn-light text-primary fw-semibold shadow-sm"
                        data-bs-toggle="modal" data-bs-target="#newClientModal">
                        <i class="bi bi-plus-lg me-2"></i>Add New Client
                    </button>
                </div>
            </div>
        </section>

        <!-- Stats Section -->
        <div v-if="stats" class="row g-4 mb-4">
            <div class="col-xl-3 col-md-6">
                <div class="card border-0 shadow-sm h-100 stat-card-hover">
                    <div class="card-body d-flex align-items-center p-3">
                        <div
                            class="stat-icon bg-primary rounded-3 text-white d-flex align-items-center justify-content-center me-3">
                            <i class="bi bi-folder2-open fs-4"></i>
                        </div>
                        <div>
                            <h3 class="fw-bold mb-0 text-dark">{{ stats.total_projects }}</h3>
                            <p class="text-muted mb-0 small">Total Projects</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-xl-3 col-md-6">
                <div class="card border-0 shadow-sm h-100 stat-card-hover">
                    <div class="card-body d-flex align-items-center p-3">
                        <div
                            class="stat-icon bg-success rounded-3 text-white d-flex align-items-center justify-content-center me-3">
                            <i class="bi bi-play-circle fs-4"></i>
                        </div>
                        <div>
                            <h3 class="fw-bold mb-0 text-dark">{{ stats.active_projects }}</h3>
                            <p class="text-muted mb-0 small">Active Projects</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-xl-3 col-md-6">
                <div class="card border-0 shadow-sm h-100 stat-card-hover">
                    <div class="card-body d-flex align-items-center p-3">
                        <div
                            class="stat-icon bg-info rounded-3 text-white d-flex align-items-center justify-content-center me-3">
                            <i class="bi bi-check-circle fs-4"></i>
                        </div>
                        <div>
                            <h3 class="fw-bold mb-0 text-dark">{{ stats.completed_projects }}</h3>
                            <p class="text-muted mb-0 small">Completed</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-xl-3 col-md-6">
                <div class="card border-0 shadow-sm h-100 stat-card-hover">
                    <div class="card-body d-flex align-items-center p-3">
                        <div
                            class="stat-icon bg-warning rounded-3 text-white d-flex align-items-center justify-content-center me-3">
                            <i class="bi bi-hourglass-split fs-4"></i>
                        </div>
                        <div>
                            <h3 class="fw-bold mb-0 text-dark">{{ stats.pending_projects || 0 }}</h3>
                            <p class="text-muted mb-0 small">Pending</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Client List Section -->
        <div class="client-list-section mb-5">
            <h3 class="fw-bold text-primary mb-3"><i class="bi bi-building me-2"></i>Client Projects</h3>

            <div v-if="ClientList.length > 0" class="row g-3">
                <div v-for="Client in ClientList" :key="Client.id" class="col-12 col-sm-6 col-md-4 col-xl-3">
                    <RouterLink :to="{ name: 'ProductManagerRequirements', params: { clientId: Client.id } }"
                        class="text-decoration-none">
                        <ProductMangerClientCard :id="Client.id" :clientname="Client.clientname"
                            :description="Client.description" :image="Client.image" />
                    </RouterLink>
                </div>
            </div>

            <div v-else class="alert alert-info border-0 shadow-sm text-center py-4">
                <i class="bi bi-info-circle me-2 fs-5"></i>
                <span class="fs-6">No clients available at the moment.</span>
            </div>
        </div>

        <!-- Charts Section -->
        <div v-if="stats" class="row g-4">
            <div class="col-lg-6">
                <div class="card border-0 shadow-sm h-100">
                    <div class="card-header bg-white border-0 pt-3 ps-3">
                        <h5 class="card-title fw-bold text-primary mb-0"><i class="bi bi-bar-chart me-2"></i>Project
                            Statistics</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas ref="statsChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-lg-6">
                <div class="card border-0 shadow-sm h-100">
                    <div class="card-header bg-white border-0 pt-3 ps-3">
                        <h5 class="card-title fw-bold text-primary mb-0"><i class="bi bi-pie-chart me-2"></i>Status
                            Distribution</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas ref="statusChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <NewClientModal @client-created="onClientCreated" />
    </div>
</template>


<script>

import ProductMangerClientCard from './fragments/ProductMangerClientCard.vue';
import NewClientModal from './fragments/NewClientModal.vue';
import { make_getrequest } from '@/store/appState';
import { Chart, registerables } from 'chart.js';
import { useNotify } from '@/utils/useNotify';

Chart.register(...registerables);

export default {
    name: 'ProductmanagerDashboard',
    data() {
        return {
            ClientList: [],
            stats: null,
            user: null,
            statsChartInstance: null,
            statusChartInstance: null
        };
    },
    setup() {
        const notify = useNotify();
        return { notify };
    },
    components: {
        ProductMangerClientCard,
        NewClientModal
    },
    methods: {
        async fetchClientList() {
            try {
                const response = await make_getrequest('/api/pm/dashboard');

                const dashboardData = response?.data || {};

                const rawClients = dashboardData?.ClientList || dashboardData?.clients || [];
                this.ClientList = rawClients.map(client => ({
                    id: client.id,
                    clientname: client.clientname || client.client_name,
                    description: 'Click to view details',
                    image: client.image || null
                }));

                this.stats = dashboardData?.stats || null;
                this.user = dashboardData?.user || null;

                console.log('Fetched Client List:', this.ClientList);
                console.log('Dashboard Stats:', this.stats);
                console.log('User Info:', this.user);

                this.$nextTick(() => {
                    this.renderCharts();
                });
            } catch (error) {
                console.error('Error fetching client list:', error);
                this.notify.error('Failed to load dashboard data');
                this.ClientList = [];
            }
        },
        decodedDescription(description) {
            if (!description) return 'No description available';

            try {
                return atob(description);
            } catch (e) {
                return description;
            }
        },
        renderCharts() {
            if (!this.stats) return;

            if (this.statsChartInstance) {
                this.statsChartInstance.destroy();
            }
            if (this.statusChartInstance) {
                this.statusChartInstance.destroy();
            }

            const statsCtx = this.$refs.statsChart?.getContext('2d');
            if (statsCtx) {
                this.statsChartInstance = new Chart(statsCtx, {
                    type: 'bar',
                    data: {
                        labels: ['Total Projects', 'Active Projects', 'Completed Projects', 'Pending Projects'],
                        datasets: [{
                            label: 'Number of Projects',
                            data: [
                                this.stats.total_projects || 0,
                                this.stats.active_projects || 0,
                                this.stats.completed_projects || 0,
                                this.stats.pending_projects || 0
                            ],
                            backgroundColor: [
                                'rgba(54, 162, 235, 0.7)',
                                'rgba(75, 192, 192, 0.7)',
                                'rgba(153, 102, 255, 0.7)',
                                'rgba(255, 159, 64, 0.7)'
                            ],
                            borderColor: [
                                'rgba(54, 162, 235, 1)',
                                'rgba(75, 192, 192, 1)',
                                'rgba(153, 102, 255, 1)',
                                'rgba(255, 159, 64, 1)'
                            ],
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    stepSize: 1
                                }
                            }
                        }
                    }
                });
            }

            const statusCtx = this.$refs.statusChart?.getContext('2d');
            if (statusCtx) {
                const pendingProjects = this.stats.pending_projects || 0;

                this.statusChartInstance = new Chart(statusCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Active', 'Completed', 'Pending'],
                        datasets: [{
                            data: [
                                this.stats.active_projects || 0,
                                this.stats.completed_projects || 0,
                                pendingProjects
                            ],
                            backgroundColor: [
                                'rgba(75, 192, 192, 0.7)',
                                'rgba(153, 102, 255, 0.7)',
                                'rgba(255, 159, 64, 0.7)'
                            ],
                            borderColor: [
                                'rgba(75, 192, 192, 1)',
                                'rgba(153, 102, 255, 1)',
                                'rgba(255, 159, 64, 1)'
                            ],
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
            }
        },
        onClientCreated(newClient) {
            console.log('New client created:', newClient);
            this.fetchClientList();
        }
    },
    mounted() {
        this.fetchClientList();
    },
    beforeUnmount() {
        if (this.statsChartInstance) {
            this.statsChartInstance.destroy();
        }
        if (this.statusChartInstance) {
            this.statusChartInstance.destroy();
        }
    }
};
</script>

<style scoped>
.welcome-card {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
}

.stat-icon {
    width: 48px;
    height: 48px;
}

.stat-card-hover {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card-hover:hover {
    transform: translateY(-3px);
    box-shadow: 0 .5rem 1rem rgba(0, 0, 0, .15) !important;
}

.text-decoration-none:hover {
    text-decoration: none !important;
}

.chart-container {
    position: relative;
    width: 100%;
    max-width: 100%;
}

.chart-container canvas {
    max-width: 100%;
    height: auto !important;
}
</style>