<template>
    <div class="client-card card mb-3 shadow-sm h-100">
        <img
            :src="`https://dummyjson.com/icon/${encodeURIComponent(clientname)}/150`"
            class="card-img-top img-fluid rounded-top"
            :alt="clientname"
        />
        <div class="card-body d-flex flex-column">
            <div class="d-flex justify-content-between align-items-start mb-2">
                <h5 class="card-title mb-0">{{ clientname }}</h5>
                <small class="badge bg-secondary">{{ id }}</small>
            </div>
            <p class="card-text text-muted flex-grow-1">{{ description }}</p>
            <!-- <div class="mt-3">
                <button class="btn btn-sm btn-primary">View</button>
                <button class="btn btn-sm btn-outline-secondary ms-2">Edit</button>
            </div> -->
        </div>
    </div>
</template>

<script>
export default {
    name: 'ClientCardComponent',
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