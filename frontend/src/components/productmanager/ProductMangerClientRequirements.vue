<template>
  <div class="product-manager-client-requirements">
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3 text-muted">Loading client details...</p>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
    </div>

    <div v-else class="row g-4">
      <div class="col-lg-3 col-md-4">
        <div class="card shadow-sm">
          <div class="card-body text-center">
            <img :src="`https://dummyjson.com/icon/${encodeURIComponent(clientData?.client_name || 'client')}/150`"
              :alt="clientData?.client_name" class="img-fluid rounded-circle mb-3 border border-3 border-primary"
              style="width: 150px; height: 150px; object-fit: cover;" />
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

              <button type="button" class="btn btn-primary btn-sm w-100" data-bs-toggle="modal"
                data-bs-target="#addRequirementModal">
                <i class="bi bi-plus-lg me-1"></i>Add Requirement
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-9 col-md-8">
        <ul class="nav nav-tabs mb-3" role="tablist">
          <li class="nav-item" role="presentation">
            <button class="nav-link active" id="requirements-tab" data-bs-toggle="tab"
              data-bs-target="#requirements-content" type="button" role="tab">
              <i class="bi bi-list-check me-1"></i>
              Requirements & Chat
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="roadmap-tab" data-bs-toggle="tab" data-bs-target="#roadmap-content"
              type="button" role="tab">
              <i class="bi bi-map me-1"></i>
              Project Roadmap
            </button>
          </li>
        </ul>

        <div class="tab-content">
          <div class="tab-pane fade show active" id="requirements-content" role="tabpanel">
            <div class="card shadow-sm h-100">
              <div class="card-header bg-primary text-white">
                <h3 class="h5 mb-0">
                  <i class="bi bi-list-check me-2"></i>
                  Client Requirements
                </h3>
              </div>
              <div class="card-body">
                <div class="requirements-wrapper">
                  <h6 class="text-primary mb-3">
                    <i class="bi bi-clipboard-check me-2"></i>
                    Requirements List
                  </h6>

                  <div v-if="requirements.length === 0" class="text-center text-muted py-5">
                    <i class="bi bi-inbox fs-1"></i>
                    <p class="mb-0 mt-2">No requirements available</p>
                  </div>

                  <div v-else class="row g-3">
                    <div v-for="req in requirements" :key="req.id" class="col-12 col-md-6 col-lg-4 col-xl-3">
                      <div class="requirement-card">
                        <div class="requirement-header">
                          <span class="badge bg-secondary">{{ req.requirement_id }}</span>
                          <span :class="getStatusBadgeClass(req.status)">
                            {{ formatStatus(req.status) }}
                          </span>
                        </div>

                        <div class="requirement-body">
                          <p class="requirement-description">{{ req.description }}</p>
                          <small class="text-muted d-block">
                            <i class="bi bi-diagram-3 me-1"></i>
                            {{ req.project_name || req.project_id }}
                          </small>
                        </div>

                        <div class="requirement-actions">
                          <button class="btn btn-sm btn-outline-primary" @click="editRequirement(req)"
                            title="Edit Status">
                            <i class="bi bi-pencil"></i>
                          </button>
                          <button class="btn btn-sm btn-outline-danger" @click="confirmDeleteRequirement(req)"
                            title="Delete">
                            <i class="bi bi-trash"></i>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="tab-pane fade" id="roadmap-content" role="tabpanel">
            <div v-if="clientData && requirements.length > 0">
              <ProductManagerRoadmap :projectId="getProjectId()" :clientId="clientId" />
            </div>
            <div v-else class="alert alert-info">
              <i class="bi bi-info-circle me-2"></i>
              Add requirements first to generate a project roadmap.
            </div>
          </div>
        </div>
      </div>
    </div>

    <AddRequirementModal :clientId="clientId" @requirement-created="onRequirementCreated" />

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
            <form @submit.prevent="saveRequirement">
              <div class="mb-3">
                <label class="form-label">Requirement ID</label>
                <input type="text" class="form-control" v-model="editForm.requirement_id" readonly>
              </div>

              <div class="mb-3">
                <label class="form-label">Project</label>
                <input type="text" class="form-control" :value="editForm.project_name || editForm.project_id" readonly>
                <small class="text-muted">Project assignment cannot be changed</small>
              </div>

              <div class="mb-3">
                <label class="form-label">Status <span class="text-danger">*</span></label>
                <select class="form-select" v-model="editForm.status" required>
                  <option value="" disabled>Select status</option>
                  <option value="PENDING">Pending</option>
                  <option value="IN_PROGRESS">In Progress</option>
                  <option value="COMPLETED">Completed</option>
                </select>
              </div>

              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea class="form-control" v-model="editForm.requirements" rows="4" readonly></textarea>
                <small class="text-muted">Description cannot be changed</small>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button type="button" class="btn btn-primary" @click="saveRequirement" :disabled="editSaving">
              <span v-if="editSaving" class="spinner-border spinner-border-sm me-1"></span>
              {{ editSaving ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </div>
      </div>
    </div>


  </div>
</template>

<script>
import ProductManagerRoadmap from './fragments/ProductManagerRoadmap.vue';
import AddRequirementModal from './fragments/AddRequirementModal.vue';
import { make_getrequest, make_putrequest, make_deleterequest } from '@/store/appState';
import { Modal } from 'bootstrap';
import Swal from 'sweetalert2';
import { useNotify } from '@/utils/useNotify';

export default {
  name: 'ProductMangerClientRequirements',
  props: {
    clientId: {
      type: [String, Number],
      required: true
    }
  },
  components: {
    ProductManagerRoadmap,
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
      editModal: null
    };
  },
  setup() {
    const notify = useNotify();
    return { notify };
  },
  computed: {
    decodedDetails() {
      if (!this.clientData?.details) return 'N/A';
      try {
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

      try {
        const payload = {
          status: this.editForm.status
        };

        const response = await make_putrequest(
          `/api/pm/client/requirements/${this.clientId}/${this.editForm.id}`,
          payload
        );

        if (response && response.data) {
          this.notify.success(response.message || 'Requirement status updated successfully!');
          this.fetchClientDetails();
          this.editModal?.hide();
        } else {
          throw new Error(response.message || 'Failed to update requirement');
        }
      } catch (error) {
        console.error('Error updating requirement:', error);
        this.notify.error(error.message || 'An error occurred while updating the requirement');
      } finally {
        this.editSaving = false;
      }
    },
    confirmDeleteRequirement(requirement) {
      Swal.fire({
        title: 'Are you sure?',
        text: `You are about to delete requirement ${requirement.requirement_id}`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Yes, delete it!'
      }).then((result) => {
        if (result.isConfirmed) {
          this.deleteRequirement(requirement);
        }
      });
    },
    async deleteRequirement(requirement) {
      try {
        const response = await make_deleterequest(
          `/api/pm/client/requirements/${this.clientId}/${requirement.id}`
        );

        if (response && response.message) {
          this.notify.success(response.message || 'Requirement deleted successfully');
          this.fetchClientDetails();
        } else {
          throw new Error(response.message || 'Failed to delete requirement');
        }
      } catch (error) {
        console.error('Error deleting requirement:', error);
        this.notify.error(error.message || 'An error occurred while deleting the requirement');
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
      this.fetchClientDetails();
    },
    getProjectId() {
      if (this.requirements && this.requirements.length > 0) {
        return this.requirements[0].project_id;
      }
      return null;
    }
  },
  mounted() {
    this.fetchClientDetails();
  },
  watch: {
    clientId() {
      this.fetchClientDetails();
    }
  }
}
</script>

<style scoped>
.requirements-wrapper {
  padding: 1rem;
}

.requirement-card {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  border-left: 4px solid #dee2e6;
}

.requirement-card:hover {
  border-left-color: #0d6efd;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.requirement-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.requirement-body {
  flex-grow: 1;
  margin-bottom: 0.75rem;
}

.requirement-description {
  font-size: 0.9rem;
  line-height: 1.5;
  color: #495057;
  margin-bottom: 0.5rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.requirement-actions {
  display: flex;
  gap: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid #e9ecef;
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
  .requirement-card {
    margin-bottom: 1rem;
  }
}
</style>
