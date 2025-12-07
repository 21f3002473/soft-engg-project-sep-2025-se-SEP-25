<template>
    <Teleport to="body">
        <div class="modal fade" id="addNewProjectModal" tabindex="-1" aria-labelledby="addNewProjectModalLabel"
            aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                <div class="modal-header bg-primary text-white">
                    <h5 class="modal-title" id="addNewProjectModalLabel">
                        <i class="bi bi-folder-plus me-2"></i>Add New Project
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"
                        aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="saveProject">
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="projectId" class="form-label">
                                    Project ID <span class="text-danger">*</span>
                                </label>
                                <div class="input-group">
                                    <input type="text" class="form-control" id="projectId"
                                        v-model="projectForm.project_id" placeholder="Auto-generated project ID"
                                        readonly>
                                    <button type="button" class="btn btn-outline-secondary" @click="generateProjectId"
                                        title="Regenerate ID">
                                        <i class="bi bi-arrow-clockwise"></i>
                                    </button>
                                </div>
                                <small class="text-muted">Auto-generated. Click to regenerate.</small>
                            </div>

                            <div class="col-md-6 mb-3">
                                <label for="projectName" class="form-label">
                                    Project Name <span class="text-danger">*</span>
                                </label>
                                <input type="text" class="form-control" id="projectName"
                                    v-model="projectForm.project_name" placeholder="Enter project name" required>
                            </div>
                        </div>

                        <div class="mb-3">
                            <label for="description" class="form-label">
                                Description <span class="text-danger">*</span>
                            </label>
                            <textarea class="form-control" id="description" v-model="projectForm.description"
                                placeholder="Enter project description" rows="3" required></textarea>
                        </div>

                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="status" class="form-label">
                                    Status <span class="text-danger">*</span>
                                </label>
                                <select class="form-select" id="status" v-model="projectForm.status" required>
                                    <option value="" disabled>Select status</option>
                                    <option value="PENDING">Pending</option>
                                    <option value="IN_PROGRESS">In Progress</option>
                                    <option value="COMPLETED">Completed</option>
                                    <option value="ON_HOLD">On Hold</option>
                                    <option value="CANCELLED">Cancelled</option>
                                </select>
                            </div>

                            <div class="col-md-6 mb-3">
                                <label for="clientId" class="form-label">
                                    Client <span class="text-danger">*</span>
                                </label>
                                <select class="form-select" id="clientId" v-model="projectForm.client_id" required
                                    :disabled="clientsLoading">
                                    <option value="" disabled>
                                        {{ clientsLoading ? 'Loading clients...' : 'Select a client' }}
                                    </option>
                                    <option v-for="client in clients" :key="client.id" :value="client.id">
                                        {{ client.client_name }} ({{ client.client_id }})
                                    </option>
                                </select>
                                <small v-if="clients.length === 0 && !clientsLoading" class="text-muted">
                                    No clients available. Please add a client first.
                                </small>
                            </div>
                        </div>

                        <div class="mb-3">
                            <label for="managerId" class="form-label">
                                Manager ID <span class="text-muted">(Optional)</span>
                            </label>
                            <input type="number" class="form-control" id="managerId"
                                v-model.number="projectForm.manager_id" placeholder="Enter manager ID (optional)">
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="bi bi-x-lg me-1"></i>Close
                    </button>
                    <button type="button" class="btn btn-primary" @click="saveProject" :disabled="loading">
                        <span v-if="loading" class="spinner-border spinner-border-sm me-1" role="status"></span>
                        <i v-else class="bi bi-check-lg me-1"></i>
                        {{ loading ? 'Creating...' : 'Create Project' }}
                    </button>
                </div>
            </div>
        </div>
        </div>
    </Teleport>
</template>

<script>
import { make_postrequest, make_getrequest } from '@/store/appState';
import { useNotify } from '@/utils/useNotify';
import bootstrap from 'bootstrap';
export default {
    name: 'AddNewProjectModal',
    data() {
        return {
            projectForm: {
                project_id: '',
                project_name: '',
                description: '',
                status: '',
                client_id: '',
                manager_id: null
            },
            clients: [],
            clientsLoading: false,
            loading: false
        };
    },
    setup() {
        const notify = useNotify();
        return { notify };
    },
    methods: {
        generateProjectId() {
            const uuid = crypto.randomUUID().split('-')[0].toUpperCase();
            this.projectForm.project_id = `PRJ-${uuid}`;
        },
        async fetchClients() {
            this.clientsLoading = true;
            try {
                const response = await make_getrequest('/api/pm/clients');
                console.log('Clients Response:', response);

                if (response && response.data && response.data.clients) {
                    this.clients = response.data.clients;
                } else if (response && response.clients) {
                    this.clients = response.clients;
                } else {
                    this.clients = [];
                }

                console.log('Loaded clients:', this.clients);
            } catch (error) {
                console.error('Error fetching clients:', error);
                this.notify.error('Failed to load clients');
                this.clients = [];
            } finally {
                this.clientsLoading = false;
            }
        },
        async saveProject() {
            this.loading = true;

            try {
                const payload = { ...this.projectForm };
                if (!payload.manager_id) {
                    delete payload.manager_id;
                }
                payload.client_id = parseInt(payload.client_id);

                const response = await make_postrequest('/api/pm/projects', payload);
                console.log('Create Project Response:', response);

                if (response && response.data) {
                    this.notify.success(response.message || 'Project created successfully!');
                    this.resetForm();
                    this.$emit('project-created', response.data);

                    const modalElement = document.getElementById('addNewProjectModal');
                    const modalInstance = bootstrap.Modal.getInstance(modalElement);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                } else {
                    throw new Error(response.message || 'Failed to create project');
                }
            } catch (error) {
                console.error('Error creating project:', error);
                this.notify.error(error.message || 'An error occurred while creating the project');
            } finally {
                this.loading = false;
            }
        },
        resetForm() {
            this.projectForm = {
                project_id: '',
                project_name: '',
                description: '',
                status: '',
                client_id: '',
                manager_id: null
            };
            this.generateProjectId();
        }
    },
    mounted() {
        this.generateProjectId();

        this.fetchClients();

        const modal = document.getElementById('addNewProjectModal');
        if (modal) {
            modal.addEventListener('show.bs.modal', () => {
                this.fetchClients();
                this.generateProjectId();
            });
        }
    }
};
</script>

<style scoped>
.modal-body {
    max-height: 70vh;
    overflow-y: auto;
}

.form-control:focus,
.form-select:focus {
    border-color: #0d6efd;
    box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}

textarea.form-control {
    resize: vertical;
    min-height: 80px;
}
</style>