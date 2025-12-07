<template>
    <div class="modal fade" id="addRequirementModal" tabindex="-1" aria-labelledby="addRequirementModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header bg-primary text-white">
                    <h5 class="modal-title" id="addRequirementModalLabel">
                        <i class="bi bi-plus-circle me-2"></i>Add New Requirement
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <!-- Success Alert -->
                    <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
                        <i class="bi bi-check-circle me-2"></i>{{ successMessage }}
                        <button type="button" class="btn-close" @click="successMessage = null"></button>
                    </div>
                    
                    <!-- Error Alert -->
                    <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show" role="alert">
                        <i class="bi bi-exclamation-triangle me-2"></i>{{ errorMessage }}
                        <button type="button" class="btn-close" @click="errorMessage = null"></button>
                    </div>

                    <form @submit.prevent="saveRequirement">
                        <div class="mb-3">
                            <label for="requirementId" class="form-label">
                                Requirement ID <span class="text-danger">*</span>
                            </label>
                            <div class="input-group">
                                <input 
                                    type="text" 
                                    class="form-control" 
                                    id="requirementId" 
                                    v-model="requirementForm.requirement_id"
                                    placeholder="Auto-generated requirement ID"
                                    readonly
                                >
                                <button 
                                    type="button" 
                                    class="btn btn-outline-secondary" 
                                    @click="generateRequirementId"
                                    title="Regenerate ID"
                                >
                                    <i class="bi bi-arrow-clockwise"></i>
                                </button>
                            </div>
                            <small class="text-muted">Auto-generated. Click to regenerate.</small>
                        </div>
                        
                        <div class="mb-3">
                            <label for="projectId" class="form-label">
                                Project <span class="text-danger">*</span>
                            </label>
                            <select 
                                class="form-select" 
                                id="projectId" 
                                v-model="requirementForm.project_id"
                                required
                                :disabled="projectsLoading"
                            >
                                <option value="" disabled>
                                    {{ projectsLoading ? 'Loading projects...' : 'Select a project' }}
                                </option>
                                <option 
                                    v-for="project in projects" 
                                    :key="project.id" 
                                    :value="project.project_id"
                                >
                                    {{ project.project_name }} ({{ project.project_id }})
                                </option>
                            </select>
                            <small v-if="projects.length === 0 && !projectsLoading" class="text-muted">
                                No projects available for this client. Please add a project first.
                            </small>
                        </div>
                        
                        <div class="mb-3">
                            <label for="requirements" class="form-label">
                                Requirement Description <span class="text-danger">*</span>
                            </label>
                            <textarea 
                                class="form-control" 
                                id="requirements" 
                                v-model="requirementForm.requirements"
                                placeholder="Enter detailed requirement description"
                                rows="4"
                                required
                            ></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="bi bi-x-lg me-1"></i>Close
                    </button>
                    <button 
                        type="button" 
                        class="btn btn-primary" 
                        @click="saveRequirement"
                        :disabled="loading"
                    >
                        <span v-if="loading" class="spinner-border spinner-border-sm me-1" role="status"></span>
                        <i v-else class="bi bi-check-lg me-1"></i>
                        {{ loading ? 'Saving...' : 'Save Requirement' }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { make_postrequest, make_getrequest } from '@/store/appState';

export default {
    name: 'AddRequirementModal',
    props: {
        clientId: {
            type: [String, Number],
            required: true
        }
    },
    data() {
        return {
            requirementForm: {
                requirement_id: '',
                project_id: '',
                requirements: ''
            },
            projects: [],
            projectsLoading: false,
            loading: false,
            successMessage: null,
            errorMessage: null
        };
    },
    methods: {
        generateRequirementId() {
            // Generate a short UUID and prefix with 'REQ-'
            const uuid = crypto.randomUUID().split('-')[0].toUpperCase();
            this.requirementForm.requirement_id = `REQ-${uuid}`;
        },
        async fetchProjects() {
            this.projectsLoading = true;
            try {
                // Fetch projects filtered by client ID
                const response = await make_getrequest(`/api/pm/projects?id_client=${this.clientId}`);
                console.log('Projects Response:', response);
                
                if (response && response.data && response.data.projects) {
                    this.projects = response.data.projects;
                } else if (response && response.projects) {
                    this.projects = response.projects;
                } else {
                    this.projects = [];
                }
                
                console.log('Loaded projects for client:', this.projects);
            } catch (error) {
                console.error('Error fetching projects:', error);
                this.projects = [];
            } finally {
                this.projectsLoading = false;
            }
        },
        async saveRequirement() {
            this.loading = true;
            this.successMessage = null;
            this.errorMessage = null;

            try {
                // project_id should be a string (e.g., "PRJ-123")
                const response = await make_postrequest(
                    `/api/pm/client/requirements/${this.clientId}`, 
                    this.requirementForm
                );
                console.log('Create Requirement Response:', response);

                if (response && response.data) {
                    this.successMessage = response.message || 'Requirement created successfully!';
                    this.resetForm();
                    this.$emit('requirement-created', response.data);
                } else {
                    this.errorMessage = response.message || 'Failed to create requirement';
                }
            } catch (error) {
                console.error('Error creating requirement:', error);
                this.errorMessage = error.message || 'An error occurred while creating the requirement';
            } finally {
                this.loading = false;
            }
        },
        resetForm() {
            this.requirementForm = {
                requirement_id: '',
                project_id: '',
                requirements: ''
            };
            // Generate new requirement ID after reset
            this.generateRequirementId();
        }
    },
    mounted() {
        // Generate initial requirement ID
        this.generateRequirementId();
        
        // Fetch projects for this client
        this.fetchProjects();
        
        // Regenerate ID and fetch projects when modal is shown
        const modal = document.getElementById('addRequirementModal');
        if (modal) {
            modal.addEventListener('show.bs.modal', () => {
                this.generateRequirementId();
                this.fetchProjects();
            });
        }
    },
    watch: {
        clientId() {
            // Refetch projects if clientId changes
            this.fetchProjects();
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
    min-height: 100px;
}
</style>
