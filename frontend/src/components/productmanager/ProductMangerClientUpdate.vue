<template>
    <div class="client-update-view container-fluid py-4">
        <div class="row mb-4">
            <div class="col-12">
                <h2 class="fw-bold mb-3">Update Client Information</h2>
                <p class="text-muted">Select a client to update their details</p>
            </div>
        </div>

        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3 text-muted">Loading clients...</p>
        </div>

        <div v-else-if="error" class="alert alert-danger" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            {{ error }}
        </div>

        <div v-else>
            <div v-if="ClientList.length > 0" class="row g-3 g-md-4">
                <div 
                    class="col-12 col-sm-6 col-md-4 col-lg-3" 
                    v-for="client in ClientList" 
                    :key="client.id"
                >
                    <RouterLink 
                        :to="{ name: 'ProductManagerClientsUpdateDetails', params: { id: client.id } }" 
                        class="text-decoration-none"
                    >
                        <ProductMangerClientCard 
                            :id="client.id" 
                            :clientname="client.client_name" 
                            :description="decodedDescription(client.description)" 
                        />
                    </RouterLink>
                </div>
            </div>

            <div v-else class="row">
                <div class="col-12">
                    <div class="alert alert-info text-center" role="alert">
                        <i class="bi bi-info-circle me-2"></i>
                        No clients available at the moment.
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import ProductMangerClientCard from './fragments/ProductMangerClientCard.vue';
import { make_getrequest } from '@/store/appState';

export default {
    name: 'ProductMangerClientUpdate',
    components: {
        ProductMangerClientCard
    },
    data() {
        return {
            ClientList: [],
            totalClients: 0,
            loading: true,
            error: null
        };
    },
    methods: {
        async fetchClients() {
            this.loading = true;
            this.error = null;

            try {
                const response = await make_getrequest('/api/pm/clients');
                
                console.log('Clients Response:', response);

                const responseData = response?.data || {};
                
                this.ClientList = responseData?.clients || [];
                this.totalClients = responseData?.total_clients || this.ClientList.length;

                console.log('Processed Clients:', this.ClientList);
                
            } catch (error) {
                console.error('Error fetching clients:', error);
                this.error = error.message || 'Failed to load clients. Please try again.';
            } finally {
                this.loading = false;
            }
        },
        decodedDescription(description) {
            if (!description) return 'No description available';
            
            try {
                return atob(description);
            } catch (e) {
                return description;
            }
        }
    },
    mounted() {
        this.fetchClients();
    }
};
</script>

<style scoped>
.client-update-view {
    background-color: #f8f9fa;
    min-height: 100vh;
}

.text-decoration-none:hover {
    text-decoration: none !important;
}
</style>