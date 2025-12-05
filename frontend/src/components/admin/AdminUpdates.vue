<template>
  <div class="dashboard">
    <main class="dashboard-content">
      <h1>Updates</h1>
      <div class="content-placeholder">
        <p>Software update status, package versions, and a "Check for Updates" button would be displayed here.</p>
        <table v-if="adminUpdatesData"
          class="table table-striped table-hover table-bordered shadow-sm custom-table align-middle">
          <thead class="table-dark">
            <tr>
              <th scope="col">Current Version</th>
              <th scope="col">Last Checked</th>
              <th scope="col">Update Available?</th>
            </tr>
          </thead>

          <tbody>
            <tr>
              <td>{{ adminUpdatesData.currentVersion }}</td>
              <td>{{ formatDate(adminUpdatesData.lastChecked) }}</td>
              <td>
                <span :class="{
                  'text-success fw-bold': adminUpdatesData.updateAvailable === true,
                  'text-danger fw-bold': adminUpdatesData.updateAvailable === false
                }">
                  {{ adminUpdatesData.updateAvailable ? "Yes" : "No" }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
        <!-- Empty state -->
        <div v-else class="text-center py-4 text-muted">
          <i class="bi bi-info-circle"></i> No update records found.
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { make_getrequest } from '@/store/appState';

export default {
  name: 'AdminUpdates',
  data() {
    return {
      adminUpdatesData: null,
    };
  },
  methods: {
    async adminUpdates() {
      try {
        const data = await make_getrequest('/api/admin/updates');
        this.adminUpdatesData = data;
      } catch (error) {
        console.error('Failed to fetch admin updates', error);
      }
    },
    formatDate(dateStr) {
      return new Date(dateStr).toLocaleString();
    },
  },
  mounted() {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!localStorage.getItem('token') || user.role !== 'root') {
      alert('Please login to access the admin dashboard.');
      this.$router.push('/login');
      return;
    }
    this.adminUpdates();
  },
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

.router-link-exact-active {
  color: #007bff;
  font-weight: bold;
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

.dashboard-content h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 20px;
}

.content-placeholder {
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  min-height: 200px;
}
</style>