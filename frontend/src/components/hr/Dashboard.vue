<template>
  <div class="landing-root">
    <!-- Navbar -->
    <nav class="navbar">
      <div class="nav-left brand">HR Dashboard</div>
      <div class="nav-right">
        <router-link to="/hrdashboard" class="nav-link">Dashboard</router-link>
        <router-link to="/employees" class="nav-link">Employees</router-link>
        <router-link to="/projects" class="nav-link">Projects</router-link>
        <router-link to="/hrpolicies" class="nav-link">HR Policies</router-link>
        <router-link to="/chatbot" class="nav-link">Chatbot</router-link>
      </div>
    </nav>

    <!-- Main Dashboard Section -->
    <section class="hero">
      <h1 class="welcome">Welcome HR!</h1>
      <p class="subtitle">Manage your workforce efficiently and effectively.</p>
      <p class="tagline">Stay on top of employee management, project tracking, and policy updates — all in one place.</p>
    </section>
  </div>
</template>

<script>
export default {
  name: "HRDashboard",
};
</script>

<style scoped>
.landing-root {
  font-family:
    Inter,
    ui-sans-serif,
    system-ui,
    -apple-system,
    'Segoe UI',
    Roboto,
    'Helvetica Neue',
    Arial;
  color: #0b1220;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
  background: url('../../assets/images/landing/landingPageBackgroundImage.png') no-repeat center
    center/cover;
  background-color: rgba(20, 40, 108, 0.85);
  background-blend-mode: overlay;
}

/* Navbar */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(6, 83, 179, 0.345); /* ultra-light blue tint */
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

/* Hero Section */
.hero {
  text-align: center;
  padding: 100px 20px 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  color: white;
  min-height: 45vh;
}

.welcome {
  font-size: 54px;
  font-weight: 800;
  margin-bottom: 10px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.subtitle {
  font-size: 28px;
  margin-bottom: 15px;
  font-weight: 500;
  color: #e2e8ff;
}

.tagline {
  font-size: 18px;
  max-width: 700px;
  color: #f2f4ff;
  margin-bottom: 25px;
}
</style>
