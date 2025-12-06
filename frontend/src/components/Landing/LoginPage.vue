<template>
  <div class="login-root min-vh-100 d-flex flex-column p-3 p-md-4 position-relative"
    style="background-color: rgba(20, 40, 108, 0.85); font-family: 'Inter', sans-serif;">
    <div :style="bgLayerStyle" class="position-fixed top-0 start-0 w-100 h-100" style="z-index: -1;" aria-hidden="true">
    </div>

    <nav class="navbar navbar-expand-lg navbar-dark bg-transparent w-100">
      <div class="container-fluid">
        <a class="navbar-brand fs-3 fw-bold" href="/">Sync'em</a>
        <a class="navbar-brand fs-3 fw-bold" href="/">Home</a>
      </div>
    </nav>

    <main class="d-flex flex-column justify-content-center align-items-center flex-grow-1 container"
      style="max-width: 550px;">
      <h1 class="display-4 fw-bold text-center mb-4 text-white">
        Log in to Sync'em
      </h1>

      <p class="fs-5 text-center mb-4" style="color: #d1d5db;">
        Welcome back! Please enter your details.
      </p>

      <form @submit.prevent="handleLogin" class="w-100">
        <div class="mb-3">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <label for="email" class="form-label fs-5 text-white mb-0">Email Address</label>
          </div>
          <input id="email" type="email" v-model="email" placeholder="Enter your email address..." required
            class="form-control form-control-lg" />
        </div>

        <div class="mb-3">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <label for="password" class="form-label mb-0 fs-5 text-white">Password</label>
            <a href="#" class="text-decoration-none" style="color: #93c5fd;">Forgot password?</a>
          </div>

          <div class="position-relative">
            <input id="password" :type="showPassword ? 'text' : 'password'" v-model="password"
              placeholder="Enter your password..." required class="form-control form-control-lg pe-5"
              autocomplete="current-password" />

            <button type="button"
              class="btn btn-link position-absolute top-50 end-0 translate-middle-y text-decoration-none text-dark p-0 me-3 d-flex align-items-center justify-content-center"
              style="width: 30px; height: 30px;" @click="showPassword = !showPassword"
              :aria-label="showPassword ? 'Hide password' : 'Show password'"
              :title="showPassword ? 'Hide password' : 'Show password'">
              <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a20.32 20.32 0 0 1 5.17-5.94" />
                <path d="M1 1l22 22" />
                <path d="M9.53 9.53A3 3 0 0 0 14.47 14.47" />
              </svg>
            </button>
          </div>
        </div>

        <button type="submit" :disabled="loading" class="btn btn-primary btn-lg w-100 fw-semibold mt-3">
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
import bgImage from '@/assets/images/landing/landingPageBackgroundImage.png';

export default {
  name: 'LoginPage',
  data() {
    return {
      email: '',
      password: '',
      loading: false,
      error: '',
      showPassword: false,
    };
  },
  computed: {
    bgLayerStyle() {
      return {
        backgroundImage: `url(${bgImage})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        backgroundColor: 'rgba(20, 40, 108, 0.85)',
        backgroundBlendMode: 'overlay',
      };
    }
  },
  methods: {
    async handleLogin() {
      this.error = '';
      if (!this.email || !this.password) {
        this.error = 'Please fill out both fields.';
        return;
      }
      this.loading = true;
      try {
        await submitLogin({ email: this.email, password: this.password }, router);
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
.login-root {
  background: url('../../assets/images/landing/landingPageBackgroundImage.png') no-repeat center center/cover;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-link:focus {
  box-shadow: none;
}
</style>