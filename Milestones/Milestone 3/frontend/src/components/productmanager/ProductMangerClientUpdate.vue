<template>
    <div class="client-update-view container py-4">
        <h2 class="mb-4">Update Client Information</h2>
        <div class="row g-4">
            <div class="col-12 col-sm-6 col-md-4 col-lg-3" v-for="client in ClientList" :key="client.id">
                <RouterLink :to="{ name: 'ProductManagerClientsUpdateDetails', params: { id: client.id } }" class="text-decoration-none">
                    <ProductMangerClientCard :id="client.id" :clientname="client.clientname" :description="client.description" />
                </RouterLink>
            </div>
        </div>
    </div>
</template>

<script>
import ProductMangerClientCard from './fragments/ProductMangerClientCard.vue';

export default {
    name: 'ProductMangerClientUpdate',
    components: {
        ProductMangerClientCard
    },
    data() {
        return {
            ClientList: [
                {
                    id: 1,
                    clientname: 'Client A',
                    description: 'Details about Client A'
                },
                {
                    id: 2,
                    clientname: 'Client B',
                    description: 'Details about Client B'
                },
                {
                    id: 3,
                    clientname: 'Client C',
                    description: 'Details about Client C'
                },
                {
                    id: 4,
                    clientname: 'Client D',
                    description: 'Details about Client D'
                }
            ]
        };
    }
};
</script>