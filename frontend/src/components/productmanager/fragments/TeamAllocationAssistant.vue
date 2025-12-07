<template>
  <div class="team-allocation-container">
    <!-- Header with NL Query Interface -->
    <div class="card shadow-sm mb-4">
      <div class="card-header bg-gradient-primary text-white">
        <h5 class="mb-0">
          <i class="bi bi-people-fill me-2"></i>
          AI Team Allocation Assistant
        </h5>
      </div>
      <div class="card-body">
        <!-- Natural Language Query -->
        <div class="mb-3">
          <label class="form-label fw-bold">Ask me anything about team allocation:</label>
          <div class="input-group input-group-lg">
            <input
              v-model="nlQuery"
              type="text"
              class="form-control"
              placeholder="e.g., Who are the best Python developers available?"
              @keyup.enter="handleNLQuery"
              :disabled="processingQuery"
            />
            <button
              class="btn btn-primary"
              @click="handleNLQuery"
              :disabled="processingQuery || !nlQuery.trim()"
            >
              <span v-if="processingQuery" class="spinner-border spinner-border-sm me-1"></span>
              <i v-else class="bi bi-search me-1"></i>
              Ask AI
            </button>
          </div>
        </div>

        <!-- Query Response -->
        <div v-if="queryResponse" class="alert alert-info">
          <strong>AI Response:</strong>
          <p class="mb-0 mt-2" style="white-space: pre-wrap">{{ queryResponse.response }}</p>
          
          <!-- Show matched employees if available -->
          <div v-if="queryResponse.data && queryResponse.data.employees" class="mt-3">
            <strong>Matching Employees:</strong>
            <div class="table-responsive mt-2">
              <table class="table table-sm">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Skill</th>
                    <th>Proficiency</th>
                    <th>Utilization</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="emp in queryResponse.data.employees.slice(0, 5)" :key="emp.id">
                    <td>{{ emp.name }}</td>
                    <td>{{ emp.skill }}</td>
                    <td><span class="badge bg-secondary">{{ emp.proficiency }}</span></td>
                    <td>{{ emp.current_utilization.toFixed(0) }}%</td>
                    <td>
                      <span :class="emp.is_available ? 'badge bg-success' : 'badge bg-danger'">
                        {{ emp.is_available ? 'Available' : 'Busy' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Generate Recommendations -->
        <div class="mt-3">
          <button
            class="btn btn-success btn-lg"
            @click="showGenerateModal = true"
            :disabled="!projectId"
          >
            <i class="bi bi-magic me-2"></i>
            Generate Team Recommendations
          </button>
          <small class="text-muted ms-2">AI will analyze project and recommend best team members</small>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3 text-muted">Loading recommendations...</p>
    </div>

    <!-- Recommendations List -->
    <div v-else-if="recommendations.length > 0">
      <h5 class="mb-3">
        <i class="bi bi-star-fill text-warning me-2"></i>
        AI Recommendations ({{ recommendations.length }})
      </h5>

      <div class="row g-3">
        <div
          v-for="rec in recommendations"
          :key="rec.id"
          class="col-12 col-md-6 col-lg-4"
        >
          <div class="recommendation-card card h-100" :class="getCardClass(rec.status)">
            <div class="card-body">
              <!-- Employee Info -->
              <div class="d-flex align-items-center mb-3">
                <div class="employee-avatar me-3">
                  <i class="bi bi-person-circle fs-1"></i>
                </div>
                <div class="flex-grow-1">
                  <h6 class="mb-0">{{ rec.employee_name }}</h6>
                  <small class="text-muted">{{ rec.employee_email }}</small>
                </div>
              </div>

              <!-- Match Score -->
              <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <span class="fw-bold">Match Score</span>
                  <span class="badge bg-primary fs-6">{{ rec.match_score.toFixed(1) }}%</span>
                </div>
                <div class="progress" style="height: 8px">
                  <div
                    class="progress-bar"
                    :class="getProgressClass(rec.match_score)"
                    :style="{ width: rec.match_score + '%' }"
                  ></div>
                </div>
              </div>

              <!-- Score Breakdown -->
              <div class="score-breakdown mb-3">
                <small class="text-muted">Score Breakdown:</small>
                <div class="d-flex justify-content-between mt-1">
                  <span><i class="bi bi-gear text-primary"></i> Skills: {{ rec.skill_match_score.toFixed(0) }}%</span>
                  <span><i class="bi bi-briefcase text-success"></i> Exp: {{ rec.experience_match_score.toFixed(0) }}%</span>
                </div>
                <div class="d-flex justify-content-between">
                  <span><i class="bi bi-check-circle text-info"></i> Avail: {{ rec.availability_score.toFixed(0) }}%</span>
                  <span><i class="bi bi-bar-chart text-warning"></i> Load: {{ rec.workload_score.toFixed(0) }}%</span>
                </div>
              </div>

              <!-- Matching Skills -->
              <div class="mb-3">
                <small class="text-muted">Matching Skills:</small>
                <div class="mt-1">
                  <span
                    v-for="skill in rec.matching_skills.slice(0, 3)"
                    :key="skill"
                    class="badge bg-secondary me-1 mb-1"
                  >
                    {{ skill }}
                  </span>
                  <span v-if="rec.matching_skills.length > 3" class="badge bg-light text-dark">
                    +{{ rec.matching_skills.length - 3 }} more
                  </span>
                </div>
              </div>

              <!-- Policy Violations -->
              <div v-if="rec.policy_violations.length > 0" class="alert alert-warning alert-sm mb-3">
                <i class="bi bi-exclamation-triangle me-1"></i>
                <small>{{ rec.policy_violations.length }} policy concern(s)</small>
              </div>

              <!-- Status Badge -->
              <div class="mb-3">
                <span :class="getStatusBadgeClass(rec.status)">
                  {{ formatStatus(rec.status) }}
                </span>
              </div>

              <!-- Action Buttons -->
              <div class="d-grid gap-2" v-if="rec.status === 'pending_review'">
                <button
                  class="btn btn-success btn-sm"
                  @click="approveRecommendation(rec)"
                  :disabled="processing"
                >
                  <i class="bi bi-check-circle me-1"></i>
                  Approve & Assign
                </button>
                <button
                  class="btn btn-outline-danger btn-sm"
                  @click="rejectRecommendation(rec)"
                  :disabled="processing"
                >
                  <i class="bi bi-x-circle me-1"></i>
                  Reject
                </button>
                <button
                  class="btn btn-outline-primary btn-sm"
                  @click="viewDetails(rec)"
                >
                  <i class="bi bi-info-circle me-1"></i>
                  View Details
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Load More -->
      <div v-if="hasMore" class="text-center mt-4">
        <button class="btn btn-outline-primary" @click="loadMore" :disabled="loadingMore">
          <span v-if="loadingMore" class="spinner-border spinner-border-sm me-1"></span>
          {{ loadingMore ? 'Loading...' : 'Load More' }}
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-5">
      <i class="bi bi-robot fs-1 text-muted"></i>
      <p class="mt-3 text-muted">No team recommendations yet</p>
      <button class="btn btn-primary" @click="showGenerateModal = true">
        <i class="bi bi-magic me-1"></i>
        Generate Recommendations
      </button>
    </div>

    <!-- Generate Modal -->
    <Teleport to="body">
      <div 
        class="modal fade" 
        id="generateModal" 
        tabindex="-1" 
        aria-labelledby="generateModalLabel"
        aria-hidden="true"
        data-bs-backdrop="true"
        data-bs-keyboard="true"
      >
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="generateModalLabel">Generate Team Recommendations</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">Team Size Hint</label>
                <input
                  v-model.number="generateForm.team_size_hint"
                  type="number"
                  class="form-control"
                  min="1"
                  max="20"
                />
                <small class="text-muted">Suggested number of team members</small>
              </div>

              <div class="mb-3">
                <label class="form-label">Notification Email</label>
                <input
                  v-model="generateForm.notify_email"
                  type="email"
                  class="form-control"
                  placeholder="manager@example.com"
                />
                <small class="text-muted">Optional: Get notified when analysis is complete</small>
              </div>

              <div class="form-check">
                <input
                  v-model="generateForm.auto_assign"
                  class="form-check-input"
                  type="checkbox"
                  id="autoAssignCheck"
                />
                <label class="form-check-label" for="autoAssignCheck">
                  Auto-assign top recommendations
                </label>
                <small class="text-muted d-block">AI will automatically assign the best matches</small>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button
                type="button"
                class="btn btn-primary"
                @click="generateRecommendations"
                :disabled="generating"
              >
                <span v-if="generating" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-magic me-1"></i>
                {{ generating ? 'Generating...' : 'Generate' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Details Modal -->
    <Teleport to="body">
      <div 
        class="modal fade" 
        id="detailsModal" 
        tabindex="-1" 
        aria-labelledby="detailsModalLabel"
        aria-hidden="true"
        data-bs-backdrop="true"
        data-bs-keyboard="true"
      >
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="detailsModalLabel">Recommendation Details</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body" v-if="selectedRecommendation">
              <h6>{{ selectedRecommendation.employee_name }}</h6>
              <p class="text-muted">{{ selectedRecommendation.employee_email }}</p>

              <h6 class="mt-3">AI Reasoning:</h6>
              <p>{{ selectedRecommendation.reasoning }}</p>

              <h6 class="mt-3">All Matching Skills:</h6>
              <div>
                <span
                  v-for="skill in selectedRecommendation.matching_skills"
                  :key="skill"
                  class="badge bg-primary me-1 mb-1"
                >
                  {{ skill }}
                </span>
              </div>

              <div v-if="selectedRecommendation.concerns && selectedRecommendation.concerns.length > 0">
                <h6 class="mt-3">Concerns:</h6>
                <ul>
                  <li v-for="concern in selectedRecommendation.concerns" :key="concern">
                    {{ concern }}
                  </li>
                </ul>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script>
import { make_getrequest, make_postrequest, make_putrequest } from '@/store/appState';
import { useNotify } from '@/utils/useNotify';
import { Modal } from 'bootstrap';

export default {
  name: 'TeamAllocationAssistant',
  props: {
    projectId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      recommendations: [],
      loading: false,
      loadingMore: false,
      generating: false,
      processing: false,
      processingQuery: false,
      limit: 12,
      offset: 0,
      totalCount: 0,
      
      // NL Query
      nlQuery: '',
      queryResponse: null,

      // Generate form
      showGenerateModal: false,
      generateForm: {
        team_size_hint: 3,
        auto_assign: false,
        notify_email: ''
      },

      // Selected recommendation
      selectedRecommendation: null,

      // Modals
      generateModal: null,
      detailsModal: null
    };
  },
  computed: {
    hasMore() {
      return this.recommendations.length < this.totalCount;
    }
  },
  methods: {
    async fetchRecommendations(append = false) {
      if (append) {
        this.loadingMore = true;
      } else {
        this.loading = true;
        this.offset = 0;
      }

      try {
        const response = await make_getrequest(
          `/api/pm/projects/${this.projectId}/team-allocation?limit=${this.limit}&offset=${this.offset}`
        );

        if (response && response.data) {
          if (append) {
            this.recommendations = [...this.recommendations, ...response.data];
          } else {
            this.recommendations = response.data;
          }
          this.totalCount = response.total_count || 0;
        }
      } catch (err) {
        console.error('Error fetching recommendations:', err);
        useNotify({
          title: 'Error',
          text: 'Failed to load recommendations',
          type: 'error'
        });
      } finally {
        this.loading = false;
        this.loadingMore = false;
      }
    },

    async handleNLQuery() {
      if (!this.nlQuery.trim()) return;

      this.processingQuery = true;
      this.queryResponse = null;

      try {
        const response = await make_postrequest('/api/pm/team-allocation/query', {
          query: this.nlQuery,
          queried_by: 1 // TODO: Get from user context
        });

        if (response) {
          this.queryResponse = response;
        }
      } catch (err) {
        console.error('Error processing query:', err);
        useNotify({
          title: 'Error',
          text: 'Failed to process query',
          type: 'error'
        });
      } finally {
        this.processingQuery = false;
      }
    },

    async generateRecommendations() {
      this.generating = true;

      try {
        const response = await make_postrequest(
          `/api/pm/projects/${this.projectId}/team-allocation`,
          this.generateForm
        );

        if (response && response.message) {
          // Hide modal first
          if (this.generateModal) {
            this.generateModal.hide();
          }
          this.showGenerateModal = false;
          
          // Remove any lingering backdrops
          this.removeModalBackdrops();

          useNotify({
            title: 'Success',
            text: 'AI is analyzing project and generating recommendations...',
            type: 'success'
          });

          // Refresh after delay
          setTimeout(() => {
            this.fetchRecommendations();
          }, 5000);
        }
      } catch (err) {
        console.error('Error generating recommendations:', err);
        useNotify({
          title: 'Error',
          text: err.message || 'Failed to generate recommendations',
          type: 'error'
        });
      } finally {
        this.generating = false;
      }
    },

    async approveRecommendation(rec) {
      this.processing = true;

      try {
        const response = await make_putrequest(
          `/api/pm/allocation-recommendations/${rec.id}`,
          {
            action: 'approve',
            feedback: 'Approved by manager',
            reviewer_id: 1 // TODO: Get from user context
          }
        );

        if (response && response.message) {
          useNotify({
            title: 'Success',
            text: `${rec.employee_name} has been assigned to the project!`,
            type: 'success'
          });

          // Update local state
          rec.status = 'approved';
        }
      } catch (err) {
        console.error('Error approving recommendation:', err);
        useNotify({
          title: 'Error',
          text: 'Failed to approve recommendation',
          type: 'error'
        });
      } finally {
        this.processing = false;
      }
    },

    async rejectRecommendation(rec) {
      this.processing = true;

      try {
        const response = await make_putrequest(
          `/api/pm/allocation-recommendations/${rec.id}`,
          {
            action: 'reject',
            feedback: 'Not suitable for this project',
            reviewer_id: 1
          }
        );

        if (response && response.message) {
          useNotify({
            title: 'Success',
            text: 'Recommendation rejected',
            type: 'info'
          });

          rec.status = 'rejected';
        }
      } catch (err) {
        console.error('Error rejecting recommendation:', err);
        useNotify({
          title: 'Error',
          text: 'Failed to reject recommendation',
          type: 'error'
        });
      } finally {
        this.processing = false;
      }
    },

    viewDetails(rec) {
      this.selectedRecommendation = rec;
      if (!this.detailsModal) {
        this.detailsModal = new Modal(document.getElementById('detailsModal'));
      }
      this.detailsModal.show();
    },

    removeModalBackdrops() {
      // Remove all modal backdrops
      const backdrops = document.querySelectorAll('.modal-backdrop');
      backdrops.forEach(backdrop => backdrop.remove());
      
      // Remove modal-open class from body
      document.body.classList.remove('modal-open');
      
      // Reset body style
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
    },

    loadMore() {
      this.offset += this.limit;
      this.fetchRecommendations(true);
    },

    getCardClass(status) {
      if (status === 'approved') return 'border-success';
      if (status === 'rejected') return 'border-danger';
      return 'border-primary';
    },

    getProgressClass(score) {
      if (score >= 80) return 'bg-success';
      if (score >= 60) return 'bg-info';
      if (score >= 40) return 'bg-warning';
      return 'bg-danger';
    },

    getStatusBadgeClass(status) {
      const classes = {
        pending_review: 'badge bg-warning',
        approved: 'badge bg-success',
        rejected: 'badge bg-danger',
        auto_assigned: 'badge bg-info'
      };
      return classes[status] || 'badge bg-secondary';
    },

    formatStatus(status) {
      return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
  },
  mounted() {
    this.fetchRecommendations();

    // Initialize modals with proper configuration
    const generateModalEl = document.getElementById('generateModal');
    const detailsModalEl = document.getElementById('detailsModal');
    
    if (generateModalEl) {
      this.generateModal = new Modal(generateModalEl, {
        backdrop: true,
        keyboard: true,
        focus: true
      });
      
      // Handle modal close events
      generateModalEl.addEventListener('hidden.bs.modal', () => {
        this.showGenerateModal = false;
        this.removeModalBackdrops();
      });
      
      generateModalEl.addEventListener('shown.bs.modal', () => {
        this.showGenerateModal = true;
      });
    }
    
    if (detailsModalEl) {
      this.detailsModal = new Modal(detailsModalEl, {
        backdrop: true,
        keyboard: true,
        focus: true
      });
      
      detailsModalEl.addEventListener('hidden.bs.modal', () => {
        this.removeModalBackdrops();
      });
    }
  },
  beforeUnmount() {
    // Clean up modals and backdrops before component is destroyed
    if (this.generateModal) {
      this.generateModal.dispose();
    }
    if (this.detailsModal) {
      this.detailsModal.dispose();
    }
    this.removeModalBackdrops();
  },
  watch: {
    showGenerateModal(val) {
      if (val && this.generateModal) {
        this.$nextTick(() => {
          this.generateModal.show();
        });
      } else if (!val && this.generateModal) {
        this.generateModal.hide();
        this.removeModalBackdrops();
      }
    },
    projectId() {
      this.fetchRecommendations();
    }
  }
};
</script>

<style scoped>
.team-allocation-container {
  padding: 20px;
}

.bg-gradient-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.recommendation-card {
  transition: all 0.3s ease;
  border-width: 2px;
}

.recommendation-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.employee-avatar {
  color: #667eea;
}

.score-breakdown {
  font-size: 0.85rem;
}

.alert-sm {
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
}

/* Ensure modals appear above everything */
:deep(.modal) {
  z-index: 1055 !important;
}

:deep(.modal-backdrop) {
  z-index: 1050 !important;
}

:deep(.modal-dialog) {
  z-index: 1056 !important;
}

@media (max-width: 768px) {
  .col-md-6 {
    width: 100%;
  }
}
</style>
