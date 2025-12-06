<template>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
        <div class="container-fluid px-4">
            <router-link class="navbar-brand fw-bold" :to="{ name: 'ProductManagerDashboard' }">
                Product Manager
            </router-link>

            <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
                data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false"
                aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>

            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <router-link class="nav-link" :to="{ name: 'ProductManagerDashboard' }">
                            Dashboard
                        </router-link>
                    </li>
                    <li class="nav-item">
                        <router-link class="nav-link" :to="{ name: 'ProductManagerClientsUpdate' }">
                            Updates
                        </router-link>
                    </li>
                    <li class="nav-item">
                        <router-link class="nav-link" :to="{ name: 'ProductManagerProjectDetails' }">
                            Projects
                        </router-link>
                    </li>
                    <li class="nav-item">
                        <router-link class="nav-link" :to="{ name: 'ProductManagerPerformance' }">
                            Performance
                        </router-link>
                    </li>
                    <li class="nav-item ms-2">
                        <router-link class="btn btn-outline-light btn-sm" :to="{ name: 'Login' }">
                            Logout
                        </router-link>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    <router-view/>
</template>


<script>
export default {
    name: 'ProductMangerNavBar',
};
</script>

<style scoped>
.nav-link {
    font-weight: 500;
    padding: 0.5rem 1rem;
    transition: background-color 0.2s ease;
}

.nav-link:hover {
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
}

.nav-link.router-link-active {
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
}
</style>