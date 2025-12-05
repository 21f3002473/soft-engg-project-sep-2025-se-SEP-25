<template>
  <div class="dashboard">
    <main class="dashboard-content">
      <h1>Account Settings</h1>
      <div class="content-placeholder">
        <p>Admin profile information, password change form, and API key management would be displayed here.</p>
        <table class="table table-striped table-hover table-bordered shadow-sm custom-table align-middle">
          <thead class="table-dark">
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{{ accounts.id }}</td>
              <td>{{ accounts.name }}</td>
              <td>{{ accounts.email }}</td>
              <td><span class="role-pill">{{ accounts.role }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
    <button type="button" class="btn btn-primary" @click="changeDetails()">change details</button>
  </div>
</template>

<script>
export default {
  name: 'AdminAccount',
  data() {
    return {
      accounts: [],
    };
  },
  methods: {
    async fetchAccountSettings() {
      const res = await fetch(`http://localhost:8000/api/admin/account`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await res.json();
      this.accounts = data;
    },
    async changeDetails() {
      this.$router.push('/admin/account/edit');
    }
  },
  mounted() {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!localStorage.getItem('token') || user.role !== 'root') {
      alert('Please login to access the admin dashboard.');
      this.$router.push('/login');
      return;
    }
    this.fetchAccountSettings();
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