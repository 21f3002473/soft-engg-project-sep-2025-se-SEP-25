<template>
    <div class="container-fluid py-4">
        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3 text-muted">Loading project details...</p>
        </div>

        <div v-else-if="error" class="alert alert-danger" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            {{ error }}
            <button class="btn btn-outline-danger btn-sm ms-3" @click="fetchProjectDetails">
                <i class="bi bi-arrow-clockwise me-1"></i>Retry
            </button>
        </div>

        <div v-else-if="project" class="row g-4">
            <div class="col-12">
                <div class="card shadow-sm">
                    <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                        <div>
                            <h4 class="mb-0">
                                <i class="bi bi-folder2-open me-2"></i>
                                {{ project.project_name }}
                            </h4>
                            <small>{{ project.project_id }}</small>
                        </div>
                        <div class="d-flex gap-2">
                            <button 
                                class="btn btn-outline-light btn-sm" 
                                @click="toggleEditMode"
                                v-if="!isEditing"
                            >
                                <i class="bi bi-pencil me-1"></i>Edit
                            </button>
                            <button 
                                class="btn btn-outline-danger btn-sm" 
                                @click="confirmDelete"
                                v-if="!isEditing"
                            >
                                <i class="bi bi-trash me-1"></i>Delete
                            </button>
                            <button 
                                class="btn btn-success btn-sm" 
                                @click="saveProject"
                                v-if="isEditing"
                                :disabled="saving"
                            >
                                <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                                <i v-else class="bi bi-check-lg me-1"></i>Save
                            </button>
                            <button 
                                class="btn btn-outline-light btn-sm" 
                                @click="cancelEdit"
                                v-if="isEditing"
                            >
                                <i class="bi bi-x-lg me-1"></i>Cancel
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
                            <i class="bi bi-check-circle me-2"></i>{{ successMessage }}
                            <button type="button" class="btn-close" @click="successMessage = null"></button>
                        </div>
                        <div v-if="updateError" class="alert alert-danger alert-dismissible fade show" role="alert">
                            <i class="bi bi-exclamation-triangle me-2"></i>{{ updateError }}
                            <button type="button" class="btn-close" @click="updateError = null"></button>
                        </div>

                        <div class="row">
                            <div class="col-md-8">
                                <div class="mb-3">
                                    <label class="form-label fw-bold">Project Name</label>
                                    <input 
                                        v-if="isEditing"
                                        type="text" 
                                        class="form-control" 
                                        v-model="editForm.project_name"
                                    >
                                    <p v-else class="mb-0">{{ project.project_name }}</p>
                                </div>

                                <div class="mb-3">
                                    <label class="form-label fw-bold">Description</label>
                                    <textarea 
                                        v-if="isEditing"
                                        class="form-control" 
                                        v-model="editForm.description"
                                        rows="4"
                                    ></textarea>
                                    <p v-else class="mb-0 text-muted">
                                        {{ project.description || 'No description available' }}
                                    </p>
                                </div>

                                <div class="mb-3">
                                    <label class="form-label fw-bold">Status</label>
                                    <select 
                                        v-if="isEditing"
                                        class="form-select" 
                                        v-model="editForm.status"
                                    >
                                        <option value="PENDING">Pending</option>
                                        <option value="IN_PROGRESS">In Progress</option>
                                        <option value="COMPLETED">Completed</option>
                                        <option value="ON_HOLD">On Hold</option>
                                        <option value="CANCELLED">Cancelled</option>
                                    </select>
                                    <span v-else :class="getStatusBadgeClass(project.status)">
                                        {{ formatStatus(project.status) }}
                                    </span>
                                </div>

                                <div class="mb-3" v-if="isEditing">
                                    <label class="form-label fw-bold">Manager ID (Optional)</label>
                                    <input 
                                        type="number" 
                                        class="form-control" 
                                        v-model.number="editForm.manager_id"
                                        placeholder="Enter manager ID"
                                    >
                                </div>
                            </div>

                            <div class="col-md-4">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 class="card-title fw-bold">
                                            <i class="bi bi-building me-2"></i>Client Information
                                        </h6>
                                        <div v-if="project.client">
                                            <p class="mb-1">
                                                <strong>Name:</strong> {{ project.client.name }}
                                            </p>
                                            <p class="mb-1">
                                                <strong>Client ID:</strong> {{ project.client.client_id }}
                                            </p>
                                            <p class="mb-0">
                                                <strong>Email:</strong> 
                                                <a :href="'mailto:' + project.client.email">
                                                    {{ project.client.email }}
                                                </a>
                                            </p>
                                        </div>
                                        <p v-else class="text-muted mb-0">No client assigned</p>

                                        <hr>

                                        <h6 class="card-title fw-bold">
                                            <i class="bi bi-list-check me-2"></i>Statistics
                                        </h6>
                                        <div class="mb-2">
                                            <span class="badge bg-primary rounded-pill me-2">
                                                {{ project.requirements_count }}
                                            </span>
                                            <span class="text-muted small">Requirements</span>
                                        </div>
                                        <div>
                                            <span class="badge bg-info rounded-pill me-2">
                                                {{ project.updates_count }}
                                            </span>
                                            <span class="text-muted small">Updates</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-12">
                <div class="card shadow-sm">
                    <div class="card-header bg-white">
                        <ul class="nav nav-tabs card-header-tabs" role="tablist">
                            <li class="nav-item" role="presentation">
                                <button 
                                    class="nav-link active" 
                                    id="requirements-tab" 
                                    data-bs-toggle="tab" 
                                    data-bs-target="#requirements" 
                                    type="button"
                                    role="tab"
                                >
                                    <i class="bi bi-clipboard-check me-1"></i>
                                    Requirements ({{ project.requirements_count }})
                                </button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button 
                                    class="nav-link" 
                                    id="updates-tab" 
                                    data-bs-toggle="tab" 
                                    data-bs-target="#updates" 
                                    type="button"
                                    role="tab"
                                >
                                    <i class="bi bi-megaphone me-1"></i>
                                    Updates ({{ project.updates_count }})
                                </button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button 
                                    class="nav-link" 
                                    id="daily-reports-tab" 
                                    data-bs-toggle="tab" 
                                    data-bs-target="#daily-reports" 
                                    type="button"
                                    role="tab"
                                >
                                    <i class="bi bi-calendar-check me-1"></i>
                                    Daily Reports
                                </button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button 
                                    class="nav-link" 
                                    id="team-allocation-tab" 
                                    data-bs-toggle="tab" 
                                    data-bs-target="#team-allocation" 
                                    type="button"
                                    role="tab"
                                >
                                    <i class="bi bi-people-fill me-1"></i>
                                    Team Allocation
                                </button>
                            </li>
                        </ul>
                    </div>
                    
                    <div class="tab-content">
                        <div class="tab-pane fade show active" id="requirements" role="tabpanel">
                            <div class="card-body">
                        <div v-if="project.requirements && project.requirements.length > 0" class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Requirement ID</th>
                                        <th>Description</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="req in project.requirements" :key="req.id">
                                        <td>
                                            <span class="badge bg-secondary">{{ req.requirement_id }}</span>
                                        </td>
                                        <td>{{ req.requirements }}</td>
                                        <td>
                                            <span :class="getStatusBadgeClass(req.status)">
                                                {{ formatStatus(req.status) }}
                                            </span>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <div v-else class="text-center text-muted py-4">
                            <i class="bi bi-inbox fs-1"></i>
                            <p class="mt-2">No requirements found for this project</p>
                        </div>
                            </div>
                        </div>

                        <div class="tab-pane fade" id="updates" role="tabpanel">
                            <div class="card-body">
                        <div v-if="project.updates && project.updates.length > 0" class="timeline">
                            <div 
                                v-for="update in project.updates" 
                                :key="update.id"
                                class="timeline-item mb-3 pb-3 border-bottom"
                            >
                                <div class="d-flex align-items-start">
                                    <div class="timeline-marker me-3">
                                        <i class="bi bi-circle-fill text-info"></i>
                                    </div>
                                    <div class="flex-grow-1">
                                        <div class="d-flex justify-content-between align-items-start mb-2">
                                            <h6 class="mb-0">
                                                <span class="badge bg-info me-2">{{ update.update_id }}</span>
                                            </h6>
                                            <small class="text-muted">
                                                <i class="bi bi-calendar3 me-1"></i>
                                                {{ formatDate(update.date) }}
                                            </small>
                                        </div>
                                        <p class="mb-1">{{ update.details }}</p>
                                        <small class="text-muted">
                                            <i class="bi bi-person me-1"></i>
                                            By: {{ update.created_by }}
                                        </small>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div v-else class="text-center text-muted py-4">
                            <i class="bi bi-inbox fs-1"></i>
                            <p class="mt-2">No updates found for this project</p>
                        </div>
                            </div>
                        </div>

                        <div class="tab-pane fade" id="daily-reports" role="tabpanel">
                            <ProjectDailyReports :projectId="projectId" />
                        </div>

                        <div class="tab-pane fade" id="team-allocation" role="tabpanel">
                            <TeamAllocationAssistant :projectId="projectId" />
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="modal fade" id="deleteConfirmModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-danger text-white">
                        <h5 class="modal-title">
                            <i class="bi bi-exclamation-triangle me-2"></i>Confirm Delete
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>Are you sure you want to delete this project?</p>
                        <p class="fw-bold mb-0">{{ project?.project_name }} ({{ project?.project_id }})</p>
                        <p class="text-danger small mt-2">
                            <i class="bi bi-exclamation-circle me-1"></i>
                            This action cannot be undone.
                        </p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button 
                            type="button" 
                            class="btn btn-danger" 
                            @click="deleteProject"
                            :disabled="deleting"
                        >
                            <span v-if="deleting" class="spinner-border spinner-border-sm me-1"></span>
                            <i v-else class="bi bi-trash me-1"></i>
                            {{ deleting ? 'Deleting...' : 'Delete Project' }}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { make_getrequest, make_putrequest, make_deleterequest } from '@/store/appState';
import { Modal } from 'bootstrap';
import ProjectDailyReports from './ProjectDailyReports.vue';
import TeamAllocationAssistant from './TeamAllocationAssistant.vue';

export default {
    name: 'SingleProjectView',
    components: {
        ProjectDailyReports,
        TeamAllocationAssistant
    },
    props: {
        projectId: {
            type: [String, Number],
            required: true
        }
    },
    data() {
        return {
            project: null,
            loading: true,
            error: null,
            isEditing: false,
            saving: false,
            deleting: false,
            successMessage: null,
            updateError: null,
            editForm: {
                project_name: '',
                description: '',
                status: '',
                manager_id: null
            },
            deleteModal: null
        };
    },
    methods: {
        async fetchProjectDetails() {
            this.loading = true;
            this.error = null;

            try {
                const response = await make_getrequest(`/api/pm/project/${this.projectId}`);
                console.log('Project Details Response:', response);

                if (response && response.data) {
                    this.project = response.data;
                } else {
                    this.error = 'Invalid response format';
                }
            } catch (err) {
                console.error('Error fetching project:', err);
                this.error = err.message || 'Failed to load project details';
            } finally {
                this.loading = false;
            }
        },
        toggleEditMode() {
            this.isEditing = true;
            this.editForm = {
                project_name: this.project.project_name,
                description: this.project.description,
                status: this.project.status,
                manager_id: this.project.manager_id || null
            };
        },
        cancelEdit() {
            this.isEditing = false;
            this.updateError = null;
        },
        async saveProject() {
            this.saving = true;
            this.successMessage = null;
            this.updateError = null;

            try {
                const payload = { ...this.editForm };
                if (!payload.manager_id) {
                    delete payload.manager_id;
                }

                const response = await make_putrequest(`/api/pm/project/${this.projectId}`, payload);
                console.log('Update Project Response:', response);

                if (response && response.data) {
                    this.project = response.data;
                    this.successMessage = response.message || 'Project updated successfully!';
                    this.isEditing = false;
                } else {
                    this.updateError = response.message || 'Failed to update project';
                }
            } catch (err) {
                console.error('Error updating project:', err);
                this.updateError = err.message || 'An error occurred while updating the project';
            } finally {
                this.saving = false;
            }
        },
        confirmDelete() {
            if (!this.deleteModal) {
                this.deleteModal = new Modal(document.getElementById('deleteConfirmModal'));
            }
            this.deleteModal.show();
        },
        async deleteProject() {
            this.deleting = true;

            try {
                const response = await make_deleterequest(`/api/pm/project/${this.projectId}`);
                console.log('Delete Project Response:', response);

                if (response && response.message) {
                    this.deleteModal.hide();
                    this.$router.push({ name: 'ProductManagerProjectDetails' });
                } else {
                    this.updateError = response.message || 'Failed to delete project';
                }
            } catch (err) {
                console.error('Error deleting project:', err);
                this.updateError = err.message || 'An error occurred while deleting the project';
            } finally {
                this.deleting = false;
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
            } else if (statusLower === 'on_hold') {
                return 'badge bg-secondary';
            } else if (statusLower === 'cancelled') {
                return 'badge bg-danger';
            }
            return 'badge bg-secondary';
        },
        formatStatus(status) {
            if (!status) return 'N/A';
            return status.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
        },
        formatDate(dateString) {
            if (!dateString) return 'N/A';
            try {
                const date = new Date(dateString);
                return date.toLocaleDateString('en-US', { 
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
        this.fetchProjectDetails();
    },
    watch: {
        projectId() {
            this.fetchProjectDetails();
        }
    }
};
</script>

<style scoped>
.card {
    transition: transform 0.2s ease;
}

.form-control:focus,
.form-select:focus {
    border-color: #0d6efd;
    box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}

textarea.form-control {
    resize: vertical;
    min-height: 100px;
}

.timeline-item {
    position: relative;
}

.timeline-marker {
    font-size: 0.5rem;
    padding-top: 0.25rem;
}

.table {
    margin-bottom: 0;
}

.table th {
    background-color: #f8f9fa;
    font-weight: 600;
}

.table td {
    vertical-align: middle;
}

.nav-tabs {
    border-bottom: 2px solid #dee2e6;
}

.nav-tabs .nav-link {
    color: #6c757d;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 12px 20px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.nav-tabs .nav-link:hover {
    color: #0d6efd;
    border-bottom-color: #0d6efd;
    background-color: transparent;
}

.nav-tabs .nav-link.active {
    color: #0d6efd;
    border-bottom: 2px solid #0d6efd;
    background-color: transparent;
}

.tab-content {
    padding: 0;
}

.tab-pane {
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
