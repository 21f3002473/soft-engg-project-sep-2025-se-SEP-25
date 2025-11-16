<template>
  <div class="container-fluid py-4">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3 text-muted">Loading employee performance...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
    </div>

    <!-- Main Content -->
    <div v-else>
      <!-- Page Header with Employee Info -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card shadow-sm border-0 bg-gradient-primary text-white">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="employee-avatar-lg me-4">
                  <i class="bi bi-person-circle fs-1"></i>
                </div>
                <div class="flex-grow-1">
                  <h2 class="fw-bold mb-2">{{ employeeData?.name }}</h2>
                  <p class="mb-1">
                    <i class="bi bi-envelope me-2"></i>{{ employeeData?.email }}
                  </p>
                  <span class="badge bg-light text-dark">{{ formatRole(employeeData?.role) }}</span>
                </div>
                <div class="text-end">
                  <RouterLink :to="{ name: 'ProductManagerPerformance' }" class="btn btn-light btn-sm">
                    <i class="bi bi-arrow-left me-1"></i>Back to List
                  </RouterLink>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Current Stats Cards -->
      <div class="row g-3 mb-4">
        <div class="col-12 col-sm-6 col-lg-3">
          <div class="card shadow-sm h-100 border-0">
            <div class="card-body text-center">
              <div class="stat-icon bg-success bg-opacity-10 text-success mb-3">
                <i class="bi bi-check-circle-fill fs-3"></i>
              </div>
              <h3 class="fw-bold mb-1">{{ currentStats?.completed || 0 }}</h3>
              <p class="text-muted mb-0 small">Completed Tasks</p>
              <small class="text-success fw-semibold">{{ currentStats?.completed_percentage || 0 }}%</small>
            </div>
          </div>
        </div>

        <div class="col-12 col-sm-6 col-lg-3">
          <div class="card shadow-sm h-100 border-0">
            <div class="card-body text-center">
              <div class="stat-icon bg-primary bg-opacity-10 text-primary mb-3">
                <i class="bi bi-arrow-repeat fs-3"></i>
              </div>
              <h3 class="fw-bold mb-1">{{ currentStats?.in_progress || 0 }}</h3>
              <p class="text-muted mb-0 small">In Progress</p>
              <small class="text-primary fw-semibold">{{ currentStats?.in_progress_percentage || 0 }}%</small>
            </div>
          </div>
        </div>

        <div class="col-12 col-sm-6 col-lg-3">
          <div class="card shadow-sm h-100 border-0">
            <div class="card-body text-center">
              <div class="stat-icon bg-warning bg-opacity-10 text-warning mb-3">
                <i class="bi bi-clock-fill fs-3"></i>
              </div>
              <h3 class="fw-bold mb-1">{{ currentStats?.pending || 0 }}</h3>
              <p class="text-muted mb-0 small">Pending Tasks</p>
              <small class="text-warning fw-semibold">{{ currentStats?.pending_percentage || 0 }}%</small>
            </div>
          </div>
        </div>

        <div class="col-12 col-sm-6 col-lg-3">
          <div class="card shadow-sm h-100 border-0">
            <div class="card-body text-center">
              <div class="stat-icon bg-info bg-opacity-10 text-info mb-3">
                <i class="bi bi-list-task fs-3"></i>
              </div>
              <h3 class="fw-bold mb-1">{{ currentStats?.total || 0 }}</h3>
              <p class="text-muted mb-0 small">Total Tasks</p>
              <small class="text-info fw-semibold">All time</small>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="row g-3">
        <!-- Performance Trends Chart -->
        <div class="col-12 col-lg-8">
          <div class="card shadow-sm h-100 border-0">
            <div class="card-header bg-white border-0">
              <h5 class="card-title mb-0">
                <i class="bi bi-graph-up me-2 text-primary"></i>
                Performance Trends
              </h5>
            </div>
            <div class="card-body">
              <div class="chart-container">
                <canvas ref="performanceChart"></canvas>
              </div>
            </div>
          </div>
        </div>

        <!-- Task Distribution Chart -->
        <div class="col-12 col-lg-4">
          <div class="card shadow-sm h-100 border-0">
            <div class="card-header bg-white border-0">
              <h5 class="card-title mb-0">
                <i class="bi bi-pie-chart me-2 text-primary"></i>
                Task Distribution
              </h5>
            </div>
            <div class="card-body">
              <div class="chart-container">
                <canvas ref="distributionChart"></canvas>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { make_getrequest } from '@/store/appState';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

export default {
  name: 'ProductMangerEmployeePerformance',
  props: {
    employeeId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      employeeData: null,
      currentStats: null,
      performanceTrends: [],
      loading: true,
      error: null,
      performanceChartInstance: null,
      distributionChartInstance: null
    };
  },
  methods: {
    async fetchPerformanceData() {
      this.loading = true;
      this.error = null;

      try {
        const response = await make_getrequest(`/pr/employee/performance/${this.employeeId}`);
        
        console.log('Performance Response:', response);

        const responseData = response?.data || {};
        
        this.employeeData = responseData?.employee || null;
        this.currentStats = responseData?.current_stats || null;
        this.performanceTrends = responseData?.performance_trends || [];

        console.log('Processed Employee Data:', this.employeeData);
        console.log('Current Stats:', this.currentStats);
        console.log('Performance Trends:', this.performanceTrends);

        this.$nextTick(() => {
          this.renderCharts();
        });
        
      } catch (error) {
        console.error('Error fetching performance data:', error);
        this.error = error.message || 'Failed to load performance data. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    renderCharts() {
      // Destroy existing charts
      if (this.performanceChartInstance) {
        this.performanceChartInstance.destroy();
      }
      if (this.distributionChartInstance) {
        this.distributionChartInstance.destroy();
      }

      // Performance Trends Line Chart
      const performanceCtx = this.$refs.performanceChart?.getContext('2d');
      if (performanceCtx && this.performanceTrends.length > 0) {
        const months = this.performanceTrends.map(item => item.month);
        const scores = this.performanceTrends.map(item => item.score);

        this.performanceChartInstance = new Chart(performanceCtx, {
          type: 'line',
          data: {
            labels: months,
            datasets: [{
              label: 'Performance Score',
              data: scores,
              borderColor: 'rgba(54, 162, 235, 1)',
              backgroundColor: 'rgba(54, 162, 235, 0.1)',
              borderWidth: 3,
              fill: true,
              tension: 0.4,
              pointRadius: 5,
              pointHoverRadius: 7,
              pointBackgroundColor: 'rgba(54, 162, 235, 1)',
              pointBorderColor: '#fff',
              pointBorderWidth: 2
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
              legend: {
                display: true,
                position: 'top'
              },
              tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                padding: 12,
                titleFont: { size: 14 },
                bodyFont: { size: 13 }
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                max: 100,
                ticks: {
                  callback: function(value) {
                    return value + '%';
                  }
                }
              }
            }
          }
        });
      }

      // Task Distribution Doughnut Chart
      const distributionCtx = this.$refs.distributionChart?.getContext('2d');
      if (distributionCtx && this.currentStats) {
        this.distributionChartInstance = new Chart(distributionCtx, {
          type: 'doughnut',
          data: {
            labels: ['Completed', 'In Progress', 'Pending'],
            datasets: [{
              data: [
                this.currentStats.completed || 0,
                this.currentStats.in_progress || 0,
                this.currentStats.pending || 0
              ],
              backgroundColor: [
                'rgba(75, 192, 192, 0.8)',
                'rgba(54, 162, 235, 0.8)',
                'rgba(255, 206, 86, 0.8)'
              ],
              borderColor: [
                'rgba(75, 192, 192, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)'
              ],
              borderWidth: 2
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
              legend: {
                position: 'bottom',
                labels: {
                  padding: 15,
                  font: { size: 12 }
                }
              }
            }
          }
        });
      }
    },
    formatRole(role) {
      const roleNames = {
        'employee': 'Employee',
        'pm': 'Product Manager',
        'hr': 'HR Manager',
        'root': 'Administrator',
        'admin': 'Administrator'
      };
      return roleNames[role?.toLowerCase()] || role;
    }
  },
  mounted() {
    this.fetchPerformanceData();
  },
  beforeUnmount() {
    if (this.performanceChartInstance) {
      this.performanceChartInstance.destroy();
    }
    if (this.distributionChartInstance) {
      this.distributionChartInstance.destroy();
    }
  },
  watch: {
    employeeId() {
      this.fetchPerformanceData();
    }
  }
};
</script>

<style scoped>
.bg-gradient-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.employee-avatar-lg {
  font-size: 4rem;
}

.stat-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  margin: 0 auto;
}

.card {
  transition: all 0.3s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1) !important;
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

@media (max-width: 768px) {
  .employee-avatar-lg {
    font-size: 3rem;
  }
}
</style>
