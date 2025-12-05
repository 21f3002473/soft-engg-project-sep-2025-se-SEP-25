<template>
  <div>
    <div class="card border-0 shadow-sm rounded-4 mb-4">
      <div class="card-body p-4">
        <p class="text-secondary mb-4">
          Admin profile information, password change form, and API key management.
        </p>
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light text-secondary">
              <tr>
                <th class="py-3 ps-4 border-0">ID</th>
                <th class="py-3 border-0">Name</th>
                <th class="py-3 border-0">Email</th>
                <th class="py-3 pe-4 border-0">Role</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="ps-4 fw-medium text-dark">{{ accounts.id }}</td>
                <td class="fw-medium text-dark">{{ accounts.name }}</td>
                <td class="text-secondary">{{ accounts.email }}</td>
                <td class="pe-4">
                  <span
                    class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill px-3 py-2">
                    {{ accounts.role }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="d-flex justify-content-end">
      <button type="button" class="btn btn-primary px-4 py-2 fw-semibold shadow-sm" @click="changeDetails()">
        Change Details
      </button>
    </div>
  </div>
</template>

<script>
import { make_getrequest } from '@/store/appState';

export default {
  name: 'AdminAccount',
  data() {
    return {
      accounts: [],
    };
  },
  methods: {
    async fetchAccountSettings() {
      try {
        const data = await make_getrequest('/api/admin/account');
        this.accounts = data;
      } catch (error) {
        console.error('Failed to fetch account settings', error);
      }
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