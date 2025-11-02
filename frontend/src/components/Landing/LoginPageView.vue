<template>
  <div class="min-vh-100 d-flex flex-column bg-gradient text-white p-3 p-md-4">
    
    <header class="container">
      <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container-fluid">
          <a class="navbar-brand fs-3 fw-bold" href="#">Sync'em</a>
          <div class="d-flex align-items-center">
            <span class="d-none d-sm-inline text-light me-3">Don't have an account?</span>
            <a href="" class="btn btn-light text-primary fw-semibold">Sign Up</a>
          </div>
        </div>
      </nav>
    </header>

    <main class="d-flex flex-column justify-content-center align-items-center flex-grow-1 container" style="max-width: 500px;">
      
      <h1 class="display-4 fw-bold text-center mb-4">
        Log in to Sync'em
      </h1>
      
      <p class="fs-5 text-center mb-4" style="color: #d1d5db;">
        Welcome back! Please enter your details.
      </p>

      <form @submit.prevent="handleLogin" class="w-100">
        
        <div class="mb-3">
          <label for="email" class="form-label">Email address</label>
          <input
            id="email"
            type="email"
            v-model="email"
            placeholder="Enter your email address..."
            required
            class="form-control form-control-lg"
          />
        </div>

        <div class="mb-3">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <label for="password" class="form-label mb-0">Password</label>
            <a href="#" class="text-decoration-none" style="color: #93c5fd;">Forgot password?</a>
          </div>
          <input
            id="password"
            type="password"
            v-model="password"
            placeholder="Enter your password..."
            required
            class="form-control form-control-lg"
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="btn btn-primary btn-lg w-100 fw-semibold mt-3"
        >
          {{ loading ? 'Logging in…' : 'Log In' }}
        </button>

        <p v-if="error" class="alert alert-danger mt-3 mb-0" role="alert">{{ error }}</p>

      </form>
    </main>

  </div>
</template>

<script>
import 'bootstrap/dist/css/bootstrap.min.css';
import { submitLogin } from '@/store/appState.js';
import router from '@/router/router.js';

export default {
  name: 'LoginPageView',
  data() {
    return {
      email: '',
      password: '',
      loading: false,
      error: '',
    };
  },
  methods: {
    async handleLogin() {
      this.error = '';
      if (!this.email || !this.password) {
        this.error = 'Please fill out both fields.';
        return;
      }
      this.loading = true;
      console.log('Attempting login with', this.email, this.password);
      try {
        let response = await submitLogin({ email: this.email, password: this.password }, router);
        console.log('Login response:', response);
      } catch (e) {
        this.error = e?.message || 'Login failed. Please try again.';
      } finally {
        this.loading = false;
      }
    }
  },
};
</script>



<style scoped>
.bg-gradient {
  background: linear-gradient(to bottom right, #4F00BC, #29007A);
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial,
                "Noto Sans", sans-serif;
}

.btn-primary {
  background-color: #007BFF;
  border-color: #007BFF;
}

.btn-primary:hover {
  background-color: #0056b3;
  border-color: #0056b3;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

