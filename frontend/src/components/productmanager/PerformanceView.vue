<template>
    <div class="dashboard">
        <h2>Client List</h2>
        <div class="ClientList">
            
            <div class="d-flex flex-row flex-wrap">
                <div class="p-2" v-for="Employee in EmployeeList" :key="Employee.id">
                    <RouterLink :to="{ name: 'ProductManagerPerformanceDetails', params: { id: Employee.id } }">
                        <EmployeeCardComponent
                            :id="Employee.id"
                            :employeename="Employee.employeename"
                            :description="Employee.description"
                        />
                    </RouterLink>
                </div>
            </div>
        </div>
    </div>
</template>


<script>

import EmployeeCardComponent from './fragments/EmployeeCardComponent.vue';

export default {
    name: 'PerformanceView',
    data() {
        return {
            EmployeeList: [
                {
                    id: 1,
                    employeename: 'Employee A',
                    description: 'Details about Employee A'
                },
                {
                    id: 2,
                    employeename: 'Employee B',
                    description: 'Details about Employee B'
                },
                {
                    id: 3,
                    employeename: 'Employee C',
                    description: 'Details about Employee C'
                },
                {
                    id: 4,
                    employeename: 'Employee D',
                    description: 'Details about Employee D'
                }
                
            ]
        };
    },
    components: {
        EmployeeCardComponent
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