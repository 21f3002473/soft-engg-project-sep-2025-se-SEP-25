<template>
  <div class="container-fluid py-4">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3 text-muted">Loading client details...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
    </div>

    <!-- Main Content -->
    <div v-else class="row g-4">
      
      <!-- Client Info Sidebar -->
      <div class="col-lg-3 col-md-4">
        <div class="card shadow-sm">
          <div class="card-body text-center">
            <img
              :src="`https://dummyjson.com/icon/${encodeURIComponent(clientData?.client_name || 'client')}/150`"
              :alt="clientData?.client_name"
              class="img-fluid rounded-circle mb-3 border border-3 border-primary"
              style="width: 150px; height: 150px; object-fit: cover;"
            />
            <h4 class="card-title mb-1">{{ clientData?.client_name || 'N/A' }}</h4>
            <p class="text-muted small mb-2">{{ clientData?.client_id || 'N/A' }}</p>
            <p class="card-text text-muted small mb-3">
              <i class="bi bi-envelope me-1"></i>{{ clientData?.email || 'N/A' }}
            </p>
            
            <div v-if="clientData?.details" class="alert alert-info text-start small mb-0">
              <strong>Details:</strong>
              <p class="mb-0 mt-1">{{ decodedDetails }}</p>
            </div>

            <div class="mt-3 pt-3 border-top">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <span class="text-muted small">Total Requirements:</span>
                <span class="badge bg-primary rounded-pill">{{ totalRequirements }}</span>
              </div>
              
              <!-- Add Requirement Button -->
              <button 
                type="button" 
                class="btn btn-primary btn-sm w-100"
                data-bs-toggle="modal" 
                data-bs-target="#addRequirementModal"
              >
                <i class="bi bi-plus-lg me-1"></i>Add Requirement
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Requirements and Chat -->
      <div class="col-lg-9 col-md-8">
        <div class="card shadow-sm h-100">
          <div class="card-header bg-primary text-white">
            <h3 class="h5 mb-0">
              <i class="bi bi-list-check me-2"></i>
              Client Requirements
            </h3>
          </div>
          <div class="card-body">
            <div class="d-flex flex-column flex-md-row gap-3 align-items-start">
              
              <!-- Requirements List -->
              <div class="flex-md-shrink-0" style="min-width: 320px; max-width: 400px;">
                <div class="alert alert-light border mb-0" style="max-height: 500px; overflow-y: auto;">
                  <h6 class="text-primary mb-3">
                    <i class="bi bi-clipboard-check me-2"></i>
                    Requirements List
                  </h6>
                  
                  <div v-if="requirements.length === 0" class="text-center text-muted py-3">
                    <i class="bi bi-inbox fs-1"></i>
                    <p class="mb-0 mt-2">No requirements available</p>
                  </div>

                  <ul v-else class="list-group list-group-flush">
                    <li 
                      v-for="req in requirements" 
                      :key="req.id"
                      class="list-group-item px-0 py-3 requirement-item"
                    >
                      <div class="d-flex flex-column">
                        <div class="d-flex align-items-center justify-content-between mb-2">
                          <span class="badge bg-secondary">{{ req.requirement_id }}</span>
                          <div class="d-flex gap-2">
                            <span :class="getStatusBadgeClass(req.status)">
                              {{ formatStatus(req.status) }}
                            </span>
                            <div class="d-flex gap-1">
                              <button 
                                class="btn btn-sm btn-outline-primary" 
                                @click="editRequirement(req)"
                                title="Edit"
                              >
                                <i class="bi bi-pencil"></i>
                              </button>
                              <button 
                                class="btn btn-sm btn-outline-danger" 
                                @click="confirmDeleteRequirement(req)"
                                title="Delete"
                              >
                                <i class="bi bi-trash"></i>
                              </button>
                            </div>
                          </div>
                        </div>
                        <p class="mb-2 requirement-description">{{ req.description }}</p>
                        <div class="d-flex justify-content-between align-items-center">
                          <small class="text-muted">
                            <i class="bi bi-diagram-3 me-1"></i>
                            {{ req.project_name || req.project_id }}
                          </small>
                        </div>
                      </div>
                    </li>
                  </ul>
                </div>
              </div>

              <!-- AI Chatbot -->
              <div class="flex-fill border rounded p-3 bg-light" style="min-height: 500px;">
                <div class="d-flex align-items-center mb-3 pb-2 border-bottom">
                  <i class="bi bi-robot text-primary me-2 fs-5"></i>
                  <h5 class="mb-0">AI Assistant</h5>
                  <span class="badge bg-success ms-auto">Online</span>
                </div>
                <ProductMangerChatbot :clientId="clientId" :clientName="clientData?.client_name" />
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Requirement Modal -->
    <AddRequirementModal 
      :clientId="clientId" 
      @requirement-created="onRequirementCreated" 
    />

    <!-- Edit Requirement Modal -->
    <div class="modal fade" id="editRequirementModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">
              <i class="bi bi-pencil me-2"></i>Edit Requirement
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <!-- Success/Error Messages -->
            <div v-if="editSuccessMessage" class="alert alert-success alert-dismissible fade show" role="alert">
              <i class="bi bi-check-circle me-2"></i>{{ editSuccessMessage }}
              <button type="button" class="btn-close" @click="editSuccessMessage = null"></button>
            </div>
            <div v-if="editErrorMessage" class="alert alert-danger alert-dismissible fade show" role="alert">
              <i class="bi bi-exclamation-triangle me-2"></i>{{ editErrorMessage }}
              <button type="button" class="btn-close" @click="editErrorMessage = null"></button>
            </div>

            <form @submit.prevent="saveRequirement">
              <div class="mb-3">
                <label class="form-label">Requirement ID</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="editForm.requirement_id"
                  readonly
                >
              </div>

              <div class="mb-3">
                <label class="form-label">Project</label>
                <input 
                  type="text" 
                  class="form-control" 
                  :value="editForm.project_name || editForm.project_id"
                  readonly
                >
                <small class="text-muted">Project assignment cannot be changed</small>
              </div>

              <div class="mb-3">
                <label class="form-label">Status <span class="text-danger">*</span></label>
                <select 
                  class="form-select" 
                  v-model="editForm.status"
                  required
                >
                  <option value="" disabled>Select status</option>
                  <option value="PENDING">Pending</option>
                  <option value="IN_PROGRESS">In Progress</option>
                  <option value="COMPLETED">Completed</option>
                </select>
              </div>

              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea 
                  class="form-control" 
                  v-model="editForm.requirements"
                  rows="4"
                  readonly
                ></textarea>
                <small class="text-muted">Description cannot be changed</small>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="saveRequirement"
              :disabled="editSaving"
            >
              <span v-if="editSaving" class="spinner-border spinner-border-sm me-1"></span>
              {{ editSaving ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteRequirementModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-danger text-white">
            <h5 class="modal-title">
              <i class="bi bi-exclamation-triangle me-2"></i>Confirm Delete
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete this requirement?</p>
            <p class="fw-bold mb-0">{{ requirementToDelete?.requirement_id }}</p>
            <p class="text-muted small mt-1">{{ requirementToDelete?.description }}</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button 
              type="button" 
              class="btn btn-danger" 
              @click="deleteRequirement"
              :disabled="deleting"
            >
              <span v-if="deleting" class="spinner-border spinner-border-sm me-1"></span>
              {{ deleting ? 'Deleting...' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ProductMangerChatbot from './fragments/ProductMangerChatbot.vue';
import AddRequirementModal from './fragments/AddRequirementModal.vue';
import { make_getrequest, make_putrequest, make_deleterequest } from '@/store/appState';
import { Modal } from 'bootstrap';

export default {
  name: 'ProductMangerClientRequirements',
  props: {
    clientId: {
      type: [String, Number],
      required: true
    }
  },
  components: {
    ProductMangerChatbot,
    AddRequirementModal
  },
  data() {
    return {
      clientData: null,
      requirements: [],
      totalRequirements: 0,
      loading: true,
      error: null,
      editForm: {
        id: null,
        requirement_id: '',
        project_id: '',
        project_name: '',
        requirements: '',
        status: ''
      },
      editProjects: [],
      editProjectsLoading: false,
      editSaving: false,
      deleting: false,
      editSuccessMessage: null,
      editErrorMessage: null,
      requirementToDelete: null,
      editModal: null,
      deleteModal: null
    };
  },
  computed: {
    decodedDetails() {
      if (!this.clientData?.details) return 'N/A';
      try {
        // Decode base64 encoded details
        return atob(this.clientData.details);
      } catch (e) {
        console.error('Error decoding details:', e);
        return this.clientData.details;
      }
    }
  },
  methods: {
    async fetchClientDetails() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await make_getrequest(`/api/pm/client/requirements/${this.clientId}`);
        
        console.log('Client Details Response:', response);
        
        // Extract data from nested response.data structure
        const responseData = response?.data || {};
        
        this.clientData = responseData?.client || null;
        this.requirements = responseData?.requirements || [];
        this.totalRequirements = responseData?.total_requirements || this.requirements.length;
        
        console.log('Processed Client Data:', this.clientData);
        console.log('Processed Requirements:', this.requirements);
        
      } catch (error) {
        console.error('Error fetching client details:', error);
        this.error = error.message || 'Failed to load client details. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    async fetchEditProjects() {
      this.editProjectsLoading = true;
      try {
        const response = await make_getrequest(`/api/pm/projects?id_client=${this.clientId}`);
        
        if (response && response.data && response.data.projects) {
          this.editProjects = response.data.projects;
        } else {
          this.editProjects = [];
        }
      } catch (error) {
        console.error('Error fetching projects:', error);
        this.editProjects = [];
      } finally {
        this.editProjectsLoading = false;
      }
    },
    editRequirement(requirement) {
      this.editForm = {
        id: requirement.id,
        requirement_id: requirement.requirement_id,
        project_id: requirement.project_id,
        project_name: requirement.project_name,
        requirements: requirement.description,
        status: requirement.status || 'PENDING'
      };
      
      if (!this.editModal) {
        this.editModal = new Modal(document.getElementById('editRequirementModal'));
      }
      this.editModal.show();
    },
    async saveRequirement() {
      this.editSaving = true;
      this.editSuccessMessage = null;
      this.editErrorMessage = null;

      try {
        const payload = {
          status: this.editForm.status
        };

        const response = await make_putrequest(
          `/api/pm/client/requirements/${this.clientId}/${this.editForm.id}`,
          payload
        );

        if (response && response.data) {
          this.editSuccessMessage = response.message || 'Requirement status updated successfully!';
          this.fetchClientDetails();
          setTimeout(() => {
            this.editModal?.hide();
            this.editSuccessMessage = null;
          }, 1500);
        } else {
          this.editErrorMessage = response.message || 'Failed to update requirement';
        }
      } catch (error) {
        console.error('Error updating requirement:', error);
        this.editErrorMessage = error.message || 'An error occurred while updating the requirement';
      } finally {
        this.editSaving = false;
      }
    },
    confirmDeleteRequirement(requirement) {
      this.requirementToDelete = requirement;
      
      if (!this.deleteModal) {
        this.deleteModal = new Modal(document.getElementById('deleteRequirementModal'));
      }
      this.deleteModal.show();
    },
    async deleteRequirement() {
      this.deleting = true;

      try {
        const response = await make_deleterequest(
          `/api/pm/client/requirements/${this.clientId}/${this.requirementToDelete.id}`
        );

        if (response && response.message) {
          this.deleteModal?.hide();
          this.fetchClientDetails();
        } else {
          this.error = response.message || 'Failed to delete requirement';
        }
      } catch (error) {
        console.error('Error deleting requirement:', error);
        this.error = error.message || 'An error occurred while deleting the requirement';
      } finally {
        this.deleting = false;
        this.requirementToDelete = null;
      }
    },
    getStatusBadgeClass(status) {
      const statusLower = status?.toLowerCase() || '';
      
      if (statusLower === 'completed') {
        return 'badge bg-success';
      } else if (statusLower === 'in_progress') {
        return 'badge bg-primary';
      } else if (statusLower === 'pending') {
        return 'badge bg-warning text-dark';
      } else if (statusLower === 'cancelled' || statusLower === 'on_hold') {
        return 'badge bg-danger';
      }
      return 'badge bg-secondary';
    },
    formatStatus(status) {
      if (!status) return 'N/A';
      return status.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
    },
    onRequirementCreated(newRequirement) {
      console.log('New requirement created:', newRequirement);
      // Refresh the requirements list
      this.fetchClientDetails();
    }
  },
  mounted() {
    this.fetchClientDetails();
  },
  watch: {
    clientId() {
      // Refetch if clientId changes
      this.fetchClientDetails();
    }
  }
}
</script>

<style scoped>
/* Custom scrollbar for requirements list */
.alert.alert-light::-webkit-scrollbar {
  width: 6px;
}

.alert.alert-light::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.alert.alert-light::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 10px;
}

.alert.alert-light::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.list-group-item {
  transition: background-color 0.2s ease;
}

.list-group-item:hover {
  background-color: #f8f9fa;
}

.requirement-item {
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
}

.requirement-item:hover {
  background-color: #f8f9fa;
  border-left-color: #0d6efd;
  transform: translateX(2px);
}

.requirement-description {
  font-size: 0.9rem;
  line-height: 1.5;
  color: #495057;
}

.badge {
  font-size: 0.75rem;
  padding: 0.35em 0.65em;
  font-weight: 600;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .card-body .border.rounded {
    min-height: 300px;
  }
  
  .flex-md-shrink-0 {
    min-width: 100% !important;
    max-width: 100% !important;
  }
}
</style>
