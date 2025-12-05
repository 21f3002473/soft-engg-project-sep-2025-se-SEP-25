<template>
  <div class="admin-account-edit min-vh-100 d-flex align-items-center justify-content-center py-4 py-md-5">
    <main class="w-100">
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-12 col-md-10 col-lg-6">
            <div class="card shadow-lg border-0 rounded-4 card-floating">
              <div
                class="card-header d-flex align-items-center justify-content-between bg-primary text-white py-3 px-4 px-md-5">
                <div>
                  <h1 class="h4 mb-1 fw-semibold">Edit Account Details</h1>
                  <p class="mb-0 small text-white-50">
                    Keep your profile and credentials up to date.
                  </p>
                </div>
                <span class="badge bg-light text-primary fw-semibold text-uppercase">
                  Admin
                </span>
              </div>

              <div class="card-body p-4 p-md-5">
                <form @submit.prevent="handleSubmit()">
                  <div class="mb-3">
                    <label for="id" class="form-label fw-semibold">User ID</label>
                    <input type="text" class="form-control form-control-sm bg-light" id="id" v-model="id" disabled />
                    <div class="form-text">System generated identifier (read-only).</div>
                  </div>

                  <div class="mb-3">
                    <label for="name" class="form-label fw-semibold">Name</label>
                    <input type="text" class="form-control" id="name" placeholder="Enter your name" v-model="name"
                      disabled />
                  </div>

                  <div class="mb-3">
                    <label for="old_password" class="form-label fw-semibold">Old Password</label>
                    <div class="input-with-eye">
                      <input :type="showOldPassword ? 'text' : 'password'" class="form-control with-eye-input"
                        id="old_password" placeholder="Enter old password" v-model="old_password"
                        autocomplete="current-password" required />
                      <button type="button" class="eye-btn" @click="showOldPassword = !showOldPassword"
                        :aria-label="showOldPassword ? 'Hide old password' : 'Show old password'"
                        title="Toggle old password visibility">
                        <svg v-if="!showOldPassword" xmlns="http://www.w3.org/2000/svg" width="18" height="18"
                          viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                          stroke-linejoin="round">
                          <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z" />
                          <circle cx="12" cy="12" r="3" />
                        </svg>
                        <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
                          fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                          stroke-linejoin="round">
                          <path d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a20.32 20.32 0 0 1 5.17-5.94" />
                          <path d="M1 1l22 22" />
                          <path d="M9.53 9.53A3 3 0 0 0 14.47 14.47" />
                        </svg>
                      </button>
                    </div>
                    <div class="form-text">Enter your current password to authorize changes.</div>
                  </div>

                  <div class="mb-3">
                    <label for="new_password" class="form-label fw-semibold">New Password</label>
                    <div class="input-with-eye">
                      <input :type="showNewPassword ? 'text' : 'password'" class="form-control with-eye-input"
                        id="new_password" placeholder="Enter new password" v-model="new_password"
                        autocomplete="new-password" required />
                      <button type="button" class="eye-btn" @click="showNewPassword = !showNewPassword"
                        :aria-label="showNewPassword ? 'Hide new password' : 'Show new password'"
                        title="Toggle new password visibility">
                        <svg v-if="!showNewPassword" xmlns="http://www.w3.org/2000/svg" width="18" height="18"
                          viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                          stroke-linejoin="round">
                          <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z" />
                          <circle cx="12" cy="12" r="3" />
                        </svg>
                        <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
                          fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                          stroke-linejoin="round">
                          <path d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a20.32 20.32 0 0 1 5.17-5.94" />
                          <path d="M1 1l22 22" />
                          <path d="M9.53 9.53A3 3 0 0 0 14.47 14.47" />
                        </svg>
                      </button>
                    </div>
                    <div class="form-text">
                      Use at least 8 characters with a mix of letters, numbers and symbols.
                    </div>
                  </div>

                  <div class="mb-3">
                    <label for="role" class="form-label fw-semibold">User Role</label>
                    <input type="text" class="form-control form-control-sm bg-light" id="role" v-model="role"
                      disabled />
                    <div class="form-text">Your access level in the system (read-only).</div>
                  </div>

                  <div class="mb-4">
                    <label for="email" class="form-label fw-semibold">Email</label>
                    <input type="email" class="form-control form-control-sm bg-light" id="email" v-model="email"
                      disabled />
                    <div class="form-text">Contact your administrator to change this email.</div>
                  </div>

                  <div class="d-flex align-items-center justify-content-between">
                    <button type="submit" class="btn btn-primary px-4">
                      <span class="me-1">
                        <i class="bi bi-save"></i>
                      </span>
                      Save Changes
                    </button>

                    <button type="button" class="btn btn-outline-secondary btn-sm"
                      @click="$router.push('/admin/account')">
                      Cancel
                    </button>
                  </div>
                </form>
              </div>

              <div class="card-footer bg-light py-3 px-4 px-md-5 small text-muted">
                Changes take effect immediately after saving.
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
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
      const res = await fetch(`http://localhost:8000/api/admin/account`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          name: this.name,
          old_password: this.old_password,
          new_password: this.new_password
        })
      });
      if (res.ok) {
        alert('Account details updated successfully.');
        this.$router.push('/admin/account');
      } else {
        alert('Failed to update account details.');
      }
    },
    async fetchAccountDetails() {
      const res = await fetch(`http://localhost:8000/api/admin/account`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await res.json();
      this.name = data.name;
      this.id = data.id;
      this.email = data.email;
      this.role = data.role;
    }
  },
  mounted() {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!localStorage.getItem('token') || user.role !== 'root') {
      alert('Please login to access the admin dashboard.');
      this.$router.push('/login');
      return;
    }
    this.fetchAccountDetails();
  }
};
</script>

<style scoped>
.admin-account-edit {
  background: radial-gradient(circle at top left, #0d6efd1f, transparent 55%),
    radial-gradient(circle at bottom right, #6610f21f, transparent 55%),
    linear-gradient(135deg, #f8f9fa, #e9ecef);
}

.card-floating {
  transform: translateY(0);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card-floating:hover {
  transform: translateY(-2px);
  box-shadow: 0 1.25rem 3rem rgba(15, 23, 42, 0.18);
}

.input-with-eye {
  position: relative;
  display: flex;
  align-items: stretch;
  border: 1px solid var(--bs-border-color, #dee2e6);
  border-radius: 0.5rem;
  background-color: #fff;
  overflow: hidden;
}

.with-eye-input {
  border: none;
  box-shadow: none;
  flex: 1 1 auto;
  padding-right: 3rem;
}

.with-eye-input:focus {
  box-shadow: none;
  outline: none;
}

.eye-btn {
  background: transparent;
  border: none;
  border-left: 1px solid #dee2e6;
  width: 2.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.eye-btn:focus-visible {
  outline: 2px solid rgba(13, 110, 253, 0.35);
  outline-offset: 2px;
  border-radius: 0;
}

.eye-btn svg {
  pointer-events: none;
}

@media (max-width: 575.98px) {
  .card-header h1.h4 {
    font-size: 1.1rem;
  }
}
</style>