<template>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="#">Product Manager</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <router-link class="nav-link active" aria-current="page" to="/productmanager/dashboard">Dashboard</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link class="nav-link" to="/productmanager/clientsUpdate">ClientsUpdate</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link class="nav-link" to="/productmanager/projects">Projects</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link class="nav-link" to="/productmanager/performance">Performance</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link class="nav-link" to="/login">Logout</router-link>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    <router-view/>
</template>


<script>
export default {
    name: 'NavbarComponent',
};
</script>