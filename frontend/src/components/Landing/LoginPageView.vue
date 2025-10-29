<template>
  <div class="min-h-screen bg-gradient-to-br from-[#4F00BC] to-[#29007A] text-white font-sans p-6 md:p-10">
    
    <header class="w-full max-w-7xl mx-auto">
      <nav class="flex justify-between items-center">
        <div class="text-3xl font-bold tracking-tighter">
          Sync'em
        </div>
        
        <div class="flex items-center space-x-4">
          <span class="hidden sm:inline text-gray-300">Don't have an account?</span>
          <a
            href="#"
            class="bg-white text-[#007BFF] font-semibold px-5 py-2.5 rounded-lg text-sm hover:bg-gray-100 transition-colors"
          >
            Sign Up
          </a>
        </div>
      </nav>
    </header>

    <main class="flex-grow flex flex-col justify-center items-center w-full max-w-md mx-auto pt-20 md:pt-32">
      
      <h1 class="text-4xl md:text-5xl font-bold text-center mb-6">
        Log in to Sync'em
      </h1>
      
      <p class="text-lg text-gray-300 text-center mb-10">
        Welcome back! Please enter your details.
      </p>

  <form @submit.prevent="handleLogin" class="w-full space-y-5">
        
        <div>
          <label for="email" class="block text-sm font-medium text-gray-200 mb-2">Email address</label>
          <input
            id="email"
            type="email"
            v-model="email"
            placeholder="Enter your email address..."
            required
            class="w-full px-4 py-3.5 rounded-lg border-none text-gray-900 placeholder-gray-500 bg-white focus:ring-2 focus:ring-blue-400 focus:outline-none"
          />
        </div>

        <div>
          <div class="flex justify-between items-baseline mb-2">
            <label for="password" class="block text-sm font-medium text-gray-200">Password</label>
            <a href="#" class="text-sm text-blue-300 hover:text-blue-200">Forgot password?</a>
          </div>
          <input
            id="password"
            type="password"
            v-model="password"
            placeholder="Enter your password..."
            required
            class="w-full px-4 py-3.5 rounded-lg border-none text-gray-900 placeholder-gray-500 bg-white focus:ring-2 focus:ring-blue-400 focus:outline-none"
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-[#007BFF] disabled:opacity-60 disabled:cursor-not-allowed text-white font-semibold px-6 py-3.5 rounded-lg text-base hover:bg-blue-600 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 focus:ring-offset-purple-800"
        >
          {{ loading ? 'Logging in…' : 'Log In' }}
        </button>

        <p v-if="error" class="text-red-200 text-sm" role="alert">{{ error }}</p>

      </form>
    </main>

  </div>
</template>

<script>
import { submitLogin } from '@/store/appState.js';
import router from '@/router/router.js';

export default {
  name: 'LoginPageView',
  data() {
    return {
        email:'',
        password:'',
        loading:false,
        error:'',
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
      console.log('Attempting login with', this.email, this.password);
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
.font-sans {
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, 
                "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
}

/* For Sampriti - Add any additional custom styles here if needed */
</style>






