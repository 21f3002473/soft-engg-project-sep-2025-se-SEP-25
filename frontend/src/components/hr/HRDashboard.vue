<template>
  <div class="container py-4 dashboard-page">
    <section class="mb-4">
      <div class="card border-0 shadow text-white welcome-card p-4">
        <div class="card-body p-0">
          <h2 class="fw-bold mb-2 display-8">HR Overview</h2>
          <p class="mb-0 opacity-75 fs-6">Manage employees, policies, and performance reviews.</p>
        </div>
      </div>
    </section>

    <section class="row g-4 mb-4">
      <div class="col-md-3 col-sm-6">
        <div class="card border-0 shadow-sm h-100 stat-card-hover">
          <div class="card-body d-flex align-items-center p-3">
            <div
              class="stat-icon rounded-3 d-flex align-items-center justify-content-center me-3 text-white bg-primary">
              <i class="bi bi-people-fill"></i>
            </div>
            <div>
              <h3 class="h4 mb-0 fw-bold text-primary fs-4">{{ employeeCount }}</h3>
              <p class="text-muted mb-0">Total Employees</p>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-3 col-sm-6">
        <div class="card border-0 shadow-sm h-100 stat-card-hover">
          <div class="card-body d-flex align-items-center p-3">
            <div
              class="stat-icon rounded-3 d-flex align-items-center justify-content-center me-3 text-white bg-success">
              <i class="bi bi-check-circle-fill"></i>
            </div>
            <div>
              <h3 class="h4 mb-0 fw-bold text-primary fs-4">{{ reviewCount }}</h3>
              <p class="text-muted mb-0">Reviews Submitted</p>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-3 col-sm-6">
        <div class="card border-0 shadow-sm h-100 stat-card-hover">
          <div class="card-body d-flex align-items-center p-3">
            <div
              class="stat-icon rounded-3 d-flex align-items-center justify-content-center me-3 text-white bg-warning">
              <i class="bi bi-star-fill"></i>
            </div>
            <div>
              <h3 class="h4 mb-0 fw-bold text-primary fs-4">{{ avgRating.toFixed(1) }}</h3>
              <p class="text-muted mb-0">Avg Rating</p>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-3 col-sm-6">
        <div class="card border-0 shadow-sm h-100 stat-card-hover">
          <div class="card-body d-flex align-items-center p-3">
            <div class="stat-icon rounded-3 d-flex align-items-center justify-content-center me-3 text-white bg-danger">
              <i class="bi bi-exclamation-circle-fill"></i>
            </div>
            <div>
              <h3 class="h4 mb-0 fw-bold text-primary fs-4">{{ employeesWithoutReviews }}</h3>
              <p class="text-muted mb-0">Pending Reviews</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="row g-4">
      <div class="col-lg-4 col-md-6">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body p-4">
            <h3 class="h5 fw-bold text-primary mb-3">Recent Employees</h3>
            <ul class="list-group list-group-flush">
              <li v-for="emp in recentEmployees" :key="emp.id"
                class="list-group-item px-0 border-bottom d-flex align-items-center">
                <div
                  class="avatar bg-primary text-white rounded-circle d-flex align-items-center justify-content-center fw-bold me-3"
                  style="width: 40px; height: 40px;">
                  {{ emp.name.charAt(0).toUpperCase() }}
                </div>
                <div>
                  <div class="fw-bold text-dark">{{ emp.name }}</div>
                  <small class="text-muted d-block">{{ emp.role || 'Employee' }}</small>
                </div>
              </li>
              <li v-if="recentEmployees.length === 0" class="list-group-item px-0 text-muted">No recent employees.</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="col-lg-4 col-md-6">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body p-4">
            <h3 class="h5 fw-bold text-primary mb-3">Recent Reviews</h3>
            <ul class="list-group list-group-flush">
              <li v-for="review in recentReviews" :key="review.id" class="list-group-item px-0 border-bottom">
                <div class="d-flex justify-content-between mb-1">
                  <span class="fw-bold text-dark">{{ review.user_name }}</span>
                  <span class="badge" :class="ratingBadge(review.rating)">{{ review.rating }}/5</span>
                </div>
                <p class="mb-0 text-muted small text-truncate">{{ review.comments || 'No comments' }}</p>
              </li>
              <li v-if="recentReviews.length === 0" class="list-group-item px-0 text-muted">No reviews yet.</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="col-lg-4 col-md-6">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body p-4">
            <h3 class="h5 fw-bold text-primary mb-3">Latest Policies</h3>
            <div v-for="policy in recentPolicies" :key="policy.id" class="mb-3 pb-3 border-bottom last-no-border">
              <div class="fw-bold text-dark mb-1">{{ policy.title }}</div>
              <p class="text-muted small mb-0 text-truncate">{{ policy.content }}</p>
            </div>
            <div v-if="recentPolicies.length === 0" class="text-muted">No policies found.</div>
          </div>
        </div>
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
    ratingBadge(rating) {
      if (rating >= 4) return "bg-success";
      if (rating >= 2) return "bg-warning text-dark";
      return "bg-danger";
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
          ...r
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
        console.log(this.recentReviews);

      } catch (err) {
        console.error("Dashboard Error:", err);
      }
    }
  }
};
</script>

<style scoped>
.dashboard-page {
  font-family: "Inter", sans-serif;
  color: #1e293b;
}

.welcome-card {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
}

.stat-icon {
  width: 48px;
  height: 48px;
  font-size: 20px;
}

.stat-card-hover {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card-hover:hover {
  transform: translateY(-3px);
  box-shadow: 0 .5rem 1rem rgba(0, 0, 0, .15) !important;
}

.last-no-border:last-child {
  border-bottom: 0 !important;
  padding-bottom: 0 !important;
  margin-bottom: 0 !important;
}
</style>
