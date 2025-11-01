<template>
    <div>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container-fluid">
                <a class="navbar-brand" href="/">Sync'em</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav">
                        <li class="nav-item">
                            <router-link to="/productmanager/dashboard" class="nav-link">Dashboard</router-link>
                        </li>
                        <li class="nav-item">
                            <router-link to="/productmanager/performance" class="nav-link">Performance</router-link>
                        </li>
                        <li class="nav-item">
                            <router-link to="/productmanager/updates" class="nav-link">Updates</router-link>
                        </li>
                        <li class="nav-item">
                            <router-link to="/productmanager/policy" class="nav-link">Policy</router-link>
                        </li>
                    </ul>
                </div>
            </div>
            <div class="d-flex align-items-center">
                <span class="navbar-text text-white me-3">
                    
                </span>
            </div>
            <div>
                <button class="btn btn-outline-light" @click="logout">Logout</button>
            </div>
        </nav>
        <router-view/>
    </div>
</template>

<script>
export default {
    name: 'ProductmanagerNavbar',
    data() {
        return {
            // Dashboard data properties
        };
    },
    methods: {
        logout() {
            // Clear authentication data and redirect to login
            localStorage.removeItem('token');
            this.$router.push('/login');
        }
    },
    mounted() {
        // Code to run when the component is mounted
    }
};

</script>