<template>
  <div class="employees-root container-fluid py-4 min-vh-100 bg-light">
    <div class="container">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 class="h3 mb-1 text-primary fw-bold">Employee Management</h2>
          <p class="text-muted mb-0">Manage reviews, announcements, FAQs, and courses</p>
        </div>
      </div>

      <ul class="nav nav-tabs mb-4 border-bottom-0">
        <li class="nav-item">
          <a class="nav-link px-4 py-2 fw-medium rounded-top border-0"
            :class="{ 'active shadow-sm bg-white text-primary': activeTab === 'employees', 'text-muted': activeTab !== 'employees' }"
            href="#" @click.prevent="activeTab = 'employees'">
            <i class="bi bi-people me-2"></i>Employees & Reviews
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link px-4 py-2 fw-medium rounded-top border-0"
            :class="{ 'active shadow-sm bg-white text-primary': activeTab === 'announcements', 'text-muted': activeTab !== 'announcements' }"
            href="#" @click.prevent="activeTab = 'announcements'">
            <i class="bi bi-megaphone me-2"></i>Announcements
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link px-4 py-2 fw-medium rounded-top border-0"
            :class="{ 'active shadow-sm bg-white text-primary': activeTab === 'faqs', 'text-muted': activeTab !== 'faqs' }"
            href="#" @click.prevent="activeTab = 'faqs'">
            <i class="bi bi-question-circle me-2"></i>FAQs
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link px-4 py-2 fw-medium rounded-top border-0"
            :class="{ 'active shadow-sm bg-white text-primary': activeTab === 'courses', 'text-muted': activeTab !== 'courses' }"
            href="#" @click.prevent="activeTab = 'courses'">
            <i class="bi bi-book me-2"></i>Courses
          </a>
        </li>
      </ul>

      <div class="card shadow-sm border-0 rounded-3">
        <div class="card-body p-4">

          <section v-if="activeTab === 'employees'" class="fade-in">
            <div class="row">
              <div class="col-md-12">
                <div class="d-flex justify-content-between align-items-center mb-4">
                  <h4 class="mb-0 text-secondary">Performance Reviews</h4>
                  <div class="input-group w-50 shadow-sm">
                    <span class="input-group-text bg-white border-end-0"><i class="bi bi-search text-muted"></i></span>
                    <input v-model="search" type="text" class="form-control border-start-0 ps-0"
                      placeholder="Search Employee..." />
                  </div>
                </div>

                <div class="table-responsive rounded border">
                  <table class="table table-hover align-middle mb-0">
                    <thead class="bg-light text-secondary small text-uppercase">
                      <tr>
                        <th class="ps-4 py-3">Employee</th>
                        <th class="py-3">Status</th>
                        <th class="py-3 text-end pe-4">Actions</th>
                      </tr>
                    </thead>

                    <tbody>
                      <tr v-for="emp in filteredEmployees" :key="emp.id" class="border-bottom-0">
                        <td class="ps-4 fw-medium">{{ emp.name }}</td>

                        <td>
                          <span class="badge rounded-pill px-3 py-2 fw-normal"
                            :class="emp.status === 'Done' ? 'bg-success-subtle text-success' : 'bg-light text-dark border'">
                            <i class="bi me-1" :class="emp.status === 'Done' ? 'bi-check-circle-fill' : 'bi-clock'"></i>
                            {{ emp.status }}
                          </span>
                        </td>

                        <td class="text-end pe-4">
                          <button class="btn btn-sm btn-outline-primary me-2 shadow-sm" @click="openViewModal(emp)">
                            <i class="bi bi-eye me-1"></i> View
                          </button>

                          <button class="btn btn-sm btn-success shadow-sm" @click="openAddModal(emp)">
                            <i class="bi bi-plus-circle me-1"></i> Review
                          </button>
                        </td>
                      </tr>
                      <tr v-if="filteredEmployees.length === 0">
                        <td colspan="3" class="text-center py-5 text-muted">No employees found.</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </section>

          <section v-if="activeTab === 'announcements'" class="fade-in">
            <HRAnnouncements />
          </section>

          <section v-if="activeTab === 'faqs'" class="fade-in">
            <HRFAQs />
          </section>

          <section v-if="activeTab === 'courses'" class="fade-in">
            <HRCourses />
          </section>

        </div>
      </div>

    </div>

    <div class="modal fade" id="viewModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header bg-light border-bottom-0">
            <h5 class="modal-title fw-bold">Performance Review</h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4">
            <h6 class="text-muted mb-3 text-uppercase small ls-1">Employee: <span class="text-dark fw-bold">{{
                selectedEmployee?.name }}</span></h6>

            <div v-if="reviews.length === 0" class="alert alert-secondary border-0 d-flex align-items-center"
              role="alert">
              <i class="bi bi-info-circle-fill me-2 fs-5"></i>
              <div>No reviews available for this employee.</div>
            </div>

            <div v-for="rev in reviews" :key="rev.id" class="card mb-3 border bg-light shadow-sm">
              <div class="card-body">
                <div class="d-flex justify-content-between mb-2">
                  <div class="text-warning">
                    <i v-for="n in 5" :key="n" class="bi" :class="n <= rev.rating ? 'bi-star-fill' : 'bi-star'"></i>
                  </div>
                  <small class="text-muted">{{ new Date(rev.created_at).toLocaleDateString() }}</small>
                </div>
                <p class="mb-0 text-secondary">{{ rev.comments || 'No comments provided.' }}</p>
              </div>
            </div>
          </div>
          <div class="modal-footer border-top-0 pt-0">
            <button type="button" class="btn btn-secondary w-100" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="addModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">

          <div class="modal-header bg-primary text-white border-bottom-0">
            <h5 class="modal-title fw-bold">Add Review</h5>
            <button class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>

          <div class="modal-body p-4">
            <p class="mb-3 text-secondary">Adding review for <strong class="text-dark">{{ selectedEmployee?.name
                }}</strong></p>
            <form @submit.prevent="submitReview">

              <div class="mb-3">
                <label class="form-label fw-medium">Rating</label>
                <div class="d-flex gap-2">
                  <button type="button" v-for="n in 5" :key="n"
                    class="btn btn-outline-warning d-flex align-items-center justify-content-center flex-grow-1"
                    :class="{ 'active': newReview.rating === n }" @click="newReview.rating = n">
                    <i class="bi bi-star-fill"></i>
                    <span class="d-none d-sm-inline ms-1">{{ n }}</span>
                  </button>
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label fw-medium">Comments</label>
                <textarea v-model="newReview.comments" rows="4" class="form-control bg-light"
                  placeholder="Share your feedback regarding the employee's performance..."></textarea>
              </div>

              <button type="submit" class="btn btn-primary w-100 py-2 fw-medium shadow-sm">
                Submit Review
              </button>

            </form>
          </div>

        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { make_getrequest, make_postrequest } from "@/store/appState.js";
import { useNotify } from "@/utils/useNotify.js";
import bootstrap from "bootstrap/dist/js/bootstrap.bundle";
import HRAnnouncements from "./fragments/HRAnnouncements.vue";
import HRFAQs from "./fragments/HRFAQs.vue";
import HRCourses from "./fragments/HRCourses.vue";

export default {
  name: "HREmployees",
  components: {
    HRAnnouncements,
    HRFAQs,
    HRCourses
  },
  setup() {
    return { notify: useNotify() };
  },
  data() {
    return {
      activeTab: 'employees',
      employees: [],
      search: "",
      selectedEmployee: null,
      reviews: [],
      newReview: {
        rating: 5,
        comments: ""
      },
    };
  },

  computed: {
    filteredEmployees() {
      return this.employees.filter((e) =>
        e.name.toLowerCase().includes(this.search.toLowerCase())
      );
    }
  },

  mounted() {
    this.fetchEmployees();
  },

  methods: {
    async fetchEmployees() {
      try {
        const res = await make_getrequest("/api/hr/employees");
        const list = res.employees || [];

        const statusRequests = list.map((emp) =>
          make_getrequest(`/api/hr/reviews/${emp.id}`)
            .then((r) => ({
              id: emp.id,
              status: (r.reviews && r.reviews.length > 0) ? "Done" : "Upcoming"
            }))
        );

        const results = await Promise.all(statusRequests);

        list.forEach((emp) => {
          const found = results.find((r) => r.id === emp.id);
          emp.status = found.status;
        });

        this.employees = list;

      } catch (err) {
        console.error("Error fetching employees:", err);
        this.notify.error("Failed to load employees");
      }
    },

    async openViewModal(emp) {
      try {
        this.selectedEmployee = emp;
        const res = await make_getrequest(`/api/hr/reviews/${emp.id}`);
        this.reviews = res.reviews || [];
        new bootstrap.Modal("#viewModal").show();
      } catch (err) {
        console.error("Error loading review:", err);
      }
    },

    openAddModal(emp) {
      this.selectedEmployee = emp;
      this.newReview = { rating: 5, comments: "" };
      new bootstrap.Modal("#addModal").show();
    },

    async submitReview() {
      try {
        await make_postrequest("/api/hr/review/create", {
          user_id: this.selectedEmployee.id,
          rating: this.newReview.rating,
          comments: this.newReview.comments
        });

        this.notify.success("Review Submitted!");
        bootstrap.Modal.getInstance(document.getElementById("addModal")).hide();

        this.fetchEmployees();
      } catch (err) {
        console.error("Error submitting review:", err);
        this.notify.error("Failed to submit review");
      }
    }
  }
};
</script>

<style scoped>
.nav-link {
  color: #6c757d;
  transition: all 0.2s ease;
}

.nav-link:hover {
  color: #0d6efd;
}

.nav-link.active {
  color: #0d6efd !important;
}

.fade-in {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(5px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.ls-1 {
  letter-spacing: 1px;
}
</style>
