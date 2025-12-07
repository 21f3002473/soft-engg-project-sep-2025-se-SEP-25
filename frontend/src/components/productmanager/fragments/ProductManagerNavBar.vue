<template>
    <div class="user-shell d-flex flex-column min-vh-100">
        <ProductManagerNavigation />

        <main class="container-fluid flex-grow-1 my-4 px-3" style="max-width: 90%;">
            <section class="page-body shadow p-4 rounded-4 bg-white bg-opacity-75"
                style="backdrop-filter: blur(5px); min-height: 250px;">
                <router-view />
            </section>
        </main>
    </div>
</template>

<script>
import ProductManagerNavigation from './ProductManagerNavigation.vue';

export default {
    name: 'ProductManagerNavBar', // Kept name to match file and router, though it acts as Layout
    components: { ProductManagerNavigation }
};
</script>

<style scoped>
.user-shell {
    background: linear-gradient(135deg, #e9f1ff 0%, #f9fbff 100%);
}
</style>