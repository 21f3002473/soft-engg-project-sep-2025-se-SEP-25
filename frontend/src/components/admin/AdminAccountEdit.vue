<template>
  <div class="row justify-content-center">
    <div class="col-12 col-md-10 col-lg-6">
      <div class="card border-0 shadow-lg rounded-4">
        <div class="card-header bg-primary text-white py-3 px-4 d-flex justify-content-between align-items-center">
          <div>
            <h1 class="h5 mb-1 fw-bold">Edit Account Details</h1>
            <p class="mb-0 small opacity-75">
              Keep your profile and credentials up to date.
            </p>
          </div>
          <span class="badge bg-white text-primary">ADMIN</span>
        </div>

        <div class="card-body p-4 p-md-5">
          <form @submit.prevent="handleSubmit()">
            <div class="mb-3">
              <label for="id" class="form-label fw-medium">User ID</label>
              <input type="text" class="form-control bg-light" id="id" v-model="id" disabled />
              <div class="form-text">System generated identifier (read-only).</div>
            </div>

            <div class="mb-3">
              <label for="name" class="form-label fw-medium">Name</label>
              <input type="text" class="form-control bg-light" id="name" placeholder="Enter your name" v-model="name"
                disabled />
              <div class="form-text">Name cannot be changed here.</div>
            </div>

            <div class="mb-3">
              <label for="old_password" class="form-label fw-medium">Old Password</label>
              <div class="input-group">
                <input :type="showOldPassword ? 'text' : 'password'" class="form-control" id="old_password"
                  placeholder="Enter old password" v-model="old_password" autocomplete="current-password" required />
                <button class="btn btn-outline-secondary" type="button" @click="showOldPassword = !showOldPassword"
                  title="Toggle password visibility">
                  <i class="bi" :class="showOldPassword ? 'bi-eye-slash' : 'bi-eye'"></i>
                  <span v-if="!showOldPassword">Show</span>
                  <span v-else>Hide</span>
                </button>
              </div>
              <div class="form-text">Enter your current password to authorize changes.</div>
            </div>

            <div class="mb-4">
              <label for="new_password" class="form-label fw-medium">New Password</label>
              <div class="input-group">
                <input :type="showNewPassword ? 'text' : 'password'" class="form-control" id="new_password"
                  placeholder="Enter new password" v-model="new_password" autocomplete="new-password" required />
                <button class="btn btn-outline-secondary" type="button" @click="showNewPassword = !showNewPassword"
                  title="Toggle password visibility">
                  <i class="bi" :class="showNewPassword ? 'bi-eye-slash' : 'bi-eye'"></i>
                  <span v-if="!showNewPassword">Show</span>
                  <span v-else>Hide</span>
                </button>
              </div>
              <div class="form-text">
                Use at least 8 characters with a mix of letters, numbers and symbols.
              </div>
            </div>

            <div class="row mb-4">
              <div class="col-md-6 mb-3 mb-md-0">
                <label for="role" class="form-label fw-medium">User Role</label>
                <input type="text" class="form-control bg-light" id="role" v-model="role" disabled />
              </div>
              <div class="col-md-6">
                <label for="email" class="form-label fw-medium">Email</label>
                <input type="email" class="form-control bg-light" id="email" v-model="email" disabled />
              </div>
            </div>

            <div class="d-flex align-items-center justify-content-between pt-2">
              <button type="submit" class="btn btn-primary px-4 fw-semibold shadow-sm">
                Save Changes
              </button>

              <button type="button" class="btn btn-outline-secondary" @click="$router.push('/admin/account')">
                Cancel
              </button>
            </div>
          </form>
        </div>
        <div class="card-footer bg-light py-3 px-4 text-center small text-muted">
          Changes take effect immediately after saving.
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { make_getrequest, make_putrequest } from '@/store/appState';
import { useNotify } from '@/utils/useNotify';

export default {
  name: 'AdminAccountEdit',
  data() {
    return {
      name: '',
      old_password: '',
      new_password: '',
      id: '',
      role: '',
      email: '',
      showOldPassword: false,
      showNewPassword: false
    };
  },
  methods: {
    async handleSubmit() {
      try {
        await make_putrequest('/api/admin/account', {
          name: this.name,
          old_password: this.old_password,
          new_password: this.new_password
        });
        useNotify().success('Account details updated successfully.');
        this.$router.push('/admin/account');
      } catch (error) {
        useNotify().error('Failed to update account details.');
        console.error(error);
      }
    },
    async fetchAccountDetails() {
      try {
        const data = await make_getrequest('/api/admin/account');
        this.name = data.name;
        this.id = data.id;
        this.email = data.email;
        this.role = data.role;
      } catch (error) {
        console.error('Failed to fetch account details', error);
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
    this.fetchAccountDetails();
  }
};
</script>