<template>
    <div class="client-card">
        <div class="card d-inline-block">
            <img :src="imageUrl" class="card-img-top" alt="">
            <div class="card-body p-2">
                <h3 class="card-title mb-1">{{ clientname }}</h3>
                <p class="card-text small mb-0">{{ description }}</p>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'ClientCardComponent',
    props: {
       id: { type: Number, required: true },
       clientname: { type: String, required: true },
       description: { type: String, required: true }
    },
    computed: {
        imageUrl() {
            return `https://dummyjson.com/icon/${this.clientname}/150`;
        }
    }
};
</script>

<style scoped>
.client-card {
    margin: 5px;
}

/* allow the card to shrink-wrap to the image width */
.card {
    width: auto;
    display: inline-block; /* redundant with d-inline-block but kept for clarity */
}

/* ensure image scales responsively and determines card width */
.card img {
    display: block;
    height: auto;
    max-width: 100%;
}

/* optional: slightly smaller card text */
.card {
    font-size: 0.75em;
}

.card-body {
    padding: 0.5rem;
}
</style>