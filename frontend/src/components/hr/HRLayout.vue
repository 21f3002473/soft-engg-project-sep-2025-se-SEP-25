<template>
  <div class="hr-layout">
    
    <nav class="navbar">
      <div class="nav-left brand">Sync'em</div>
      <div class="nav-right">
        <router-link to="/hr" class="nav-link">Dashboard</router-link>
        <router-link to="/hr/employees" class="nav-link active">Employees</router-link>
        <router-link to="/hr/projects" class="nav-link">Projects</router-link>
        <router-link to="/hr/hrpolicies" class="nav-link">HR Policies</router-link>
        <router-link to="/hr/chatbot" class="nav-link">Chatbot</router-link>
      </div>
    </nav>

    <!-- This is where children (Dashboard, Chatbot, etc.) will appear -->
    <router-view />
  </div>
</template>
<style scoped>
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
</style>
