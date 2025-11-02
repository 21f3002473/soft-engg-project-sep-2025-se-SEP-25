<template>
    <div class="client-card card">
        <div class="card-body">
            <img src="https://dummyjson.com/icon/{{ clientname }}/150" class="card-img-top" alt="Client Image">
            <h5 class="card-title">{{ clientname }}</h5>
            <p class="card-text">{{ description }}</p>
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