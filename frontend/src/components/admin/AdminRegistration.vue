<template>
  <section class="min-vh-100 d-flex align-items-center justify-content-center bg-body-tertiary bg-gradient py-5">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
          <div class="card shadow-lg border-0 rounded-4 overflow-hidden">
            <div class="card-header bg-primary bg-gradient text-white py-4">
              <h1 class="h4 mb-0 text-center fw-semibold">Admin Registration</h1>
              <p class="mb-0 text-center opacity-75 small">Create a secure administrator account to manage your org</p>
            </div>
            <div class="card-body p-4 p-md-5">
              <form @submit.prevent="registerAdmin" novalidate>
                <div class="form-floating mb-3">
                  <input type="text" id="name" v-model="name" class="form-control" placeholder="Jane Doe" required />
                  <label for="name">Full Name</label>
                </div>

                <div class="form-floating mb-3">
                  <input type="email" id="email" v-model="email" class="form-control" placeholder="jane@company.com"
                    required />
                  <label for="email">Work Email</label>
                </div>

                <div class="form-floating mb-4">
                  <input type="password" id="password" v-model="password" class="form-control" placeholder="Password"
                    required />
                  <label for="password">Password</label>
                </div>
                <div class="form-text mb-4">Use 8+ characters with a mix of letters, numbers, and symbols.</div>

                <button type="submit" class="btn btn-primary btn-lg w-100 shadow-sm">Create Account</button>
              </form>
            </div>
          </div>
          <p class="text-center text-muted mt-3 mb-0 small">By creating an account, you agree to our policies.</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'AdminRegistration',
  data() {
    return {
      name: '',
      email: '',
      password: ''
    };
  },
  methods: {
    registerAdmin() {
      console.log('Admin registered:', this.name, this.email, this.password);
      this.name = '';
      this.email = '';
      this.password = '';
    }
  }
};
</script>