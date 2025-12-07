<template>
  <div class="daily-reports-container">
    <div class="reports-header">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h4 class="mb-0">
          <i class="bi bi-calendar-check me-2"></i>
          Daily Progress Reports
        </h4>
        <button 
          class="btn btn-primary btn-sm"
          @click="generateReport"
          :disabled="generating"
        >
          <span v-if="generating" class="spinner-border spinner-border-sm me-1"></span>
          <i v-else class="bi bi-plus-circle me-1"></i>
          {{ generating ? 'Generating...' : 'Generate Report' }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 text-muted">Loading reports...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle me-2"></i>
      {{ error }}
    </div>

    <div v-else-if="reports.length > 0" class="reports-list">
      <div 
        v-for="report in reports" 
        :key="report.id"
        class="report-card mb-3"
        @click="viewReport(report)"
      >
        <div class="report-card-header">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <h6 class="mb-1">
                <i class="bi bi-file-earmark-text me-2"></i>
                {{ formatDate(report.report_date) }}
              </h6>
              <small class="text-muted">
                Generated: {{ formatDateTime(report.generated_at) }}
              </small>
            </div>
            <div class="report-badges">
              <span class="badge bg-info me-1">
                <i class="bi bi-activity me-1"></i>
                {{ report.updates_count }} updates
              </span>
              <span class="badge bg-success">
                <i class="bi bi-graph-up me-1"></i>
                {{ report.completion_percentage }}%
              </span>
              <span v-if="report.email_sent" class="badge bg-primary ms-1">
                <i class="bi bi-envelope-check"></i>
              </span>
            </div>
          </div>
        </div>
        <div class="report-card-body">
          <p class="report-summary mb-0">{{ report.summary }}</p>
        </div>
      </div>

      <div v-if="hasMore" class="text-center mt-3">
        <button 
          class="btn btn-outline-primary btn-sm"
          @click="loadMore"
          :disabled="loadingMore"
        >
          <span v-if="loadingMore" class="spinner-border spinner-border-sm me-1"></span>
          {{ loadingMore ? 'Loading...' : 'Load More' }}
        </button>
      </div>
    </div>

    <div v-else class="empty-state text-center py-5">
      <i class="bi bi-inbox fs-1 text-muted"></i>
      <p class="mt-3 text-muted">No daily reports yet</p>
      <button class="btn btn-primary btn-sm mt-2" @click="generateReport">
        <i class="bi bi-plus-circle me-1"></i>
        Generate First Report
      </button>
    </div>

    <div class="modal fade" id="reportDetailModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-file-earmark-text me-2"></i>
              Daily Report - {{ selectedReport ? formatDate(selectedReport.report_date) : '' }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div v-if="loadingDetail" class="text-center py-4">
              <div class="spinner-border text-primary"></div>
            </div>
            <div v-else-if="selectedReport" class="report-detail">
              <div v-html="selectedReport.report_body_html"></div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { make_getrequest, make_postrequest } from '@/store/appState';
import { useNotify } from '@/utils/useNotify';
import { Modal } from 'bootstrap';

export default {
  name: 'ProjectDailyReports',
  props: {
    projectId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      reports: [],
      loading: false,
      loadingMore: false,
      generating: false,
      loadingDetail: false,
      error: null,
      limit: 10,
      offset: 0,
      totalCount: 0,
      selectedReport: null,
      detailModal: null
    };
  },
  computed: {
    hasMore() {
      return this.reports.length < this.totalCount;
    }
  },
  methods: {
    async fetchReports(append = false) {
      if (append) {
        this.loadingMore = true;
      } else {
        this.loading = true;
        this.offset = 0;
      }
      
      this.error = null;

      try {
        const response = await make_getrequest(
          `/api/pm/project/${this.projectId}/daily-reports?limit=${this.limit}&offset=${this.offset}`
        );

        if (response && response.data) {
          if (append) {
            this.reports = [...this.reports, ...response.data];
          } else {
            this.reports = response.data;
          }
          this.totalCount = response.total_count || 0;
        }
      } catch (err) {
        console.error('Error fetching daily reports:', err);
        this.error = err.message || 'Failed to load daily reports';
      } finally {
        this.loading = false;
        this.loadingMore = false;
      }
    },
    async generateReport() {
      this.generating = true;
      this.error = null;

      try {
        const response = await make_postrequest(
          `/api/pm/project/${this.projectId}/daily-reports`,
          { auto_send: true }
        );

        if (response && response.message) {
          useNotify({
            title: 'Success',
            text: 'Daily report generation started! It will be ready shortly.',
            type: 'success'
          });
          
          setTimeout(() => {
            this.fetchReports();
          }, 3000);
        }
      } catch (err) {
        console.error('Error generating report:', err);
        useNotify({
          title: 'Error',
          text: err.message || 'Failed to generate report',
          type: 'error'
        });
      } finally {
        this.generating = false;
      }
    },
    async viewReport(report) {
      this.selectedReport = report;
      this.loadingDetail = true;

      if (!this.detailModal) {
        this.detailModal = new Modal(document.getElementById('reportDetailModal'));
      }
      this.detailModal.show();

      try {
        const response = await make_getrequest(
          `/api/pm/daily-reports/${report.id}`
        );

        if (response && response.report) {
          this.selectedReport = response.report;
        }
      } catch (err) {
        console.error('Error fetching report details:', err);
        useNotify({
          title: 'Error',
          text: 'Failed to load report details',
          type: 'error'
        });
      } finally {
        this.loadingDetail = false;
      }
    },
    loadMore() {
      this.offset += this.limit;
      this.fetchReports(true);
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        });
      } catch (e) {
        return dateString;
      }
    },
    formatDateTime(dateString) {
      if (!dateString) return 'N/A';
      try {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      } catch (e) {
        return dateString;
      }
    }
  },
  mounted() {
    this.fetchReports();
  },
  watch: {
    projectId() {
      this.fetchReports();
    }
  }
};
</script>

<style scoped>
.daily-reports-container {
  padding: 20px;
}

.reports-header h4 {
  color: #333;
  font-weight: 600;
}

.report-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.report-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
  transform: translateY(-2px);
}

.report-card-header h6 {
  color: #333;
  font-weight: 600;
  margin: 0;
}

.report-badges .badge {
  font-size: 0.75rem;
  padding: 4px 8px;
}

.report-summary {
  color: #666;
  font-size: 0.9rem;
  margin-top: 10px;
  line-height: 1.5;
}

.empty-state i {
  font-size: 4rem;
  color: #ccc;
}

.modal-xl {
  max-width: 1200px;
}

.report-detail {
  max-height: 70vh;
  overflow-y: auto;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .report-badges {
    margin-top: 8px;
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }
  
  .modal-xl {
    max-width: 95%;
  }
}
</style>