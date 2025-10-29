<template>
  <div class="landing-root">
    <!-- Navbar -->
    <nav class="navbar">
      <div class="nav-left">
        <span class="brand"><i>Sync'em</i></span>
      </div>
      <div class="nav-right">
        <router-link to="/" class="nav-link">Home</router-link>
        <router-link to="/login" class="nav-link">Login</router-link>
        <router-link to="/register" class="nav-link">Register</router-link>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <h1 class="welcome">WELCOME!</h1>
        <h2 class="subtitle">Sync'em Application</h2>
        <p class="tagline">Seamlessly synchronize your data, tasks, and teams.</p>
        <router-link to="/register" class="cta-button">Get Started</router-link>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <div class="features-grid">
        <div class="feature-group">
          <h2 class="section-title">For HR Manager</h2>
          <div class="features">
            <div class="feature">
              <h3>AI-Powered Skill Matching</h3>
              <p>
                Use a GenAI assistant to analyze employee skill sets and recommend optimal project
                allocations for data-driven staffing decisions.
              </p>
            </div>
            <div class="feature">
              <h3>Automated Performance Summaries</h3>
              <p>
                Automatically generate performance summaries using GenAI to deliver personalized
                feedback and identify training needs efficiently.
              </p>
            </div>
          </div>
        </div>

        <div class="feature-group">
          <h2 class="section-title">For Employees</h2>
          <div class="features">
            <div class="feature">
              <h3>HR Chatbot Assistance</h3>
              <p>
                Get instant answers to HR-related queries (like leave, WFH, travel policies) via a
                GenAI chatbot—no need to wait for your manager.
              </p>
            </div>
            <div class="feature">
              <h3>Personalized Learning Paths</h3>
              <p>
                Receive GenAI-driven recommendations for skill development and courses tailored to
                your career growth.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <p>© 2025 Sync'em. All rights reserved.</p>
    </footer>
  </div>
</template>

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
  background: url('./background-blue-background-blue-design-illustration-lg.png') no-repeat center
    center/cover;
  background-color: rgba(20, 40, 108, 0.85);
  background-blend-mode: overlay;
}

/* Navbar */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(20, 150, 224, 0.799); /* soft transparent blue */
  padding: 20px 40px;
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.25);
  box-shadow: 0 2px 8px rgba(0, 0, 50, 0.2);
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

/* Hero */
.hero {
  text-align: center;
  padding: 60px 20px 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  color: white;
  min-height: 40vh;
}

.welcome {
  font-size: 54px;
  font-weight: 800;
  margin-bottom: 10px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.subtitle {
  font-size: 32px;
  margin-bottom: 10px;
  font-weight: 500;
  color: #e2e8ff;
}

.tagline {
  font-size: 18px;
  max-width: 600px;
  color: #f2f4ff;
  margin-bottom: 25px;
}

.cta-button {
  display: inline-block;
  background: linear-gradient(90deg, #6366f1, #3b82f6);
  color: white;
  text-decoration: none;
  padding: 10px 24px;
  border-radius: 8px;
  font-weight: 600;
  transition:
    transform 0.3s ease,
    background 0.3s ease;
}

.cta-button:hover {
  background: linear-gradient(90deg, #818cf8, #60a5fa);
  transform: translateY(-2px);
}

/* Features Layout */
.features-section {
  color: white;
  padding: 40px 5%;
}

.features-grid {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: nowrap;
  gap: 40px;
}

.feature-group {
  flex: 1;
  min-width: 0;
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 25px;
  color: #e2e8ff;
  text-align: center;
}

.features {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.feature {
  background: rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  padding: 24px;
  width: 240px;
  text-align: center;
  color: white;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(6px);
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.feature:hover {
  background: rgba(255, 255, 255, 0.25);
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.7);
  transform: translateY(-5px) scale(1.02);
}

.feature h3 {
  font-size: 18px;
  margin-bottom: 8px;
  color: #ffffff;
}

.feature p {
  font-size: 14px;
  color: #f0f0ff;
  line-height: 1.5;
}

/* Footer */
.footer {
  text-align: center;
  padding: 16px 0;
  color: #e5e7eb;
  background: rgba(0, 0, 0, 0.3);
  font-size: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
}
</style>
