<template>
  <div class="dashboard">
    <!-- <header class="dashboard-header">
      <div class="nav-links">
        <router-link to="/systemStatus">System Status</router-link>
        <router-link to="/logs">Logs</router-link>
        <router-link to="/updates" class="router-link-exact-active">Updates</router-link>
        <router-link to="/chatbotConfig">Chatbot Config</router-link>
      </div>
      <div class="account-link">
        <router-link to="/account">Account</router-link>
      </div>
    </header> -->

    <main class="dashboard-content">
      <h1>Updates</h1>
      <div class="content-placeholder">
        <p>Software update status, package versions, and a "Check for Updates" button would be displayed here.</p>
        <table v-if="adminUpdatesData" class="table table-striped table-hover table-bordered shadow-sm custom-table align-middle">
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
                <span
                  :class="{
                    'text-success fw-bold': adminUpdatesData.updateAvailable === true,
                    'text-danger fw-bold': adminUpdatesData.updateAvailable === false
                  }"
                >
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
export default {
  name: 'AdminUpdates',
  data() {
    return {
      adminUpdatesData: null,
    };
  },
  methods: {
    async adminUpdates() {
      // Logic to fetch and display updates
      const res = await fetch(`http://localhost:8000/api/admin/updates`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await res.json();
      // console.log(data);
      // console.log(data.length);
      this.adminUpdatesData = data;
    },
    formatDate(dateStr) {
      return new Date(dateStr).toLocaleString();
    },
  },
  mounted() {
    const user = JSON.parse(localStorage.getItem('user'));
    if(!localStorage.getItem('token') || user.role !== 'root') {
      alert('Please login to access the admin dashboard.');
      this.$router.push('/login');
      return;
    }
    this.adminUpdates();
  },
};
</script>

<style scoped>
/* All styles are identical to ChatbotConfig.vue */
.dashboard {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background-color: #f4f7f6;
  height: 100vh;
  color: #333;
}
a { text-decoration: none; color: #555; font-size: 14px; }
a:hover { color: #000; }
.router-link-exact-active { color: #007bff; font-weight: bold; }
.dashboard-header { display: flex; justify-content: space-between; align-items: center; padding: 15px 30px; background-color: #ffffff; border-bottom: 1px solid #ddd; }
.nav-links a { margin-right: 25px; }
.account-link a { font-weight: bold; }
.dashboard-content { padding: 25px 30px; }
.dashboard-content h1 { margin: 0; font-size: 28px; font-weight: 600; margin-bottom: 20px; }
.content-placeholder { background-color: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 20px; min-height: 200px; }
</style>