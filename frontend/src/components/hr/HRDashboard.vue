<template>
  <div class="landing-root min-vh-100 d-flex flex-column">
    <!-- Navbar -->
    <!-- <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container">
        <a class="navbar-brand fw-bold" href="#">Sync'em HR</a>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#hrNavbar"
          aria-controls="hrNavbar"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="hrNavbar">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <a class="nav-link active" href="#">Dashboard</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#">Employees</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#">Projects</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#">Policies</a>
            </li>
          </ul>
        </div>
      </div>
    </nav> -->

    <!-- Main Dashboard Section -->
    <main class="flex-fill">
      <div class="container py-5">
        <div class="row align-items-center">
          <div class="col-lg-7">
            <h1 class="display-4 fw-bold">Welcome HR!</h1>
            <p class="lead">Manage your workforce efficiently and effectively.</p>
            <p class="text-muted">
              Stay on top of employee management, project tracking, and policy updates — all in one place.
            </p>
            <div class="mt-4">
              <button class="btn btn-primary me-2">View Employees</button>
              <button class="btn btn-outline-secondary">Create Policy</button>
            </div>
          </div>

          <div class="col-lg-5 d-none d-lg-block">
            <div class="card shadow-sm">
              <div class="card-body">
                <h5 class="card-title">Quick stats</h5>
                <div class="d-flex justify-content-between">
                  <div class="text-center">
                    <h3 class="mb-0">124</h3>
                    <small class="text-muted">Employees</small>
                  </div>
                  <div class="text-center">
                    <h3 class="mb-0">8</h3>
                    <small class="text-muted">Open Roles</small>
                  </div>
                  <div class="text-center">
                    <h3 class="mb-0">16</h3>
                    <small class="text-muted">Active Projects</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Feature Cards -->
        <div class="row mt-4">
          <div class="col-md-4 mb-3">
            <div class="card h-100">
              <div class="card-body d-flex flex-column">
                <h5 class="card-title">Employees</h5>
                <p class="card-text text-muted">Browse and manage employee records.</p>
                <div class="mt-auto">
                  <a href="#" class="btn btn-sm btn-outline-primary">Open</a>
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-4 mb-3">
            <div class="card h-100">
              <div class="card-body d-flex flex-column">
                <h5 class="card-title">Projects</h5>
                <p class="card-text text-muted">Track and assign projects.</p>
                <div class="mt-auto">
                  <a href="#" class="btn btn-sm btn-outline-primary">Open</a>
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-4 mb-3">
            <div class="card h-100">
              <div class="card-body d-flex flex-column">
                <h5 class="card-title">Policies</h5>
                <p class="card-text text-muted">Create and update company policies.</p>
                <div class="mt-auto">
                  <a href="#" class="btn btn-sm btn-outline-primary">Open</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <!-- <footer class="bg-light text-center py-3">
      <div class="container">
        <small class="text-muted">© 2025 Sync'em. All rights reserved.</small>
      </div>
    </footer> -->
  </div>
</template>
<script>
export default {
  name: "HRDashboard",
};
let Data = {
  return: {},
  chartData: {},
  chartOptions: {},
};
</script>

<!-- <style scoped>
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
  /* background: url('../../assets/images/landing/landingPageBackgroundImage.png') no-repeat center
    center/cover; */
  /* background-color: rgba(20, 40, 108, 0.85);
  background-blend-mode: overlay; */
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
  flex-grow: 1; /* makes hero take remaining space */
  text-align: center;
  padding: 100px 20px 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center; /* centers vertically */
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

/* Footer */
.footer {
  text-align: center;
  padding: 16px 0;
  color: #e5e7eb;
  background: rgba(0, 0, 0, 0.3);
  font-size: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
}
</style> -->
