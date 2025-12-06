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

    <!-- This is where children (Dashboard, Chatbot, etc.) will appear -->
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

<!-- <style scoped>
/* Navbar */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(11, 11, 212, 0.792); /* ultra-light blue tint */
  backdrop-filter: blur(3px);
  padding: 20px 40px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 2px 10px rgba(90, 160, 255, 0.08);
  position: sticky;
  top: 0;
  z-index: 10;
}

.nav-left {
  font-size: 24px;
  color: white;
  font-weight: 600;
}

.brand {
  font-style: italic;
  font-weight: 700;
  letter-spacing: 0.5px;
  color: #ffffff;
}

.nav-right {
  display: flex;
  align-items: center;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-size: 18px;
  margin-left: 25px;
  font-weight: 500;
  transition: color 0.3s ease;
}

.nav-link:hover {
  color: #dce3ff;
}
</style> -->
