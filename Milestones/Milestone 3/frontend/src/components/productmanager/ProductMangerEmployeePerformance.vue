<template>
  <div class="container-fluid py-4">
    <div class="row g-4">
      
      <div class="col-lg-3 col-md-4">
        <div class="card shadow-sm">
          <div class="card-body text-center">
            <img
              :src="`https://dummyjson.com/icon/${employeeId}/150`"
              alt="Employee Image"
              class="img-fluid rounded-circle mb-3 border border-3 border-primary"
              style="width: 150px; height: 150px; object-fit: cover;"
            />
            <h4 class="card-title mb-2">Employee ID: {{ employeeId }}</h4>
            <p class="card-text text-muted">Details about Employee with ID: {{ employeeId }}</p>
          </div>
        </div>

        <div class="card shadow-sm mt-3">
          <div class="card-header bg-info text-white">
            <h5 class="mb-0">Current Stats</h5>
          </div>
          <div class="card-body">
            <canvas ref="pieChart"></canvas>
          </div>
        </div>
      </div>

      
      <div class="col-lg-9 col-md-8">
        <div class="card shadow-sm mb-3">
          <div class="card-header bg-success text-white">
            <h5 class="mb-0">Performance Trends</h5>
          </div>
          <div class="card-body">
            <canvas ref="lineChart"></canvas>
          </div>
        </div>

        <div class="card shadow-sm">
          <div class="card-header bg-primary text-white">
            <h3 class="h5 mb-0">AI Performance Assistant</h3>
          </div>
          <div class="card-body">
            <ProductMangerChatbot />
          </div>
        </div>
      </div>
    </div>
  </div>

</template>

<script>
import ProductMangerChatbot from './fragments/ProductMangerChatbot.vue';
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
  components: {
    ProductMangerChatbot
  },
  data() {
    return {
      pieChartInstance: null,
      lineChartInstance: null
    };
  },
  mounted() {
    this.initPieChart();
    this.initLineChart();
  },
  beforeUnmount() {
    if (this.pieChartInstance) this.pieChartInstance.destroy();
    if (this.lineChartInstance) this.lineChartInstance.destroy();
  },
  methods: {
    initPieChart() {
      const ctx = this.$refs.pieChart.getContext('2d');
      this.pieChartInstance = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: ['Completed', 'In Progress', 'Pending'],
          datasets: [{
            data: [65, 25, 10],
            backgroundColor: ['#28a745', '#ffc107', '#dc3545'],
            borderWidth: 2,
            borderColor: '#fff'
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
    },
    initLineChart() {
      const ctx = this.$refs.lineChart.getContext('2d');
      this.lineChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
          datasets: [{
            label: 'Performance Score',
            data: [65, 72, 68, 78, 85, 88],
            borderColor: '#007bff',
            backgroundColor: 'rgba(0, 123, 255, 0.1)',
            tension: 0.4,
            fill: true,
            pointRadius: 5,
            pointHoverRadius: 7
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          scales: {
            y: {
              beginAtZero: true,
              max: 100
            }
          },
          plugins: {
            legend: {
              display: true,
              position: 'top'
            }
          }
        }
      });
    }
  }
}
</script>

<style scoped>
/* Minimal custom styles - Bootstrap handles most of the styling */
@media (max-width: 768px) {
  .card-body .border.rounded {
    min-height: 300px;
  }
}
</style>
