<template>
    <div class="dashboard">
        <div class="container-fluid">
            <!-- Page Header -->
            <div class="row mb-4">
                <div class="col-12 d-flex justify-content-between align-items-center">
                    <div>
                        <h2 class="fw-bold mb-3">Product Manager Dashboard</h2>
                        <p class="text-muted">Overview of projects and client information</p>
                    </div>
                    <button 
                        type="button" 
                        class="btn btn-primary"
                        data-bs-toggle="modal" 
                        data-bs-target="#newClientModal"
                    >
                        <i class="bi bi-plus-lg me-2"></i>Add New Client
                    </button>
                </div>
            </div>

            <div class="client-list-section">
                <div class="row mb-3">
                    <div class="col-12">
                        <h3 class="fw-bold">Client Projects</h3>
                    </div>
                </div>

                <div v-if="ClientList.length > 0" class="row g-3">
                    <div 
                        v-for="Client in ClientList" 
                        :key="Client.id"
                        class="col-12 col-sm-6 col-md-4 col-xl-3"
                    >
                        <RouterLink 
                            :to="{ name: 'ProductManagerRequirements', params: { clientId: Client.id } }"
                            class="text-decoration-none"
                        >
                            <ProductMangerClientCard 
                                :id="Client.id" 
                                :clientname="Client.clientname" 
                                :description="Client.description"
                                :image="Client.image"
                            />
                        </RouterLink>
                    </div>
                </div>

                <div v-else class="row">
                    <div class="col-12">
                        <div class="alert alert-info text-center" role="alert">
                            <i class="bi bi-info-circle me-2"></i>
                            No clients available at the moment.
                        </div>
                    </div>
                </div>
            </div>

            <!-- Stats Section -->
            <div v-if="stats" class="stats-section mb-5">
                <!-- Stats Cards Row -->
                <div class="row g-3 mb-4">
                    <div class="col-12 col-sm-6 col-lg-3">
                        <div class="card text-center text-white bg-primary shadow-sm h-100">
                            <div class="card-body">
                                <h3 class="display-6 fw-bold mb-2">{{ stats.total_projects }}</h3>
                                <p class="mb-0">Total Projects</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-12 col-sm-6 col-lg-3">
                        <div class="card text-center text-white bg-success shadow-sm h-100">
                            <div class="card-body">
                                <h3 class="display-6 fw-bold mb-2">{{ stats.active_projects }}</h3>
                                <p class="mb-0">Active Projects</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-12 col-sm-6 col-lg-3">
                        <div class="card text-center text-white bg-info shadow-sm h-100">
                            <div class="card-body">
                                <h3 class="display-6 fw-bold mb-2">{{ stats.completed_projects }}</h3>
                                <p class="mb-0">Completed Projects</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-12 col-sm-6 col-lg-3">
                        <div class="card text-center text-white bg-warning shadow-sm h-100">
                            <div class="card-body">
                                <h3 class="display-6 fw-bold mb-2">{{ stats.pending_projects || 0 }}</h3>
                                <p class="mb-0">Pending Projects</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Charts Row -->
                <div class="row g-3">
                    <div class="col-12 col-lg-6">
                        <div class="card shadow-sm h-100">
                            <div class="card-header bg-white">
                                <h5 class="card-title mb-0">Project Statistics</h5>
                            </div>
                            <div class="card-body">
                                <div class="chart-container">
                                    <canvas ref="statsChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-12 col-lg-6">
                        <div class="card shadow-sm h-100">
                            <div class="card-header bg-white">
                                <h5 class="card-title mb-0">Project Status Distribution</h5>
                            </div>
                            <div class="card-body">
                                <div class="chart-container">
                                    <canvas ref="statusChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Client List Section -->
            
        </div>

        <!-- New Client Modal -->
        <NewClientModal @client-created="onClientCreated" />
    </div>
</template>


<script>

import ProductMangerClientCard from './fragments/ProductMangerClientCard.vue';
import NewClientModal from './fragments/NewClientModal.vue';
import { make_getrequest } from '@/store/appState';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

// make API call to the endpoint "/api/pm/dashboard" to get the list of clients

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
    components: {
        ProductMangerClientCard,
        NewClientModal
    },
    methods: {
        async fetchClientList() {
            try {
                const response = await make_getrequest('/api/pm/dashboard');
                
                // Handle the nested response structure - data is inside response.data
                const dashboardData = response?.data || {};
                
                // Map ClientList to match the card component props
                // API returns: { id, clientname, image } where image is image_base64
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
                
                // Render charts after data is loaded
                this.$nextTick(() => {
                    this.renderCharts();
                });
            } catch (error) {
                console.error('Error fetching client list:', error);
                // Ensure ClientList is empty array on error
                this.ClientList = [];
            }
        },
        decodedDescription(description) {
            if (!description) return 'No description available';
            
            try {
                // Try to decode base64 if it's encoded
                return atob(description);
            } catch (e) {
                // If decoding fails, return as is
                return description;
            }
        },
        renderCharts() {
            if (!this.stats) return;
            
            // Destroy existing charts if they exist
            if (this.statsChartInstance) {
                this.statsChartInstance.destroy();
            }
            if (this.statusChartInstance) {
                this.statusChartInstance.destroy();
            }
            
            // Bar Chart for Stats
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
            
            // Doughnut Chart for Status
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
            // Refresh the client list after a new client is created
            this.fetchClientList();
        }
    },
    mounted() {
        this.fetchClientList();
    },
    beforeUnmount() {
        // Clean up charts when component is destroyed
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
.dashboard {
    background-color: #f8f9fa;
    min-height: 100vh;
    max-width: 100vw;
    overflow-x: hidden;
    padding: 1.5rem 0;
}

.container-fluid {
    max-width: 100%;
    /* padding-left: 1rem;
    padding-right: 1rem; */
}

.card {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border: 1px solid rgba(0, 0, 0, 0.1);
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

.client-list-section {
    margin-top: 2rem;
}

.text-decoration-none:hover {
    text-decoration: none !important;
}

/* Ensure charts are responsive */
.chart-container {
    position: relative;
    width: 100%;
    max-width: 100%;
}

.chart-container canvas {
    max-width: 100%;
    height: auto !important;
}

/* Fix Bootstrap row overflow */
.row {
    --bs-gutter-x: 1.5rem;
    margin-left: calc(var(--bs-gutter-x) * -0.5);
    margin-right: calc(var(--bs-gutter-x) * -0.5);
}

/* Responsive padding adjustments */
@media (min-width: 768px) {
    .container-fluid {
        padding-left: 2rem;
        padding-right: 2rem;
    }
}

@media (min-width: 1200px) {
    .container-fluid {
        padding-left: 3rem;
        padding-right: 3rem;
    }
}

/* Ensure no element causes overflow */
* {
    box-sizing: border-box;
}
</style>