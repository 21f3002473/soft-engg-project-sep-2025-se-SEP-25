<template>
  <div class="hr-layout">
    
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container-fluid">
        <router-link class="navbar-brand" :to="{ name: 'HRDashboard' }">Sync'em</router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarHR" aria-controls="navbarHR" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarHR">
          <ul class="navbar-nav ms-auto mb-2 mb-lg-0">
            <li class="nav-item">
              <router-link :to="{ name: 'HRDashboard' }" class="nav-link">Dashboard</router-link>
            </li>
            <li class="nav-item">
              <router-link :to="{ name: 'HREmployees' }" class="nav-link">Employees</router-link>
            </li>
            <li class="nav-item">
              <router-link :to="{ name: 'HRProjects' }" class="nav-link">Projects</router-link>
            </li>
            <li class="nav-item">
              <router-link :to="{ name: 'HRPolicies' }" class="nav-link">HR Policies</router-link>
            </li>
            <li class="nav-item">
              <router-link :to="{ name: 'HRChatbot' }" class="nav-link">Chatbot</router-link>
            </li>
            <li class="nav-item ms-2">
              <button class="btn btn-outline-light btn-sm" @click="logout">Logout</button>
            </li>
          </ul>
        </div>
      </div>
    </nav>
    <router-view />
  </div>
</template>

<script>
export default {
  name: "HRLayout",
  methods: {
    logout() {
      this.$store.dispatch('logout');
      this.$router.push({ name: 'Login' });
    }
  }
}
</script>