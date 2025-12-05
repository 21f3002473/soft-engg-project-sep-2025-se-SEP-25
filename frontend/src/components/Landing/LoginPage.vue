<template>
  <div
    class="min-vh-100 d-flex flex-column bg-gradient text-white p-3 p-md-4 bg-image root-stack"
  >
    <!-- background layer placed first so it's positioned behind all content -->
    <div :style="bgLayerStyle" class="bg-layer" aria-hidden="true"></div>
    
      <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container-fluid">
          <a class="navbar-brand fs-3 fw-bold" href="/">Sync'em</a>
          <!-- <div class="d-flex align-items-center">
            <span class="d-none d-sm-inline text-light me-3">Don't have an account?</span>
            <a href="" class="btn btn-light text-primary fw-semibold">Sign Up</a>
          </div> -->
          <a class="navbar-brand fs-3 fw-bold" href="/">Home</a>
        </div>
      </nav>

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

        <!-- Password field with eye toggle -->
        <div class="mb-3">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <label for="password" class="form-label mb-0">Password</label>
            <a href="#" class="text-decoration-none" style="color: #93c5fd;">Forgot password?</a>
          </div>

          <div class="input-with-eye">
            <input
              id="password"
              :type="showPassword ? 'text' : 'password'"
              v-model="password"
              placeholder="Enter your password..."
              required
              class="form-control form-control-lg with-eye-input"
              autocomplete="current-password"
            />

            <button
              type="button"
              class="eye-btn"
              @click="showPassword = !showPassword"
              :aria-label="showPassword ? 'Hide password' : 'Show password'"
              :title="showPassword ? 'Hide password' : 'Show password'"
            >
              <!-- eye open -->
              <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" width="18" height="18"
                   viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                   stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
                <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>

              <!-- eye slash -->
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18"
                   viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                   stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
                <path d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a20.32 20.32 0 0 1 5.17-5.94"/>
                <path d="M1 1l22 22"/>
                <path d="M9.53 9.53A3 3 0 0 0 14.47 14.47"/>
              </svg>
            </button>
          </div>
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
// import background so bundler resolves path
import bgImage from '@/assets/images/landing/landingPageBackgroundImage.png';

export default {
  name: 'LoginPage',
  data() {
    return {
      email: '',
      password: '',
      loading: false,
      error: '',
      showPassword: false, // <- added toggle state
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
      // console.log('Attempting login with', this.email, this.password);
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
/* root stacking context so bg-layer z-index:-1 sits behind everything */
.root-stack {
  position: relative;
  z-index: 0;
}

.bg-layer {
  position: fixed;
  inset: 0; /* shorthand for top:0; right:0; bottom:0; left:0; */
  z-index: -1;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-blend-mode: overlay;
  /* fallback color when image fails to load */
  background-color: rgba(20, 40, 108, 0.85);
  /* optional subtle blur */
  /* filter: blur(0.5px); */
}

.bg-gradient {
  /* keep font and blend-mode but avoid direct url() here so bundler does not misresolve */
  /* background: linear-gradient(to bottom right, #4F00BC, #29007A); */
  /* background: url('../../assets/images/landing/landingPageBackgroundImage.png') no-repeat center center/cover; */
  /* background-color: rgba(20, 40, 108, 0.85); */
  background-blend-mode: overlay;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial,
                "Noto Sans", sans-serif;
}

/* kept as fallback; main image is applied via bg-layer to ensure bundler resolves the path */
/* .bg-image {
  background: url('../../assets/images/landing/landingPageBackgroundImage.png') no-repeat center center/cover;
  background-color: rgba(20, 40, 108, 0.85);
  background-blend-mode: overlay;
} */

.btn-primary {
  /* background-color: #007BFF; */
  /* border-color: #007BFF; */
}

.btn-primary:hover {
  /* background-color: #0056b3; */
  /* border-color: #0056b3; */
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* --- password eye styles --- */
.input-with-eye {
  position: relative;
  display: flex;
  align-items: center;
}

.with-eye-input {
  padding-right: 42px !important; /* leave space for the eye button */
}

.eye-btn {
  position: absolute;
  right: 10px;
  background: transparent;
  border: none;
  cursor: pointer;
  height: 34px;
  width: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  top: 50%;
  transform: translateY(-50%);
  padding: 0;
  color: black;
}

.eye-btn svg {
  pointer-events: none;
}

.eye-btn:focus {
  outline: 2px solid rgba(255,255,255,0.12);
  border-radius: 4px;
}
</style>
