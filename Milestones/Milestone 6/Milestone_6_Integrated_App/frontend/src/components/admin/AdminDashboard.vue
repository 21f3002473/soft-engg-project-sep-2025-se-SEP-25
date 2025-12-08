<template>
  <div class="dashboard-page">
    <section class="card border-0 shadow-sm rounded-4">
      <div class="card-body p-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h3 class="h4 fw-bold text-primary mb-0">Employee List</h3>

          <div class="position-relative" style="width: 280px;">
            <svg class="position-absolute top-50 start-0 translate-middle-y ms-3 text-secondary" width="16" height="16"
              viewBox="0 0 24 24" fill="currentColor">
              <path
                d="M11 4a7 7 0 1 1 0 14 7 7 0 0 1 0-14zm0-2a9 9 0 1 0 5.293 16.293l4.707 4.707-1.414 1.414-4.707-4.707A9 9 0 0 0 11 2z" />
            </svg>
            <input type="text" class="form-control ps-5 rounded-pill border-0 bg-light" placeholder="Search by Name"
              v-model="searchQuery" aria-label="Search employees by name" />
          </div>
        </div>

        <div class="table-responsive">
          <table class="table table-hover mb-0 align-middle">
            <thead class="bg-light text-secondary">
              <tr>
                <th class="py-3 ps-4 border-0 rounded-start-3">Employee ID</th>
                <th class="py-3 border-0">Employee Name</th>
                <th class="py-3 border-0">Work Email ID</th>
                <th class="py-3 border-0">Roles</th>
                <th class="py-3 border-0">Status</th>
                <th class="py-3 pe-4 border-0 rounded-end-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="emp in filteredEmployees" :key="emp.id" class="border-bottom-0">
                <td class="ps-4 fw-medium text-dark">{{ emp.id }}</td>
                <td class="fw-medium text-dark">{{ emp.name }}</td>
                <td class="text-secondary">{{ emp.email }}</td>
                <td><span
                    class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill fw-normal px-3">{{
                      emp.role }}</span></td>
                <td>
                  <span
                    class="badge bg-success-subtle text-success border border-success-subtle rounded-pill px-3 py-1 fw-medium"
                    style="font-size: 0.85em;">Active</span>
                </td>
                <td class="pe-4">
                  <button class="btn btn-sm btn-outline-danger d-flex align-items-center gap-1 rounded-pill px-3"
                    @click="deleteUser(emp)" aria-label="Delete employee">
                    <i class="bi bi-trash"></i> Delete
                  </button>
                </td>
              </tr>
              <tr v-if="filteredEmployees.length === 0">
                <td colspan="6" class="text-center py-5 text-muted">No employees found matching your search.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { make_getrequest, make_deleterequest } from '@/store/appState';
import Swal from 'sweetalert2';
import { useNotify } from '@/utils/useNotify';

export default {
  name: 'AdminDashboard',
  props: {
    title: {
      type: String,
      default: 'Super Admin Dashboard'
    }
  },
  data() {
    return {
      employees: [],
      originalEmployees: [],
      isChatbotOpen: false,
      messages: [{ from: 'ai', text: "Hi! I'm your assistant. How can I help?" }],
      draft: '',
      searchQuery: '',
    };
  },
  computed: {
    filteredEmployees() {
      if (!this.searchQuery) {
        return this.employees;
      }
      return this.employees.filter(emp => {
        return emp.name.toLowerCase().includes(this.searchQuery.toLowerCase());
      });
    }
  },
  methods: {
    async fetchData() {
      try {
        const data = await make_getrequest('/api/admin/employees');
        this.employees = data;
        this.originalEmployees = Array.isArray(data) ? data.slice() : [];
      } catch (error) {
        console.error('Failed to fetch employees', error);
      }
    },
    async deleteUser(emp) {
      const result = await Swal.fire({
        title: 'Are you sure?',
        text: `Do you really want to delete user ${emp.name}? This action cannot be undone.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Yes, delete it!'
      });

      if (!result.isConfirmed) {
        return;
      }

      try {
        await make_deleterequest(`/api/admin/deleteusers/${emp.id}`);
        this.employees = this.employees.filter(e => e.id !== emp.id);
        this.originalEmployees = this.originalEmployees.filter(e => e.id !== emp.id);
        useNotify().success(`User ${emp.name} deleted successfully.`);
      } catch (error) {
        console.error('Failed to delete user', error);
        useNotify().error('Failed to delete user');
      }
    }
  },
  mounted() {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!localStorage.getItem('token') || user.role !== 'root') {
      useNotify().warn('Please login to access the admin dashboard.');
      this.$router.push('/login');
      return;
    }
    this.fetchData();
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
</style>