<template>
  <div class="product-manager-update-client">
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3 text-muted">Loading client updates...</p>
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
              <div class="d-flex justify-content-between align-items-center">
                <span class="text-muted small">Total Updates:</span>
                <span class="badge bg-primary rounded-pill">{{ totalUpdates }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-9 col-md-8">
        <ul class="nav nav-tabs mb-3" role="tablist">
          <li class="nav-item" role="presentation">
            <button class="nav-link active" id="updates-tab" data-bs-toggle="tab" data-bs-target="#updates-content"
              type="button" role="tab">
              <i class="bi bi-bell-fill me-1"></i>
              Updates
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="emails-tab" data-bs-toggle="tab" data-bs-target="#emails-content" type="button"
              role="tab">
              <i class="bi bi-envelope-check me-1"></i>
              Email History
            </button>
          </li>
        </ul>

        <div class="tab-content">
          <div class="tab-pane fade show active" id="updates-content" role="tabpanel">
            <div class="card shadow-sm h-100">
              <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                <h3 class="h5 mb-0">
                  <i class="bi bi-bell-fill me-2"></i>
                  Client Updates
                </h3>
                <button type="button" class="btn btn-light btn-sm" data-bs-toggle="modal"
                  data-bs-target="#addUpdateModal">
                  <i class="bi bi-plus-lg me-1"></i>Add Update
                </button>
              </div>
              <div class="card-body">
                <!-- Updates List (Full Width) -->
                <div class="alert alert-light border mb-0" style="max-height: 500px; overflow-y: auto;">
                  <h6 class="text-primary mb-3">
                    <i class="bi bi-calendar-check me-2"></i>
                    Updates List ({{ totalUpdates }})
                  </h6>

                  <div v-if="updates.length === 0" class="text-center text-muted py-3">
                    <i class="bi bi-inbox fs-1"></i>
                    <p class="mb-0 mt-2">No updates available</p>
                  </div>

                  <ul v-else class="list-group list-group-flush">
                    <li v-for="update in updates" :key="update.id" class="list-group-item px-0 py-3">
                      <div class="d-flex flex-column">
                        <div class="d-flex align-items-center justify-content-between mb-2">
                          <span class="badge bg-secondary">{{ update.update_id }}</span>
                          <div class="d-flex gap-1">
                            <button class="btn btn-sm btn-outline-primary" @click="editUpdate(update)" title="Edit">
                              <i class="bi bi-pencil me-1"></i>Edit
                            </button>
                            <button class="btn btn-sm btn-outline-danger" @click="confirmDeleteUpdate(update)"
                              title="Delete">
                              <i class="bi bi-trash me-1"></i>Delete
                            </button>
                          </div>
                        </div>
                        <p class="mb-1 small">{{ update.description }}</p>
                        <div class="d-flex flex-wrap gap-2">
                          <small class="text-muted">
                            <i class="bi bi-calendar3 me-1"></i>
                            {{ formatDate(update.date) }}
                          </small>
                          <small class="text-muted">
                            <i class="bi bi-folder me-1"></i>
                            Project: {{ update.project_id }}
                          </small>
                          <small class="text-muted">
                            <i class="bi bi-person me-1"></i>
                            By: {{ update.created_by }}
                          </small>
                        </div>
                      </div>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div class="tab-pane fade" id="emails-content" role="tabpanel">
            <div v-if="clientData && clientProjects.length > 0">
              <ProductManagerEmailHistory :projectId="getFirstProjectId()" />
            </div>
            <div v-else class="alert alert-info">
              <i class="bi bi-info-circle me-2"></i>
              Client must have projects to view email history.
            </div>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div class="modal fade" id="addUpdateModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">
              <i class="bi bi-plus-circle me-2"></i>
              {{ isEditing ? 'Edit Update' : 'Add New Update' }}
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveUpdate">
              <div class="mb-3">
                <label class="form-label">Update ID <span class="text-danger">*</span></label>
                <div class="input-group">
                  <input type="text" class="form-control" v-model="updateForm.update_id" :readonly="isEditing" required>
                  <button v-if="!isEditing" type="button" class="btn btn-outline-secondary" @click="generateUpdateId">
                    <i class="bi bi-arrow-clockwise"></i>
                  </button>
                </div>
                <small class="text-muted">Auto-generated. Click to regenerate.</small>
              </div>

              <div class="mb-3" v-if="!isEditing">
                <label class="form-label">Project <span class="text-danger">*</span></label>
                <select class="form-select" v-model="updateForm.project_id" required :disabled="projectsLoading">
                  <option value="" disabled>
                    {{ projectsLoading ? 'Loading projects...' : 'Select a project' }}
                  </option>
                  <option v-for="project in clientProjects" :key="project.id" :value="project.id">
                    {{ project.project_name }} ({{ project.project_id }})
                  </option>
                </select>
              </div>

              <div class="mb-3">
                <label class="form-label">Details <span class="text-danger">*</span></label>
                <textarea class="form-control" v-model="updateForm.details" rows="4" required
                  placeholder="Enter update details"></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button type="button" class="btn btn-primary" @click="saveUpdate" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
              {{ saving ? 'Saving...' : 'Save Update' }}
            </button>
          </div>
          </div>
        </div>
      </div>
    </Teleport>


  </div>
</template>

<script>
import ProductManagerEmailHistory from './fragments/ProductManagerEmailHistory.vue';
import { make_getrequest, make_postrequest, make_putrequest, make_deleterequest } from '@/store/appState';
import { Modal } from 'bootstrap';
import Swal from 'sweetalert2';
import { useNotify } from '@/utils/useNotify';

export default {
  name: "ProductMangerUpdateClient",
  props: {
    clientID: {
      type: [String, Number],
      required: true
    }
  },
  components: {
    ProductManagerEmailHistory
  },
  data() {
    return {
      clientData: null,
      updates: [],
      totalUpdates: 0,
      clientProjects: [],
      projectsLoading: false,
      loading: true,
      error: null,
      isEditing: false,
      saving: false,
      updateForm: {
        update_id: '',
        project_id: '',
        details: ''
      },
      addUpdateModal: null
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
        return this.clientData.details;
      }
    }
  },
  methods: {
    async fetchClientUpdates() {
      this.loading = true;
      this.error = null;

      try {
        const response = await make_getrequest(`/api/pm/client/updates/${this.clientID}`);

        console.log('Client Updates Response:', response);

        const responseData = response?.data || {};

        this.clientData = responseData?.client || null;
        this.updates = responseData?.updates || [];
        this.totalUpdates = responseData?.total_updates || this.updates.length;

        console.log('Processed Client Data:', this.clientData);
        console.log('Processed Updates:', this.updates);

      } catch (error) {
        console.error('Error fetching client updates:', error);
        this.error = error.message || 'Failed to load client updates. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    async fetchClientProjects() {
      this.projectsLoading = true;
      try {
        const response = await make_getrequest(`/api/pm/projects?id_client=${this.clientID}`);

        if (response && response.data && response.data.projects) {
          this.clientProjects = response.data.projects;
        } else {
          this.clientProjects = [];
        }
      } catch (error) {
        console.error('Error fetching client projects:', error);
        this.clientProjects = [];
      } finally {
        this.projectsLoading = false;
      }
    },
    generateUpdateId() {
      const uuid = crypto.randomUUID().split('-')[0].toUpperCase();
      this.updateForm.update_id = `UPD-${uuid}`;
    },
    editUpdate(update) {
      this.isEditing = true;
      this.updateForm = {
        update_id: update.update_id,
        project_id: update.project_id,
        details: update.description,
        id: update.id
      };

      if (!this.addUpdateModal) {
        this.addUpdateModal = new Modal(document.getElementById('addUpdateModal'));
      }
      this.addUpdateModal.show();
    },
    async saveUpdate() {
      this.saving = true;

      try {
        let response;

        if (this.isEditing) {
          response = await make_putrequest(
            `/api/pm/client/updates/${this.clientID}/${this.updateForm.id}`,
            { details: this.updateForm.details }
          );
        } else {
          response = await make_postrequest(
            `/api/pm/client/updates/${this.clientID}`,
            {
              update_id: this.updateForm.update_id,
              project_id: this.updateForm.project_id,
              details: this.updateForm.details
            }
          );
        }

        if (response && response.data) {
          this.notify.success(response.message || 'Update saved successfully!');
          this.fetchClientUpdates();
          this.resetForm();
          this.addUpdateModal?.hide();
        } else {
          throw new Error(response.message || 'Failed to save update');
        }
      } catch (error) {
        console.error('Error saving update:', error);
        this.notify.error(error.message || 'An error occurred while saving the update');
      } finally {
        this.saving = false;
      }
    },
    confirmDeleteUpdate(update) {
      Swal.fire({
        title: 'Are you sure?',
        text: `You are about to delete update ${update.update_id}`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Yes, delete it!'
      }).then((result) => {
        if (result.isConfirmed) {
          this.deleteUpdate(update);
        }
      });
    },
    async deleteUpdate(update) {
      try {
        const response = await make_deleterequest(
          `/api/pm/client/updates/${this.clientID}/${update.id}`
        );

        if (response && response.message) {
          this.notify.success(response.message || 'Update deleted successfully!');
          this.fetchClientUpdates();
        } else {
          throw new Error(response.message || 'Failed to delete update');
        }
      } catch (error) {
        console.error('Error deleting update:', error);
        this.notify.error(error.message || 'An error occurred while deleting the update');
      }
    },
    resetForm() {
      this.isEditing = false;
      this.updateForm = {
        update_id: '',
        project_id: '',
        details: ''
      };
      this.generateUpdateId();
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        });
      } catch (e) {
        return dateString;
      }
    },
    getFirstProjectId() {
      if (this.clientProjects && this.clientProjects.length > 0) {
        return this.clientProjects[0].id;
      }
      return null;
    }
  },
  mounted() {
    this.fetchClientUpdates();
    this.fetchClientProjects();
    this.generateUpdateId();

    const addModalEl = document.getElementById('addUpdateModal');
    if (addModalEl) {
      addModalEl.addEventListener('show.bs.modal', () => {
        if (!this.isEditing) {
          this.fetchClientProjects();
          this.generateUpdateId();
        }
      });
      addModalEl.addEventListener('hidden.bs.modal', () => {
        this.resetForm();
      });
    }
  },
  watch: {
    clientID() {
      this.fetchClientUpdates();
    }
  }
}
</script>

<style scoped>
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