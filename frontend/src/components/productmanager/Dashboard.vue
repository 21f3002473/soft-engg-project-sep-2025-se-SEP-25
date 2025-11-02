<template>
    <div class="dashboard">
        <h2>Client List</h2>
        <div class="ClientList">
            
            <div class="d-flex flex-row flex-wrap">
                <div class="p-2" v-for="Client in ClientList" :key="Client.id">
                    <RouterLink :to="{ name: 'ProductManagerRequirements', params: { clientId: Client.id } }">
                        <ClientCardComponent 
                            :id="Client.id" 
                            :clientname="Client.clientname" 
                            :description="Client.description" 
                        />
                    </RouterLink>
                </div>
            </div>
        </div>
    </div>
</template>


<script>

import ClientCardComponent from './fragments/ClientCardComponent.vue';

export default {
    name: 'ProductmanagerDashboard',
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
    },
    components: {
        ClientCardComponent
    },
    methods: {
        // Dashboard methods
    },
    mounted() {
        // Code to run when the component is mounted
    }
};
</script>

<style scoped>

.ClientList {
    margin-top: 20px;
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
}

</style>