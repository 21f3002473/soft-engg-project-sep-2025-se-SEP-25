<template>
  <div class="admin-account-edit">
    <main>
      <h1>Edit Account Details</h1>
      <div class="account-edit-form">
        <form @submit.prevent="handleSubmit()">

          <div class="mb-3">
            <label for="User ID" class="form-label">User ID</label>
            <input type="text" class="form-control" id="id" v-model="id" disabled>
          </div>

          <div class="mb-3">
            <label for="name" class="form-label">Name</label>
            <input type="text" class="form-control" id="name" placeholder="Enter your name" v-model="name">
          </div>

          <!-- Old Password with inline SVG toggle -->
          <div class="mb-3 password-wrapper">
            <label for="old_password" class="form-label">Old Password</label>
            <div class="input-with-eye">
              <input
                :type="showOldPassword ? 'text' : 'password'"
                class="form-control with-eye-input"
                id="old_password"
                placeholder="Enter old password"
                v-model="old_password"
                autocomplete="current-password"
              />
              <button
                type="button"
                class="eye-btn"
                @click="showOldPassword = !showOldPassword"
                :aria-label="showOldPassword ? 'Hide old password' : 'Show old password'"
                title="Toggle old password visibility"
              >
                <svg v-if="!showOldPassword" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a20.32 20.32 0 0 1 5.17-5.94"/>
                  <path d="M1 1l22 22"/>
                  <path d="M9.53 9.53A3 3 0 0 0 14.47 14.47"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- New Password with inline SVG toggle -->
          <div class="mb-3 password-wrapper">
            <label for="new_password" class="form-label">New Password</label>
            <div class="input-with-eye">
              <input
                :type="showNewPassword ? 'text' : 'password'"
                class="form-control with-eye-input"
                id="new_password"
                placeholder="Enter new password"
                v-model="new_password"
                autocomplete="new-password"
              />
              <button
                type="button"
                class="eye-btn"
                @click="showNewPassword = !showNewPassword"
                :aria-label="showNewPassword ? 'Hide new password' : 'Show new password'"
                title="Toggle new password visibility"
              >
                <svg v-if="!showNewPassword" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a20.32 20.32 0 0 1 5.17-5.94"/>
                  <path d="M1 1l22 22"/>
                  <path d="M9.53 9.53A3 3 0 0 0 14.47 14.47"/>
                </svg>
              </button>
            </div>
          </div>

          <div class="mb-3">
            <label for="role" class="form-label">User Role</label>
            <input type="text" class="form-control" id="role" v-model="role" disabled>
          </div>

          <div class="mb-3">
            <label for="email" class="form-label">Email</label>
            <input type="email" class="form-control" id="email" v-model="email" disabled>
          </div>

          <button type="submit" class="btn btn-primary">Save Changes</button>
        </form>
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
    },
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
.input-with-eye {
  position: relative;
  display: flex;
  align-items: center;
}

.with-eye-input {
  padding-right: 42px; /* room for the button */
  width: 100%;
  box-sizing: border-box;
}

.eye-btn {
  position: absolute;
  right: 8px;
  background: transparent;
  border: none;
  height: 32px;
  width: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  top: 50%;
  transform: translateY(-50%);
  padding: 0;
  color: #495057; /* matches typical bootstrap input text color */
}

.eye-btn:focus {
  outline: 2px solid rgba(0,123,255,0.25);
  border-radius: 4px;
}

.eye-btn svg {
  pointer-events: none; /* let the button handle clicks */
}
</style>
