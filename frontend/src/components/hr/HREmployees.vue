<template>
  <div class="employees-root container-fluid py-4">
    <div class="container">
      <section class="employees-section">
        <div class="row">

          <!-- LEFT: TABLE -->
          <div class="col-md-8 mb-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h1 class="h4 mb-0">Performance Reviews</h1>
              <input
                v-model="search"
                type="text"
                class="form-control form-control-sm w-50"
                placeholder="Search Employee..."
              />
            </div>

            <div class="table-responsive">
              <table class="table table-striped table-hover">
                <thead class="thead-light">
                  <tr>
                    <th>Employee</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>

                <tbody>
                  <tr v-for="emp in filteredEmployees" :key="emp.id">
                    <td>{{ emp.name }}</td>

                    <td>
                      <span
                        class="badge"
                        :class="emp.status === 'Done' ? 'bg-success' : 'bg-secondary'"
                      >
                        {{ emp.status }}
                      </span>
                    </td>

                    <td>
                      <button
                        class="btn btn-sm btn-primary me-2"
                        @click="openViewModal(emp)"
                      >
                        View
                      </button>

                      <button
                        class="btn btn-sm btn-success"
                        @click="openAddModal(emp)"
                      >
                        Add Review
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- RIGHT: PANEL -->
          <div class="col-md-4">
            <div class="card">
              <div class="card-body">
                <h5 class="card-title">Review Gen</h5>
                <p class="card-text">
                  Auto-generate and manage employee performance assessments.
                </p>
              </div>
            </div>
          </div>

        </div>
      </section>
    </div>

    <!-- MODAL: VIEW REVIEW -->
    <div class="modal fade" id="viewModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">

          <div class="modal-header">
            <h5 class="modal-title">Review – {{ selectedEmployee?.name }}</h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>

          <div class="modal-body">
            <div v-if="reviews.length === 0">
              <p class="text-muted">No reviews available.</p>
            </div>

            <div
              v-for="rev in reviews"
              :key="rev.id"
              class="mb-3 p-2 border rounded"
            >
              <p><strong>Rating:</strong> ⭐ {{ rev.rating }}</p>
              <p><strong>Comments:</strong> {{ rev.comments || 'None' }}</p>
              <small class="text-muted">
                Created: {{ new Date(rev.created_at).toLocaleString() }}
              </small>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- MODAL: ADD REVIEW -->
    <div class="modal fade" id="addModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">

          <div class="modal-header">
            <h5 class="modal-title">Add Review – {{ selectedEmployee?.name }}</h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>

          <div class="modal-body">
            <form @submit.prevent="submitReview">

              <div class="mb-3">
                <label class="form-label">Rating</label>
                <select v-model="newReview.rating" class="form-select" required>
                  <option disabled value="">Select rating</option>
                  <option v-for="n in 5" :key="n" :value="n">{{ n }}</option>
                </select>
              </div>

              <div class="mb-3">
                <label class="form-label">Comments</label>
                <textarea
                  v-model="newReview.comments"
                  rows="3"
                  class="form-control"
                  placeholder="Enter comments (optional)"
                ></textarea>
              </div>

              <button type="submit" class="btn btn-primary w-100">
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
import axios from "axios";
import bootstrap from "bootstrap/dist/js/bootstrap.bundle";

export default {
  name: "HREmployees",

  data() {
    return {
      employees: [],
      search: "",
      selectedEmployee: null,
      reviews: [],
      newReview: {
        rating: "",
        comments: ""
      },
      BASE: "http://localhost:8000/api/hr",
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
    // 🔐 AUTH HEADERS
    getAuthHeaders() {
      const token = localStorage.getItem("hr_token"); // FIXED
      if (!token) {
        console.warn("No token found, redirecting to login");
        window.location.href = "/login";
      }
      return {
        headers: {
          Authorization: `Bearer ${token}`
        }
      };
    },

    // ✔️ FETCH EMPLOYEES + STATUS
    async fetchEmployees() {
      try {
        //const res = await axios.get(`${this.BASE}/employees`, this.getAuthHeaders());
        //const list = res.data;
        const res = await axios.get(`${this.BASE}/employees`, this.getAuthHeaders());
        const list = res.data.employees || [];
        

        // Fetch review status for each employee in parallel
        const statusRequests = list.map((emp) =>
          axios
            .get(`${this.BASE}/reviews/${emp.id}`, this.getAuthHeaders())
            .then((r) => ({
              id: emp.id,
              //status: r.data.length > 0 ? "Done" : "Upcoming"
              status: (r.data.reviews && r.data.reviews.length > 0) ? "Done" : "Upcoming"
            }))
        );

        const results = await Promise.all(statusRequests);

        // Merge statuses into employees list
        list.forEach((emp) => {
          const found = results.find((r) => r.id === emp.id);
          emp.status = found.status;
        });

        this.employees = list;

      } catch (err) {
        console.error("Error fetching employees:", err);

        if (err.response && err.response.status === 401) {
          console.warn("Token expired. Redirecting...");
          localStorage.removeItem("hr_token");
          window.location.href = "/login";
        }
      }
    },

    // ✔️ OPEN VIEW MODAL
    async openViewModal(emp) {
      try {
        this.selectedEmployee = emp;

        const res = await axios.get(
          `${this.BASE}/reviews/${emp.id}`,
          this.getAuthHeaders()
        );

        //this.reviews = res.data;
        this.reviews = res.data.reviews || [];


        new bootstrap.Modal("#viewModal").show();
      } catch (err) {
        console.error("Error loading review:", err);
      }
    },

    // ✔️ OPEN ADD MODAL
    openAddModal(emp) {
      this.selectedEmployee = emp;
      this.newReview = { rating: "", comments: "" };

      new bootstrap.Modal("#addModal").show();
    },

    // ✔️ SUBMIT NEW REVIEW
    async submitReview() {
      try {
        await axios.post(
          `${this.BASE}/review/create`,
          {
            user_id: this.selectedEmployee.id,
            rating: this.newReview.rating,
            comments: this.newReview.comments
          },
          this.getAuthHeaders()
        );

        alert("Review Submitted!");
        bootstrap.Modal.getInstance(document.getElementById("addModal")).hide();

        this.fetchEmployees();
      } catch (err) {
        console.error("Error submitting review:", err);
      }
    }
  }
};
</script>

<style scoped>
.badge {
  font-size: 0.85rem;
}
</style>


<!-- <style scoped>
.employees-root {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue',
    Arial;
  color: #fff;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
  /* background: url('../../assets/images/landing/landingPageBackgroundImage.png') no-repeat center
    center/cover; */
  /* background-color: rgba(10, 20, 70, 0.85);
  background-blend-mode: overlay; */
}

/* Navbar */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(90, 160, 255, 0.08);
  backdrop-filter: blur(4px);
  padding: 20px 60px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}
.brand {
  font-style: italic;
  font-weight: 700;
  color: #ffffff;
  font-size: 22px;
}
.nav-right {
  display: flex;
  align-items: center;
}
.nav-link {
  color: white;
  text-decoration: none;
  margin-left: 25px;
  font-size: 16px;
  transition: color 0.3s;
}
.nav-link:hover,
.nav-link.active {
  color: #dce3ff;
}

/* Section Layout */
.employees-section {
  flex-grow: 1;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 80px 20px;
  color: white;
}

.employees-container {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 40px;
  width: 90%;
  max-width: 1100px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 40px 50px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Left Column */
.employees-left {
  display: flex;
  flex-direction: column;
}
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.employees-title {
  font-size: 28px;
  color: #e2e8ff;
  font-weight: 700;
}

/* Search Bar beside title */
.search-input {
  background: rgba(255, 255, 255, 0.95);
  border: none;
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 15px;
  color: #1e3a8a;
  outline: none;
  width: 200px;
}

/* Table */
.employees-table {
  width: 100%;
  border-collapse: collapse;
}
.employees-table th,
.employees-table td {
  padding: 12px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  text-align: left;
}
.review-btn {
  background: linear-gradient(90deg, #6366f1, #3b82f6);
  border: none;
  color: white;
  border-radius: 8px;
  padding: 8px 16px;
  cursor: pointer;
  font-weight: 600;
  transition: transform 0.2s;
}
.review-btn:hover {
  transform: translateY(-2px);
  background: linear-gradient(90deg, #818cf8, #60a5fa);
}
.review-btn.done {
  background: linear-gradient(90deg, #10b981, #059669);
}

/* Right Column (Review Gen) */
.employees-right {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}
.reviewgen-title {
  font-size: 22px;
  color: #f1f5f9;
  margin-bottom: 12px;
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
