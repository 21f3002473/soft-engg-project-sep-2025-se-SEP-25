<template>
    <div class="employee-card card shadow-sm h-100 border-0">
        <div class="card-header bg-primary text-white text-center py-3">
            <div class="employee-avatar">
                <i class="bi bi-person-circle fs-1"></i>
            </div>
        </div>
        <div class="card-body d-flex flex-column">
            <div class="d-flex justify-content-between align-items-start mb-2">
                <h5 class="card-title mb-0 text-dark">{{ employeename }}</h5>
                <span class="badge bg-secondary rounded-pill">ID: {{ id }}</span>
            </div>
            <p class="card-text text-muted small mb-2">
                <i class="bi bi-envelope me-1"></i>{{ email }}
            </p>
            <div class="mb-3">
                <span class="badge" :class="getRoleBadgeClass(role)">
                    {{ formatRole(role) }}
                </span>
            </div>
            <div class="mt-auto pt-2">
                <small class="text-primary fw-semibold">
                    <i class="bi bi-bar-chart-line me-1"></i>
                    View Performance
                </small>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'ProductMangerEmployeeCard',
    props: {
        id: {
            type: Number,
            required: true
        },
        employeename: {
            type: String,
            required: true
        },
        email: {
            type: String,
            required: true
        },
        role: {
            type: String,
            required: true
        }
    },
    methods: {
        getRoleBadgeClass(role) {
            const roleClasses = {
                'employee': 'bg-info',
                'pm': 'bg-success',
                'hr': 'bg-warning text-dark',
                'root': 'bg-danger',
                'admin': 'bg-danger'
            };
            return roleClasses[role?.toLowerCase()] || 'bg-secondary';
        },
        formatRole(role) {
            const roleNames = {
                'employee': 'Employee',
                'pm': 'Product Manager',
                'hr': 'HR Manager',
                'root': 'Administrator',
                'admin': 'Administrator'
            };
            return roleNames[role?.toLowerCase()] || role;
        }
    }
};
</script>

<style scoped>
.employee-card {
    transition: all 0.3s ease;
    cursor: pointer;
}

.employee-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15) !important;
}

.employee-avatar {
    color: white;
}

.card-title {
    font-size: 1.1rem;
    font-weight: 600;
}

.card-text {
    line-height: 1.5;
}

.card-header {
    border-bottom: none;
}
</style>