<template>
    <!-- new client modal -->
    <div class="modal fade" id="newClientModal" tabindex="-1" aria-labelledby="newClientModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="newClientModalLabel">Add New Client</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <!-- Success Alert -->
                    <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
                        {{ successMessage }}
                        <button type="button" class="btn-close" @click="successMessage = null"></button>
                    </div>
                    
                    <!-- Error Alert -->
                    <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show" role="alert">
                        {{ errorMessage }}
                        <button type="button" class="btn-close" @click="errorMessage = null"></button>
                    </div>

                    <form @submit.prevent="saveClient">
                        <div class="mb-3">
                            <label for="clientId" class="form-label">Client ID <span class="text-danger">*</span></label>
                            <input 
                                type="text" 
                                class="form-control" 
                                id="clientId" 
                                v-model="clientForm.client_id"
                                placeholder="Enter client ID (e.g., CL001)"
                                required
                            >
                        </div>
                        <div class="mb-3">
                            <label for="clientName" class="form-label">Client Name <span class="text-danger">*</span></label>
                            <input 
                                type="text" 
                                class="form-control" 
                                id="clientName" 
                                v-model="clientForm.client_name"
                                placeholder="Enter client name"
                                required
                            >
                        </div>
                        <div class="mb-3">
                            <label for="clientEmail" class="form-label">Client Email <span class="text-danger">*</span></label>
                            <input 
                                type="email" 
                                class="form-control" 
                                id="clientEmail" 
                                v-model="clientForm.email"
                                placeholder="Enter client email"
                                required
                            >
                        </div>
                        <div class="mb-3">
                            <label for="clientImage" class="form-label">Client Logo/Image</label>
                            <input 
                                type="file" 
                                class="form-control" 
                                id="clientImage" 
                                @change="handleImageUpload"
                                accept="image/*"
                            >
                            <small class="text-muted">Upload client logo or image (will be encoded automatically)</small>
                        </div>
                        
                        <!-- Image Preview -->
                        <div v-if="imagePreview" class="mb-3 text-center">
                            <label class="form-label d-block">Image Preview</label>
                            <img 
                                :src="imagePreview" 
                                alt="Client Image Preview" 
                                class="img-thumbnail"
                                style="max-width: 150px; max-height: 150px; object-fit: cover;"
                            >
                            <button type="button" class="btn btn-sm btn-outline-danger ms-2" @click="removeImage">
                                <i class="bi bi-trash"></i> Remove
                            </button>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button 
                        type="button" 
                        class="btn btn-primary" 
                        @click="saveClient"
                        :disabled="loading"
                    >
                        <span v-if="loading" class="spinner-border spinner-border-sm me-1" role="status"></span>
                        {{ loading ? 'Saving...' : 'Save Client' }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { make_postrequest } from '@/store/appState';

export default {
    name: 'NewClientModal',
    data() {
        return {
            clientForm: {
                client_id: '',
                client_name: '',
                email: '',
                image_base64: ''
            },
            imagePreview: null,
            loading: false,
            successMessage: null,
            errorMessage: null
        };
    },
    methods: {
        handleImageUpload(event) {
            const file = event.target.files[0];
            if (!file) return;

            // Validate file type
            if (!file.type.startsWith('image/')) {
                this.errorMessage = 'Please select a valid image file';
                return;
            }

            // Validate file size (max 2MB)
            if (file.size > 2 * 1024 * 1024) {
                this.errorMessage = 'Image size should be less than 2MB';
                return;
            }

            const reader = new FileReader();
            reader.onload = (e) => {
                const base64String = e.target.result;
                this.imagePreview = base64String;
                // Remove the data:image/...;base64, prefix for API
                this.clientForm.image_base64 = base64String.split(',')[1];
            };
            reader.readAsDataURL(file);
        },
        removeImage() {
            this.imagePreview = null;
            this.clientForm.image_base64 = '';
            // Reset file input
            const fileInput = document.getElementById('clientImage');
            if (fileInput) fileInput.value = '';
        },
        async saveClient() {
            this.loading = true;
            this.successMessage = null;
            this.errorMessage = null;

            try {
                const response = await make_postrequest('/api/pm/dashboard', this.clientForm);
                console.log('Create Client Response:', response);

                if (response && response.data) {
                    this.successMessage = response.message || 'Client created successfully!';
                    this.resetForm();
                    this.$emit('client-created', response.data);
                } else {
                    this.errorMessage = response.message || 'Failed to create client';
                }
            } catch (error) {
                console.error('Error creating client:', error);
                this.errorMessage = error.message || 'An error occurred while creating the client';
            } finally {
                this.loading = false;
            }
        },
        resetForm() {
            this.clientForm = {
                client_id: '',
                client_name: '',
                email: '',
                image_base64: ''
            };
            this.imagePreview = null;
            // Reset file input
            const fileInput = document.getElementById('clientImage');
            if (fileInput) fileInput.value = '';
        }
    }
};
</script>

<style scoped>
.modal-body {
    max-height: 70vh;
    overflow-y: auto;
}

.img-thumbnail {
    border: 2px solid #dee2e6;
    border-radius: 8px;
}
</style>