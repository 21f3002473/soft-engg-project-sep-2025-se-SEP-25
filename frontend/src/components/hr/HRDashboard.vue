<template>
  <div class="dashboard-container">
    <header class="dash-header">
      <h1 class="title">HR Dashboard</h1>
      <p class="subtitle">Overview of employees and performance reviews</p>
    </header>

    <section class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon bg-blue"></div>
        <div class="stat-info">
          <h2>{{ employeeCount }}</h2>
          <p>Total Employees</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon bg-green"></div>
        <div class="stat-info">
          <h2>{{ reviewCount }}</h2>
          <p>Total Reviews Submitted</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon bg-orange"></div>
        <div class="stat-info">
          <h2>{{ avgRating.toFixed(1) }}</h2>
          <p>Average Rating</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon bg-red"></div>
        <div class="stat-info">
          <h2>{{ employeesWithoutReviews }}</h2>
          <p>Employees Without Reviews</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon bg-purple"></div>
        <div class="stat-info">
          <h2>{{ employeesWithReviews }}</h2>
          <p>Employees With Reviews</p>
        </div>
      </div>
    </section>

    <section class="content-row">
      <div class="panel-card">
        <h3>Recent Employees</h3>
        <ul class="list">
          <li v-for="emp in recentEmployees" :key="emp.id" class="list-item">
            <div class="list-left">
              <span class="avatar">{{ emp.name.charAt(0).toUpperCase() }}</span>
              <div>
                <strong>{{ emp.name }}</strong>
                <p class="muted">{{ emp.role || 'Employee' }}</p>
                <p class="small-text">Reports to: {{ emp.reporting_manager_name || 'N/A' }}</p>
              </div>
            </div>
          </li>
        </ul>
      </div>

      <div class="panel-card">
        <h3>Recent Performance Reviews</h3>
        <ul class="list">
          <li v-for="review in recentReviews" :key="review.id" class="list-item">
            <div class="list-left">
              <span class="dot" :class="ratingColor(review.rating)"></span>
              <div>
                <strong>{{ review.user_name }}</strong>
                <p class="muted small-text">{{ review.comments?.slice(0, 50) || 'No comments' }}...</p>
                <p class="small-text">Rating: {{ review.rating }}/5</p>
              </div>
            </div>
          </li>
        </ul>
      </div>

      <div class="panel-card">
        <h3>Latest Policies</h3>
        <ul class="list">
          <li v-for="policy in recentPolicies" :key="policy.id" class="list-item">
            <div class="list-left">
              <span class="dot bg-purple"></span>
              <div>
                <strong>{{ policy.title }}</strong>
                <p class="muted small-text">{{ policy.content?.slice(0, 50) || 'No description' }}...</p>
              </div>
            </div>
          </li>
        </ul>
      </div>
    </section>
  </div>
</template>

<script>
import { make_getrequest } from "@/store/appState";

export default {
  name: "HRDashboard",
  data() {
    return {
      employees: [],
      reviews: [],
      employeeCount: 0,
      policyCount: 0,
      reviewCount: 0,
      avgRating: 0,
      employeesWithReviews: 0,
      employeesWithoutReviews: 0,
      recentEmployees: [],
      recentReviews: [],
      policies: []
    };
  },
  computed: {
    recentPolicies() {
      return this.policies.slice(0, 5);
    }
  },
  mounted() {
    this.loadData();
  },
  methods: {
    ratingColor(rating) {
      if (rating >= 4) return "bg-green";
      if (rating >= 2) return "bg-orange";
      return "bg-red";
    },
    async loadData() {
      try {
        const [empRes, polRes, revRes] = await Promise.all([
          make_getrequest("/api/hr/employees"),
          make_getrequest("/api/hr/policies"),
          make_getrequest("/api/hr/reviews")
        ]);

        const employees = (empRes.employees || []).map(emp => ({
          ...emp,
          reporting_manager_name: emp.reporting_manager?.name || null
        }));

        const reviews = (revRes.reviews || []).map(r => ({
          ...r,
          user_name: r.user?.name || "N/A"
        }));

        this.employees = employees;
        this.policies = polRes.policies || [];
        this.reviews = reviews;

        this.employeeCount = employees.length;
        this.reviewCount = reviews.length;
        this.policyCount = this.policies.length;

        this.avgRating = reviews.length > 0
          ? (reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length)
          : 0;

        const employeeIdsWithReviews = new Set(reviews.map(r => r.user_id));
        this.employeesWithReviews = employeeIdsWithReviews.size;
        this.employeesWithoutReviews = this.employeeCount - this.employeesWithReviews;

        this.recentEmployees = [...employees]
          .sort((a, b) => b.id - a.id)
          .slice(0, 5);

        this.recentReviews = [...reviews]
          .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
          .slice(0, 5);

      } catch (err) {
        console.error("Dashboard Error:", err);
      }
    }
  }
};
</script>



<style scoped>
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
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
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
}

.bg-blue {
  background: #4c8dff;
}

.bg-green {
  background: #46d37d;
}

.bg-purple {
  background: #9b6cff;
}

.bg-orange {
  background: #f5a623;
}

.bg-red {
  background: #f44336;
}

.stat-info h2 {
  font-size: 28px;
  margin: 0;
  font-weight: 700;
}

.stat-info p {
  margin: 0;
  color: #717d91;
}

.content-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 25px;
}

.panel-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.07);
}

.panel-card h3 {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 18px;
}

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
