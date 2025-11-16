<template>
    <div class="client-card card shadow-sm h-100 border-0">
        <img
            :src="`https://dummyjson.com/icon/${encodeURIComponent(clientname)}/150`"
            class="card-img-top"
            :alt="clientname"
            style="height: 150px; object-fit: cover;"
        />
        <div class="card-body d-flex flex-column">
            <div class="d-flex justify-content-between align-items-start mb-2">
                <h5 class="card-title mb-0 text-dark">{{ clientname }}</h5>
                <span class="badge bg-secondary rounded-pill">ID: {{ id }}</span>
            </div>
            <p class="card-text text-muted flex-grow-1 small">{{ description }}</p>
            <div class="mt-auto pt-2">
                <small class="text-primary fw-semibold">
                    <i class="bi bi-arrow-right-circle me-1"></i>
                    View Details
                </small>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'ProductMangerClientCard',
    props: {
        id: {
            type: Number,
            required: true
        },
        clientname: {
            type: String,
            required: true
        },
        description: {
            type: String,
            required: true
        }
    }
};
</script>

<style scoped>
.client-card {
    transition: all 0.3s ease;
    cursor: pointer;
}

.client-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15) !important;
}

.card-title {
    font-size: 1.1rem;
    font-weight: 600;
}

.card-text {
    line-height: 1.5;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
}
</style>