<template>
  <div class="dashboard">

    <main class="dashboard-content">
      <h1>Logs</h1>
      <div class="content-placeholder">
        <p>A live-tailing log viewer (e.g., for application, system, or audit logs) would go here.</p>
        <table class="table table-striped table-hover table-bordered shadow-sm custom-table align-middle">
          <thead class="table-dark">
            <tr>
              <th>Admin ID</th>
              <th>Admin Email</th>
              <th>Admin Name</th>
              <th>User Count</th>
              <th>Logs Count</th>
              <th>Backup Count</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{{ currentAdminID }}</td>
              <td>{{ currentAdminEmail }}</td>
              <td>{{ currentAdminName }}</td>
              <td>{{ logs.userCount }}</td>
              <td>{{ logs.logsCount }}</td>
              <td>{{ logs.backupsCount }}</td>
            </tr>
          </tbody>
        </table>
        </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'AdminLogs',
  data() {
    return {
      logs: [],
      currentAdminID: null,
      currentAdminEmail: null,
      currentAdminName: null,
    };
  },
  methods: {
    async fetchLogs() {
      // Placeholder for log fetching logic
      const res = await fetch(`http://localhost:8000/api/admin/summary`,{
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      }); 
      if (res.ok) {
        const data = await res.json();
        // Process and display logs
        this.logs = data;
        this.currentAdminID = this.logs.currentAdmin.id;
        this.currentAdminEmail = this.logs.currentAdmin.email;
        this.currentAdminName = this.logs.currentAdmin.name;
      } else {
        console.error('Failed to fetch logs');
        return;
      }
    },
  }, 
  mounted() {
    this.fetchLogs();
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