<template>
  <div class="dashboard-container">
    <!-- HEADER -->
    <header class="dash-header">
      <h1 class="title">HR Dashboard</h1>
      <p class="subtitle">Overview of employees, reviews, and policies</p>
    </header>

    <!-- STATS CARDS -->
    <section class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon bg-blue"></div>
        <div class="stat-info">
          <h2>{{ employeeCount }}</h2>
          <p>Employees</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon bg-green"></div>
        <div class="stat-info">
          <h2>{{ reviewCount }}</h2>
          <p>Performance Reviews</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon bg-purple"></div>
        <div class="stat-info">
          <h2>{{ policyCount }}</h2>
          <p>Company Policies</p>
        </div>
      </div>
    </section>

    <!-- CONTENT ROW -->
    <section class="content-row">
      <!-- EMPLOYEES PANEL -->
      <div class="panel-card">
        <h3>Recent Employees</h3>
        <ul class="list">
          <li v-for="emp in employees" :key="emp.id" class="list-item">
            <div class="list-left">
              <span class="avatar">{{ emp.name.charAt(0).toUpperCase() }}</span>
              <div>
                <strong>{{ emp.name }}</strong>
                <p class="muted">{{ emp.role || 'Employee' }}</p>
              </div>
            </div>
          </li>
        </ul>
      </div>

      <!-- POLICIES PANEL -->
      <div class="panel-card">
        <h3>Latest Policies</h3>
        <ul class="list">
          <li v-for="policy in policies" :key="policy.id" class="list-item">
            <div class="list-left">
              <span class="dot bg-purple"></span>
              <div>
                <strong>{{ policy.title }}</strong>
                <p class="muted small-text">{{ policy.description?.slice(0, 40) || 'No description' }}...</p>
              </div>
            </div>
          </li>
        </ul>
      </div>
    </section>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "HRDashboard",
  data() {
    return {
      employees: [],
      policies: [],
      reviews: [],
      employeeCount: 0,
      policyCount: 0,
      reviewCount: 0
    };
  },

  mounted() {
    this.loadData();
  },

  methods: {
    async loadData() {
      const base = "http://localhost:8000/api/hr";
      const token = localStorage.getItem("hr_token");

      if (!token) {
        console.error("No HR token found");
        this.$router.push("/login");
        return;
      }

      const auth = {
        headers: {
          Authorization: `Bearer ${token}`
        }
      };

      try {
        const [empRes, polRes, revRes] = await Promise.all([
          axios.get(`${base}/employees`, auth),
          axios.get(`${base}/policies`, auth),
          axios.get(`${base}/reviews`, auth)
        ]);

        this.employees = empRes.data.slice(0, 5);
        this.policies = polRes.data.slice(0, 5);

        this.employeeCount = empRes.data.length;
        this.policyCount = polRes.data.length;
        this.reviewCount = revRes.data.length;
      } catch (err) {
        console.error("Dashboard Error:", err);
      }
    }
  }
};
</script>

<style scoped>
/* LAYOUT */
.dashboard-container {
  padding: 40px 60px;
  font-family: "Inter", sans-serif;
  background: #f7f9fc;
  min-height: 100vh;
}

.dash-header {
  margin-bottom: 30px;
}

.title {
  font-size: 34px;
  font-weight: 800;
  color: #1e1e1e;
}

.subtitle {
  font-size: 16px;
  color: #687083;
  margin-top: -4px;
}

/* STATS GRID */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: white;
  border-radius: 14px;
  padding: 22px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
  transition: 0.2s;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 18px rgba(0,0,0,0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
}

.bg-blue { background: #4c8dff; }
.bg-green { background: #46d37d; }
.bg-purple { background: #9b6cff; }

.stat-info h2 {
  font-size: 28px;
  margin: 0;
  font-weight: 700;
}

.stat-info p {
  margin: 0;
  color: #717d91;
}

/* CONTENT ROW */
.content-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 25px;
}

/* PANEL CARD */
.panel-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.07);
}

.panel-card h3 {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 18px;
}

/* LISTS */
.list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.list-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #eceff5;
}

.list-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #4c8dff;
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: 700;
}

.dot {
  width: 13px;
  height: 13px;
  border-radius: 50%;
}

.muted {
  color: #79808f;
  font-size: 14px;
}

.small-text {
  font-size: 13px;
}
</style>
