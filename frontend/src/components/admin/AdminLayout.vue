<template>
  <div class="user-shell d-flex flex-column min-vh-100">
    <header class="d-flex justify-content-between align-items-center px-4 py-3 bg-white border-bottom shadow-sm">
      <div class="d-flex gap-4 align-items-center">
        <router-link :to="{ name: 'AdminDashboard' }"
          class="text-decoration-none text-secondary fw-medium">Dashboard</router-link>
        <router-link :to="{ name: 'AdminAddEmployee' }" class="text-decoration-none text-secondary fw-medium">Add
          Employee</router-link>
        <router-link :to="{ name: 'AdminLogs' }"
          class="text-decoration-none text-secondary fw-medium">Logs</router-link>
        <router-link :to="{ name: 'AdminUpdates' }"
          class="text-decoration-none text-secondary fw-medium">Updates</router-link>
        <router-link :to="{ name: 'AdminBackups' }"
          class="text-decoration-none text-secondary fw-medium">Backups</router-link>
      </div>
      <div class="d-flex align-items-center gap-3">
        <router-link :to="{ name: 'AdminAccount' }" class="text-decoration-none text-dark fw-bold">Account</router-link>
        <button class="btn btn-sm btn-danger" @click="logout">Logout</button>
      </div>
    </header>

    <main class="container-xl flex-grow-1 my-4 px-3" style="max-width: 1200px;">
      <transition name="fade-slide" mode="out-in">
        <div v-if="$route.meta.title || title" key="title" class="mb-4 text-start">
          <h1 class="fw-bold mb-2" style="color: #1e3a8a; font-size: 28px;">{{ $route.meta.title || title }}</h1>
          <div class="bg-primary rounded-pill" style="height: 3px; width: 50px;"></div>
        </div>
      </transition>

      <section class="page-body shadow p-4 rounded-4 bg-white bg-opacity-75"
        style="backdrop-filter: blur(5px); min-height: 250px;">
        <router-view />
      </section>
    </main>
  </div>
</template>

<script>
export default {
  name: 'AdminLayout',
  props: {
    title: { type: String, default: '' }
  },
  data() {
    return {
      isChatbotOpen: false,
      messages: [{ from: 'ai', text: "Hi! I'm your assistant. How can I help?" }],
      draft: '',
    };
  },
  methods: {
    sendMessage() {
      if (!this.draft.trim()) return;
      this.messages.push({ from: 'user', text: this.draft.trim() });

      setTimeout(() => {
        this.messages.push({ from: 'ai', text: "This is a simulated AI response." });
        this.$nextTick(() => {
          const chatBody = this.$refs.scrollArea;
          if (chatBody) {
            chatBody.scrollTop = chatBody.scrollHeight;
          }
        });
      }, 1000);
      this.draft = '';
    },
    async logout() {
      this.$store.dispatch('logout');
      this.$router.push({ name: 'Login' });
    },
  }
};
</script>

<style scoped>
.user-shell {
  background: linear-gradient(135deg, #e9f1ff 0%, #f9fbff 100%);
}

.router-link-exact-active {
  color: #0d6efd !important;
  /* Bootstrap primary color */
  font-weight: 700 !important;
  position: relative;
}

.router-link-exact-active::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #0d6efd;
  border-radius: 2px;
}

a:hover {
  color: #000 !important;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>