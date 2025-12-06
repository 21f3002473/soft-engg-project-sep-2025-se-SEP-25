<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h2 text-primary fw-bold mb-0">Requests</h1>
      <div class="d-flex gap-3 align-items-center position-relative">
        <div class="dropdown">
          <button class="btn btn-primary rounded-pill fw-bold d-flex align-items-center gap-2 shadow-sm" type="button"
            @click="showCreateOptions = !showCreateOptions">
            <i class="bi bi-plus-lg"></i> New Request
          </button>
          <ul class="dropdown-menu show mt-2 border-0 shadow" v-if="showCreateOptions" style="right: 0; left: auto;">
            <li><a class="dropdown-item" href="#" @click.prevent="navigateTo('leave')">Leave</a></li>
            <li><a class="dropdown-item" href="#" @click.prevent="navigateTo('reimbursement')">Reimbursement</a></li>
            <li><a class="dropdown-item" href="#" @click.prevent="navigateTo('transfer')">Transfer</a></li>
          </ul>
        </div>
        <input v-model="search" placeholder="Search requests..." class="form-control rounded-pill border-0 bg-light"
          type="search" style="width: 250px;" />
      </div>
    </div>

    <section class="card border-0 shadow-sm p-4" style="min-height: 400px;">
      <transition name="fade">
        <div v-if="!isChildRouteActive" class="requests-container">
          <div v-if="loading" class="text-center py-5 text-muted">
            <div class="spinner-border text-primary mb-2" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <div>Loading requests...</div>
          </div>
          <div v-else-if="filteredRequests.length" class="d-flex flex-column gap-3">
            <div class="card p-3 border bg-light request-item" v-for="req in filteredRequests" :key="req.uniqueKey"
              @click="openRequest(req)" style="cursor: pointer; transition: all 0.2s;">
              <div class="d-flex justify-content-between align-items-center">
                <div class="d-flex flex-column gap-1">
                  <div class="d-flex align-items-center gap-2">
                    <span class="badge rounded-pill text-uppercase" :class="getBadgeClass(req.type)">{{ req.type}}</span>
                    <span class="text-muted small">{{ formatDate(req.date) }}</span>
                  </div>
                  <h5 class="mb-0 fw-bold text-dark">{{ req.description }}</h5>
                  <div class="text-muted small" v-if="req.details">
                    {{ req.details }}
                  </div>
                </div>
                <div>
                  <span class="badge rounded-pill text-capitalize" :class="getStatusClass(req.status)">{{ req.status}}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-5 text-muted">
            <p class="mb-0">No requests found.</p>
          </div>
        </div>
      </transition>


      <transition name="slide-fade">
        <div v-if="isChildRouteActive" class="bg-light rounded p-3">
          <button
            class="btn btn-link text-decoration-none text-secondary fw-bold p-0 mb-3 d-flex align-items-center gap-2"
            @click="goBack">
            <i class="bi bi-arrow-left"></i> Back to Requests
          </button>
          <router-view />
        </div>
      </transition>
    </section>
  </div>
</template>

<script>
import { make_getrequest } from "@/store/appState.js";
import { useNotify } from "@/utils/useNotify.js";
import titleCase from "@/utils/titleCase.js";

const toTitleCase = str =>
  str.toLowerCase().replace(/\b\w/g, c => c.toUpperCase());

export default {
  name: "EmployeeRequests",
  data() {
    return {
      search: "",
      requests: [],
      loading: false,
      showCreateOptions: false,
    };
  },
  computed: {
    filteredRequests() {
      const q = this.search.trim().toLowerCase();
      if (!q) return this.requests;
      return this.requests.filter((r) =>
        r.type.toLowerCase().includes(q) ||
        r.status.toLowerCase().includes(q) ||
        (r.description && r.description.toLowerCase().includes(q))
      );
    },
    isChildRouteActive() {
      return this.$route.name !== 'EmployeeRequests';
    }
  },
  methods: {
    navigateTo(type) {
      this.showCreateOptions = false;
      this.$router.push(`/employee/requests/${type}`);
    },
    openRequest(req) {
      const id = req.uniqueKey.split('-')[1];
      this.$router.push({
        path: `/employee/requests/${req.type.toLowerCase()}/${id}`,
        state: { requestData: JSON.parse(JSON.stringify(req)) }
      });
    },
    goBack() {
      this.$router.push('/employee/requests');
    },
    formatDate(dateStr) {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleDateString(undefined, {
        year: 'numeric', month: 'short', day: 'numeric'
      });
    },
    getBadgeClass(type) {
      switch (type.toLowerCase()) {
        case 'leave': return 'bg-primary-subtle text-primary';
        case 'reimbursement': return 'bg-success-subtle text-success';
        case 'transfer': return 'bg-info-subtle text-info';
        default: return 'bg-secondary';
      }
    },
    getStatusClass(status) {
      switch (status.toLowerCase()) {
        case 'pending': return 'bg-warning-subtle text-warning border border-warning-subtle';
        case 'completed': return 'bg-success-subtle text-success border border-success-subtle';
        case 'rejected': return 'bg-danger-subtle text-danger border border-danger-subtle';
        default: return 'bg-secondary';
      }
    },
    async fetchRequests() {
      this.loading = true;
      try {
        const [leavesRes, reimbursementsRes, transfersRes] = await Promise.all([
          make_getrequest('/api/employee/requests/leave'),
          make_getrequest('/api/employee/requests/reimbursement'),
          make_getrequest('/api/employee/requests/transfer')
        ]);

        const leaves = (leavesRes.leaves || []).map(l => ({
          uniqueKey: `leave-${l.request_id}`,
          type: 'Leave',
          description: `${titleCase(l.leave_type)} Leave`,
          details: `${l.reason || 'No reason provided'}`,
          date: l.created_date || l.from_date,
          status: l.status,
          raw: l
        }));

        const reimbursements = (reimbursementsRes.reimbursements || []).map(r => ({
          uniqueKey: `reimb-${r.request_id}`,
          type: 'Reimbursement',
          description: `${titleCase(r.expense_type)} Reimbursement`,
          details: `Amount: $${r.amount} - ${r.remark || ''}`,
          date: r.date_expense,
          status: r.status,
          raw: r
        }));

        const transfers = (transfersRes.transfers || []).map(t => ({
          uniqueKey: `trans-${t.request_id}`,
          type: 'Transfer',
          description: `Transfer to ${titleCase(t.request_department)}`,
          details: `Reason: ${t.reason || 'None'}`,
          date: null,
          status: t.status,
          raw: t
        }));

        this.requests = [...leaves, ...reimbursements, ...transfers].sort((a, b) => {
          if (a.date && b.date) return new Date(b.date) - new Date(a.date);
          return 0;
        });

      } catch (error) {
        console.error("Failed to fetch requests", error);
        useNotify().error("Failed to fetch requests.");
      } finally {
        this.loading = false;
      }
    }
  },
  mounted() {
    this.fetchRequests();
  }
};
</script>

<style scoped>
.request-item:hover {
  background: #fff !important;
  transform: translateY(-2px);
  box-shadow: 0 .125rem .25rem rgba(0, 0, 0, .075) !important;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active {
  transition: all 0.4s ease;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
</style>