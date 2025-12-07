<template>
    <div class="dashboard">
        <div class="container-fluid">
            <div class="row mb-4">
                <div class="col-12">
                    <h2 class="fw-bold mb-3">Employee Performance</h2>
                    <p class="text-muted">View and track employee performance metrics</p>
                </div>
            </div>

            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3 text-muted">Loading employees...</p>
            </div>

            <div v-else-if="error" class="alert alert-danger" role="alert">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                {{ error }}
            </div>

            <div v-else class="employee-list-section">
                <div v-if="EmployeeList.length > 0" class="row g-3">
                    <div v-for="Employee in EmployeeList" :key="Employee.id" class="col-12 col-sm-6 col-md-4 col-xl-3">
                        <RouterLink :to="{ name: 'ProductManagerPerformanceDetails', params: { id: Employee.id } }"
                            class="text-decoration-none">
                            <ProductMangerEmployeeCard :id="Employee.id" :employeename="Employee.name"
                                :email="Employee.email" :role="Employee.role" />
                        </RouterLink>
                    </div>
                </div>

                <div v-else class="row">
                    <div class="col-12">
                        <div class="alert alert-info text-center" role="alert">
                            <i class="bi bi-info-circle me-2"></i>
                            No employees available at the moment.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import ProductMangerEmployeeCard from './fragments/ProductMangerEmployeeCard.vue';
import { make_getrequest } from '@/store/appState';
import { useNotify } from '@/utils/useNotify';

export default {
    name: 'ProductMangerPerformance',
    components: {
        ProductMangerEmployeeCard
    },
    data() {
        return {
            EmployeeList: [],
            totalEmployees: 0,
            loading: true,
            error: null
        };
    },
    setup() {
        const notify = useNotify();
        return { notify };
    },
    methods: {
        async fetchEmployees() {
            this.loading = true;
            this.error = null;

            try {
                const response = await make_getrequest('/api/pm/employees');

                console.log('Employees Response:', response);

                const responseData = response?.data || {};

                this.EmployeeList = responseData?.employees || [];
                this.totalEmployees = responseData?.total_employees || this.EmployeeList.length;

                console.log('Processed Employees:', this.EmployeeList);

            } catch (error) {
                console.error('Error fetching employees:', error);
                this.error = error.message || 'Failed to load employees. Please try again.';
                this.notify.error(this.error);
            } finally {
                this.loading = false;
            }
        }
    },
    mounted() {
        this.fetchEmployees();
    }
};
</script>

<style scoped>
.dashboard {
    background-color: #f8f9fa;
    min-height: 100vh;
    max-width: 100vw;
    overflow-x: hidden;
    padding: 1.5rem 0;
}

.container-fluid {
    max-width: 100%;
}

.employee-list-section {
    margin-top: 1rem;
}

.text-decoration-none:hover {
    text-decoration: none !important;
}

@media (min-width: 768px) {
    .container-fluid {
        padding-left: 2rem;
        padding-right: 2rem;
    }
}

@media (min-width: 1200px) {
    .container-fluid {
        padding-left: 3rem;
        padding-right: 3rem;
    }
}

* {
    box-sizing: border-box;
}
</style>