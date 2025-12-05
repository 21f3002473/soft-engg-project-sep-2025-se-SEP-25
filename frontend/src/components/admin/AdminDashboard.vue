<template>
  <div class="dashboard">
    <main class="dashboard-content">
      <div class="content-header">
        <h1>{{ title }}</h1>
        <div class="search-bar">
          <svg class="icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
            <path
              d="M11 4a7 7 0 1 1 0 14 7 7 0 0 1 0-14zm0-2a9 9 0 1 0 5.293 16.293l4.707 4.707-1.414 1.414-4.707-4.707A9 9 0 0 0 11 2z" />
          </svg>
          <input class="search-input" type="text" placeholder="Search by Name" v-model="searchQuery"
            aria-label="Search employees by name" />
        </div>
      </div>

      <div class="main-area">

        <div class="employee-list">
          <table class="table table-striped table-hover table-bordered shadow-sm custom-table align-middle">
            <thead class="table-dark">
              <tr>
                <th>Employee ID</th>
                <th>Employee Name</th>
                <th>Work Email ID</th>
                <th>Employee Role</th>
                <th>Employee Status</th>
                <th>Take Action</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="emp in this.employees" :key="emp.id">
                <td>{{ emp.id }}</td>
                <td>{{ emp.name }}</td>
                <td>{{ emp.email }}</td>
                <td>{{ emp.role }}</td>

                <td>
                  Active
                </td>

                <td>
                  <button class="btn btn-sm btn-outline-danger" @click="deleteUser(emp)" aria-label="Delete employee">
                    Delete Employee
                  </button>
                </td>

              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { make_getrequest, make_deleterequest } from '@/store/appState';

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
      employees: [
      ],
      originalEmployees: [],
      isChatbotOpen: this?.isChatbotOpen ?? false,
      messages: [{ from: 'ai', text: "Hi! I'm your assistant. How can I help?" }],
      draft: '',
      searchQuery: '',
    };
  },
  computed: {
    filteredEmployees() {
      console.log('Search query changed to:', this.searchQuery);
      if (!this.searchQuery) {
        return this.employees;
      }
      console.log('Filtered employees:', this.employees.filter(emp => {
        return emp.name.toLowerCase().includes(this.searchQuery.toLowerCase());
      }));
      return this.employees.filter(emp => {
        return emp.name.toLowerCase().includes(this.searchQuery.toLowerCase());
      });
    }
  },
  watch: {
    searchQuery(newQ) {
      const q = (newQ || '').toLowerCase().trim();
      if (!q) {
        this.employees = this.originalEmployees.slice();
        return;
      }
      this.employees = this.originalEmployees.filter(emp =>
        emp.name && emp.name.toLowerCase().includes(q)
      );
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
      if (!confirm(`Are you sure you want to delete user ${emp.name}?`)) {
        return;
      }
      try {
        await make_deleterequest(`/api/admin/deleteusers/${emp.id}`);
        this.employees = this.employees.filter(e => e.id !== emp.id);
        this.originalEmployees = this.originalEmployees.filter(e => e.id !== emp.id);
        alert(`User ${emp.name} deleted successfully.`);
      } catch (error) {
        console.error('Failed to delete user', error);
      }
    }
  },
  mounted() {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!localStorage.getItem('token') || user.role !== 'root') {
      alert('Please login to access the admin dashboard.');
      this.$router.push('/login');
      return;
    }
    this.fetchData();
  }
};
</script>

<style scoped>
.dashboard {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background-color: #f4f7f6;
  height: 100vh;
  color: #333;
}

a {
  text-decoration: none;
  color: #555;
  font-size: 14px;
}

a:hover {
  color: #000;
}

.btn {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: #f9f9f9;
  cursor: pointer;
  font-size: 14px;
}

.btn:hover {
  background-color: #2563eb;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  background-color: #ffffff;
  border-bottom: 1px solid #ddd;
}

.nav-links a {
  margin-right: 25px;
}

.account-link a {
  font-weight: bold;

}

.dashboard-content {
  padding: 25px 30px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.content-header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
}

.search-bar {
  position: relative;
  width: 260px;
  display: flex;
  align-items: center;
}

.search-bar .icon {
  position: absolute;
  left: 14px;
  width: 18px;
  height: 18px;
  fill: #6b7280;
  pointer-events: none;
}

.search-bar .search-input {
  width: 100%;
  padding: 10px 14px 10px 40px;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  background: #ffffff;
  font-size: 14px;
  color: #1f2937;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, background 0.25s ease;
}

.search-bar .search-input::placeholder {
  color: #9ca3af;
}

.search-bar .search-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
  background: #f8fafc;
}

.search-bar .search-input:hover:not(:focus) {
  border-color: #9ca3af;
}

.main-area {
  display: flex;
  gap: 25px;
}

.employee-list {
  flex: 3;
  background-color: #ffffff;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.employee-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.employee-item:last-child {
  border-bottom: none;
}

.emp-name {
  font-weight: 600;
  flex-basis: 10%;
}

.emp-status {
  flex-basis: 10%;
  text-align: center;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.emp-status.new {
  background-color: #e0f8e0;
  color: #006400;
}

.emp-status.old {
  background-color: #eee;
  color: #555;
}

.status-dropdown {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: #f9f9f9;
  flex-grow: 1;
}

.chatbot-panel {
  flex: 1;
  background-color: #ffffff;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.chatbot-panel h3 {
  margin-top: 0;
  margin-bottom: 15px;
  text-align: center;
  font-weight: 600;
}

.chat-history {
  flex-grow: 1;
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 15px;
  min-height: 250px;
  font-family: monospace;
  color: #666;
  overflow-y: auto;
}

.btn-ai {
  background-color: #ececec;
  border: none;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  font-weight: bold;
  align-self: center;
  margin-top: auto;
}

.chat-trigger {
  position: fixed;
  right: 24px;
  bottom: 24px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  background: #111827;
  color: #fff;
  font-weight: 700;
  letter-spacing: 0.5px;
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.25);
  cursor: pointer;
  z-index: 2000;
  transition: transform 0.15s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.chat-trigger:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 34px rgba(0, 0, 0, 0.28);
  background: #0b1220;
}

.chat-window {
  position: fixed;
  right: 24px;
  bottom: 90px;
  width: 340px;
  max-height: 70vh;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.22);
  overflow: hidden;
  z-index: 2000;
}

.chat-header {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
}

.chat-header .title {
  font-weight: 600;
  font-size: 14px;
}

.chat-header .spacer {
  flex: 1;
}

.chat-header .close {
  border: none;
  background: transparent;
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
  color: #6b7280;
}

.chat-header .close:hover {
  color: #111827;
}

.chat-body {
  padding: 12px;
  gap: 8px;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  background: #ffffff;
}

.message {
  max-width: 80%;
  padding: 8px 10px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.35;
  word-wrap: break-word;
}

.message.ai {
  align-self: flex-start;
  background: #f1f5f9;
  color: #0f172a;
  border-top-left-radius: 4px;
}

.message.user {
  align-self: flex-end;
  background: #2563eb;
  color: #ffffff;
  border-top-right-radius: 4px;
}

.chat-input {
  display: flex;
  gap: 8px;
  border-top: 1px solid #e5e7eb;
  padding: 10px;
  background: #fafafa;
}

.chat-input input {
  flex: 1;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 13px;
  outline: none;
}

.chat-input input:focus {
  border-color: #93c5fd;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.chat-input button {
  border: none;
  border-radius: 10px;
  padding: 10px 14px;
  font-weight: 600;
  background: #111827;
  color: #fff;
  cursor: pointer;
}

.chat-input button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(6px) scale(0.995);
}
</style>