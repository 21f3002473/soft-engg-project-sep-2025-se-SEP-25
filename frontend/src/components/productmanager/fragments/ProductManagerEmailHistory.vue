<template>
  <div class="email-history-container">
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading emails...</span>
      </div>
      <p class="mt-3 text-muted">Loading email history...</p>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
    </div>

    <div v-else>
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h5 class="text-primary mb-0">
          <i class="bi bi-envelope-check me-2"></i>
          Email History ({{ totalEmails }})
        </h5>
        <button class="btn btn-primary btn-sm" @click="generateEmail" :disabled="generating">
          <span v-if="generating" class="spinner-border spinner-border-sm me-1"></span>
          <i v-else class="bi bi-send me-1"></i>
          {{ generating ? 'Generating...' : 'Generate & Send Email' }}
        </button>
      </div>



      <div v-if="emails.length === 0" class="text-center py-5 bg-light rounded">
        <i class="bi bi-inbox fs-1 text-muted"></i>
        <p class="mt-3 text-muted">No emails sent yet</p>
        <button class="btn btn-primary mt-2" @click="generateEmail">
          <i class="bi bi-send me-1"></i>
          Send First Progress Email
        </button>
      </div>

      <div v-else class="email-timeline">
        <div v-for="email in emails" :key="email.id" class="email-card mb-3">
          <div class="card shadow-sm">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start mb-3">
                <div class="flex-fill">
                  <h6 class="mb-1 fw-bold">{{ email.subject }}</h6>
                  <div class="d-flex flex-wrap gap-2 align-items-center text-muted small">
                    <span>
                      <i class="bi bi-calendar3 me-1"></i>
                      {{ formatDate(email.sent_at) }}
                    </span>
                    <span>
                      <i class="bi bi-envelope me-1"></i>
                      {{ email.recipient_email }}
                    </span>
                    <span class="badge" :class="{
                      'bg-success': email.delivery_status === 'sent',
                      'bg-danger': email.delivery_status === 'failed',
                      'bg-warning': email.delivery_status === 'pending'
                    }">
                      {{ email.delivery_status }}
                    </span>
                    <span v-if="email.opened" class="badge bg-info">
                      <i class="bi bi-eye me-1"></i>Opened
                    </span>
                  </div>
                </div>
                <button class="btn btn-sm btn-outline-primary" @click="viewEmailDetails(email.id)"
                  data-bs-toggle="modal" data-bs-target="#emailDetailModal">
                  <i class="bi bi-eye"></i>
                </button>
              </div>

              <div class="d-flex flex-wrap gap-3 small text-muted">
                <span v-if="email.project_status">
                  <i class="bi bi-diagram-3 me-1"></i>
                  Project: {{ email.project_status }}
                </span>
                <span>
                  <i class="bi bi-tag me-1"></i>
                  Trigger: {{ formatTriggerType(email.trigger_type) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="emailDetailModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">
              <i class="bi bi-envelope-open me-2"></i>
              Email Details
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div v-if="loadingDetail" class="text-center py-4">
              <div class="spinner-border text-primary" role="status"></div>
            </div>
            <div v-else-if="selectedEmail">
              <div class="mb-4">
                <h6 class="fw-bold mb-3">{{ selectedEmail.email.subject }}</h6>
                <div class="row g-2 mb-3">
                  <div class="col-md-6">
                    <small class="text-muted">Sent At:</small><br>
                    <span>{{ formatDate(selectedEmail.email.sent_at) }}</span>
                  </div>
                  <div class="col-md-6">
                    <small class="text-muted">To:</small><br>
                    <span>{{ selectedEmail.email.recipient_email }}</span>
                  </div>
                  <div class="col-md-6">
                    <small class="text-muted">Status:</small><br>
                    <span class="badge bg-success">{{ selectedEmail.email.delivery_status }}</span>
                  </div>
                  <div class="col-md-6">
                    <small class="text-muted">Opened:</small><br>
                    <span>{{ selectedEmail.email.opened ? 'Yes' : 'No' }}</span>
                  </div>
                </div>
              </div>

              <div v-if="selectedEmail.project" class="mb-4 p-3 bg-light rounded">
                <small class="text-muted">Project:</small>
                <p class="mb-0 fw-bold">{{ selectedEmail.project.project_name }}</p>
              </div>

              <ul class="nav nav-tabs mb-3" role="tablist">
                <li class="nav-item">
                  <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#html-content" type="button">
                    <i class="bi bi-file-code me-1"></i>HTML Preview
                  </button>
                </li>
                <li class="nav-item">
                  <button class="nav-link" data-bs-toggle="tab" data-bs-target="#text-content" type="button">
                    <i class="bi bi-file-text me-1"></i>Plain Text
                  </button>
                </li>
              </ul>

              <div class="tab-content">
                <div class="tab-pane fade show active" id="html-content">
                  <div class="border rounded p-3" style="max-height: 500px; overflow-y: auto; background-color: white;"
                    v-html="selectedEmail.email.email_body_html"></div>
                </div>

                <div class="tab-pane fade" id="text-content">
                  <pre class="border rounded p-3 bg-light"
                    style="max-height: 500px; overflow-y: auto; white-space: pre-wrap;">{{ selectedEmail.email.email_body_text }}</pre>
                </div>
              </div>
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

export default {
  name: 'ProductManagerEmailHistory',
  props: {
    projectId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      emails: [],
      selectedEmail: null,
      loading: false,
      loadingDetail: false,
      generating: false,
      error: null,
      totalEmails: 0
    };
  },
  setup() {
    const notify = useNotify();
    return { notify };
  },
  mounted() {
    this.fetchEmails();
  },
  methods: {
    async fetchEmails() {
      this.loading = true;
      this.error = null;
      try {
        const response = await make_getrequest(
          `/api/pm/project/${this.projectId}/progress-emails`
        );

        if (response && response.data) {
          const data = response.data;
          this.emails = data.emails || [];
          this.totalEmails = data.total_emails || 0;
        } else {
          // Fallback if data structure is different or empty
          this.emails = [];
        }

      } catch (error) {
        console.error('Error fetching email history:', error);
        this.error = error.message || 'Failed to load email history';
        // Optional: keep error in UI instead of toast for initial load
      } finally {
        this.loading = false;
      }
    },

    async generateEmail() {
      this.generating = true;
      this.error = null;
      try {
        const response = await make_postrequest(
          `/api/pm/project/${this.projectId}/progress-emails?auto_send=true&trigger_type=manual`,
          {}
        );

        if (response && response.message) {
          this.notify.success(response.message + ' - Email will be sent shortly!');
          setTimeout(() => {
            this.fetchEmails();
          }, 3000);
        } else if (response && response.data && response.data.message) {
          this.notify.success(response.data.message + ' - Email will be sent shortly!');
          setTimeout(() => {
            this.fetchEmails();
          }, 3000);
        } else {
          this.notify.error("Failed to generate email");
        }
      } catch (error) {
        console.error('Error generating email:', error);
        const errMsg = error.message || 'Failed to generate email';
        this.notify.error(errMsg);
      } finally {
        this.generating = false;
      }
    },

    async viewEmailDetails(emailId) {
      this.loadingDetail = true;
      try {
        const response = await make_getrequest(
          `/api/pm/progress-emails/${emailId}`
        );

        if (response && response.data) {
          this.selectedEmail = response.data;
        } else if (response && response.message) { // Sometimes it returns data directly depending on wrapper but usually .data
          this.selectedEmail = response;
        }
      } catch (error) {
        console.error('Error fetching email details:', error);
        this.notify.error(error.message || 'Failed to load email details');
      } finally {
        this.loadingDetail = false;
      }
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },

    formatTriggerType(type) {
      return type?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Manual';
    }
  }
};
</script>

<style scoped>
.email-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.email-card:hover {
  transform: translateY(-2px);
}

.email-timeline {
  position: relative;
  padding-left: 20px;
}

.email-timeline::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(to bottom, #667eea, #764ba2);
}

.email-card::before {
  content: '';
  position: absolute;
  left: -24px;
  top: 20px;
  width: 10px;
  height: 10px;
  background: #667eea;
  border-radius: 50%;
  border: 3px solid white;
  box-shadow: 0 0 0 2px #667eea;
}
</style>
