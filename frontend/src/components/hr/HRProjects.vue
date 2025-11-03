<template>
  <div class="container py-4">
    <header class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h4 mb-0">Projects Overview</h1>
      <nav>
        <a class="btn btn-outline-primary btn-sm" href="#">HR</a>
      </nav>
    </header>

    <div class="card">
      <div class="card-body">
        <form class="row g-2 mb-3">
          <div class="col-md-6">
            <input
              type="text"
              v-model="searchProject"
              class="form-control"
              placeholder="Search by Project Name..."
            />
          </div>
          <div class="col-md-6">
            <input
              type="text"
              v-model="searchManager"
              class="form-control"
              placeholder="Search by Project Manager..."
            />
          </div>
        </form>

        <div class="table-responsive">
          <table class="table table-striped table-hover mb-0">
            <thead class="table-dark">
              <tr>
                <th scope="col">Project Name</th>
                <th scope="col">Project Manager</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(project, index) in filteredProjects"
                :key="index"
              >
                <td>{{ project.name }}</td>
                <td>{{ project.manager }}</td>
              </tr>
              <tr v-if="filteredProjects.length === 0">
                <td colspan="2" class="text-center fst-italic">
                  No matching projects found.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- <div class="card-footer text-muted text-center">
        © 2025 Sync'em. All rights reserved.
      </div> -->
    </div>
  </div>
</template>

<script>
export default {
  name: "HRProjects",
  data() {
    return {
      searchProject: "",
      searchManager: "",
      projects: [
        { name: "P1", manager: "M1" },
        { name: "P2", manager: "M2" },
        { name: "P3", manager: "M3" },
        { name: "P4", manager: "M4" },
        { name: "P5", manager: "M5" },
      ],
    };
  },
  computed: {
    filteredProjects() {
      return this.projects.filter(
        (p) =>
          p.name.toLowerCase().includes(this.searchProject.toLowerCase()) &&
          p.manager.toLowerCase().includes(this.searchManager.toLowerCase())
      );
    },
  },
};
</script>

<!-- <style scoped>
.hrprojects-root {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto;
  color: #fff;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  /* background: url('../../assets/images/landing/landingPageBackgroundImage.png') no-repeat center center/cover; */
  /* background-color: rgba(20, 40, 108, 0.85);
  background-blend-mode: overlay; */
}

/* Navbar (same as HR Policies) */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(90, 160, 255, 0.1);
  backdrop-filter: blur(4px);
  padding: 20px 40px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  position: sticky;
  top: 0;
  z-index: 10;
  flex-wrap: nowrap;
}
.brand {
  font-style: italic;
  font-weight: 700;
  color: #ffffff;
  font-size: 24px;
  line-height: 1;
}
.nav-right {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: nowrap;
}
.nav-link {
  display: inline-flex;
  align-items: center;
  color: white;
  text-decoration: none;
  font-size: 18px;
  transition: color 0.3s;
}
.nav-link:hover,
.nav-link.active {
  color: #dce3ff;
}

/* Main Section */
.projects-section {
  flex-grow: 1;
  display: flex;
  justify-content: center;
  padding: 60px 20px;
}

.projects-container {
  width: 90%;
  max-width: 900px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(8px);
}

.projects-title {
  text-align: center;
  font-size: 26px;
  font-weight: 600;
  margin-bottom: 25px;
  color: #c7d2fe;
}

/* Search bars */
.search-bar-container {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 25px;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  background: rgba(255, 255, 255, 0.9);
  color: #1e3a8a;
  border: none;
  border-radius: 8px;
  padding: 12px;
  font-size: 16px;
  outline: none;
  min-width: 250px;
}

/* Table */
.projects-table {
  width: 100%;
  border-collapse: collapse;
  color: #f1f5f9;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  overflow: hidden;
}

.projects-table th,
.projects-table td {
  padding: 14px 18px;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}

.projects-table th {
  background: rgba(99, 102, 241, 0.3);
  color: #e0e7ff;
  font-weight: 600;
  font-size: 17px;
}

.projects-table tr:hover {
  background: rgba(255, 255, 255, 0.1);
  transition: background 0.2s ease-in-out;
}

.no-results {
  text-align: center;
  color: #f3f4f6;
  font-style: italic;
  padding: 20px;
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

/* Responsive */
@media (max-width: 768px) {
  .search-bar-container {
    flex-direction: column;
  }
}
</style> -->
