<template>
  <div class="container-fluid py-4">
    <div class="row mb-4">
      <div class="col-12 d-flex justify-content-between align-items-center">
        <div>
          <h2 class="mb-3">Projects Dashboard</h2>
          <p class="text-muted">Total Projects: {{ totalProjects }}</p>
        </div>
        <button 
          type="button" 
          class="btn btn-primary"
          data-bs-toggle="modal" 
          data-bs-target="#addNewProjectModal"
        >
          <i class="bi bi-plus-lg me-2"></i>Add New Project
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3">Loading projects...</p>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">
      <h4 class="alert-heading">Error!</h4>
      <p>{{ error }}</p>
    </div>

    <div v-else-if="projects.length > 0" class="row g-4">
      <div v-for="project in projects" :key="project.id" class="col-12 col-md-6 col-lg-4">
        <div class="card h-100 shadow-sm">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">{{ project.project_name }}</h5>
            <span :class="getStatusBadgeClass(project.status)">
              {{ project.status }}
            </span>
          </div>
          <div class="card-body">
            <h6 class="card-subtitle mb-2 text-muted">
              ID: {{ project.project_id }}
            </h6>
            <p class="card-text">{{ project.description || 'No description available' }}</p>
            
            <hr>
            
            <div v-if="project.client" class="mb-3">
              <h6 class="fw-bold">Client Information</h6>
              <p class="mb-1">
                <strong>Name:</strong> {{ project.client.name }}
              </p>
              <p class="mb-0">
                <strong>Email:</strong> 
                <a :href="'mailto:' + project.client.email" class="text-decoration-none">
                  {{ project.client.email }}
                </a>
              </p>
            </div>

            <div class="d-flex justify-content-between align-items-center">
              <span class="badge bg-primary rounded-pill">
                {{ project.requirements_count }} Requirements
              </span>
              <button 
                class="btn btn-sm btn-outline-primary" 
                @click="viewProjectDetails(project.id)"
              >
                View Details
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-5">
      <h4 class="text-muted">No projects found</h4>
      <p>There are currently no projects in the system.</p>
    </div>

    <AddNewProjectModal @project-created="onProjectCreated" />
  </div>
</template>

<script>
import { make_getrequest } from '@/store/appState';
import AddNewProjectModal from './fragments/AddNewProjectModal.vue';

export default {
    name: 'ProductManagerProjectsView',
    components: {
        AddNewProjectModal
    },
    data() {
        return {
            projects: [],
            totalProjects: 0,
            loading: false,
            error: null,
        };
    },
    methods: {
        async fetchProjects() {
            this.loading = true;
            this.error = null;
            
            try {
                const result = await make_getrequest('/api/pm/projects/dashboard');
                console.log('Full API Response:', result);
                                
                if (result && result.data && result.data.projects) {
                    this.projects = result.data.projects;
                    this.totalProjects = result.data.total_projects;
                } else if (result && result.projects) {
                    this.projects = result.projects;
                    this.totalProjects = result.total_projects;
                } else {
                    this.error = 'Invalid response format';
                }
                
                console.log('Projects loaded:', this.projects.length);
            } catch (err) {
                this.error = err.message || 'An unexpected error occurred';
                console.error('Error fetching projects:', err);
            } finally {
                this.loading = false;
            }
        },
        getStatusBadgeClass(status) {
            const statusLower = status?.toLowerCase() || '';
            const baseClasses = 'badge';
            
            if (statusLower.includes('active') || statusLower.includes('in progress')) {
                return `${baseClasses} bg-success`;
            } else if (statusLower.includes('completed')) {
                return `${baseClasses} bg-primary`;
            } else if (statusLower.includes('pending')) {
                return `${baseClasses} bg-warning text-dark`;
            } else if (statusLower.includes('cancelled') || statusLower.includes('on hold')) {
                return `${baseClasses} bg-danger`;
            }
            return `${baseClasses} bg-secondary`;
        },
        viewProjectDetails(projectId) {
            console.log('View project details:', projectId);
            this.$router.push({ 
                name: 'ProductManagerSingleProject', 
                params: { projectId: projectId } 
            });
        },
        onProjectCreated(newProject) {
            console.log('New project created:', newProject);
            this.fetchProjects();
        }
    },
    mounted() {
        this.fetchProjects();
    },
};
</script>

<style scoped>
.card {
    transition: transform 0.2s ease-in-out;
}

.card:hover {
    transform: translateY(-5px);
}

.card-header {
    background-color: #f8f9fa;
    border-bottom: 2px solid #dee2e6;
}

.card-text {
    color: #6c757d;
    font-size: 0.9rem;
    max-height: 3em;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}
</style>
