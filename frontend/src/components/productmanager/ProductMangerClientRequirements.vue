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
              <div class="d-flex justify-content-between align-items-center">
                <span class="text-muted small">Total Requirements:</span>
                <span class="badge bg-primary rounded-pill">{{ totalRequirements }}</span>
              </div>
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
                      class="list-group-item px-0"
                    >
                      <div class="d-flex align-items-start">
                        <span class="badge bg-secondary me-2 mt-1">{{ req.requirement_id }}</span>
                        <div class="flex-fill">
                          <p class="mb-0 small">{{ req.description }}</p>
                          <small class="text-muted">Project ID: {{ req.project_id }}</small>
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
  </div>
</template>

<script>
import ProductMangerChatbot from './fragments/ProductMangerChatbot.vue';
import { make_getrequest } from '@/store/appState';

export default {
  name: 'ProductMangerClientRequirements',
  props: {
    clientId: {
      type: [String, Number],
      required: true
    }
  },
  components: {
    ProductMangerChatbot
  },
  data() {
    return {
      clientData: null,
      requirements: [],
      totalRequirements: 0,
      loading: true,
      error: null
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
        const response = await make_getrequest(`/pr/client/requirements/${this.clientId}`);
        
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
