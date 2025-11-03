<template>
  <div class="user-shell">
    <!-- Navbar -->
    <UserNavBar />

    <!-- Page Content -->
    <main class="content">
      <transition name="fade-slide" mode="out-in">
        <div v-if="title" key="title" class="page-header">
          <h1 class="page-title">{{ title }}</h1>
          <div class="page-divider"></div>
        </div>
      </transition>

      <section class="page-body">
        <router-view />
      </section>
    </main>

    <!-- Floating Chat Button -->
    <button
      class="chat-toggle"
      @click="toggleChat"
      :class="{ 'is-open': isChatOpen }"
    >
      <span v-if="!isChatOpen">💬 Need Help?</span>
      <span v-else>&times;</span>
    </button>

    <!-- Chat Popup -->
    <ChatPopup :is-open="isChatOpen" @close="toggleChat" />
  </div>
</template>

<script>
import UserNavBar from './fragments/NavBar.vue';
import ChatPopup from './fragments/ChatPopup.vue';

export default {
  name: 'UserLayout',
  components: { UserNavBar, ChatPopup },
  props: {
    title: { type: String, default: '' }
  },
  data() {
    return { isChatOpen: false };
  },
  methods: {
    toggleChat() {
      this.isChatOpen = !this.isChatOpen;
    }
  }
};
</script>

<style scoped>
/* Layout base */
.user-shell {
  min-height: 100vh;
  background: linear-gradient(135deg, #e9f1ff 0%, #f9fbff 100%);
  display: flex;
  flex-direction: column;
}

/* Content area */
.content {
  max-width: 1200px;
  margin: 16px auto 32px; /* reduced top margin */
  padding: 16px;
  width: 90%;
}

/* Header */
.page-header {
  text-align: left;
  margin-bottom: 16px; /* tighter header spacing */
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e3a8a;
  margin-bottom: 6px;
}

.page-divider {
  height: 3px;
  width: 50px;
  background: #3b82f6;
  border-radius: 6px;
}

/* Page Body */
.page-body {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
  backdrop-filter: blur(5px);
  min-height: 250px;
  transition: all 0.3s ease;
}

/* Floating Chat Button */
.chat-toggle {
  position: fixed;
  right: 30px;
  bottom: 30px;
  padding: 14px 28px;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff;
  border: none;
  border-radius: 40px;
  cursor: pointer;
  font-weight: 600;
  letter-spacing: 0.5px;
  box-shadow: 0 8px 16px rgba(37, 99, 235, 0.4);
  transition: all 0.3s ease;
  z-index: 1000;
}

.chat-toggle:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(37, 99, 235, 0.5);
}

.chat-toggle.is-open {
  background: #dc2626;
  border-radius: 50%;
  padding: 12px 16px;
  width: 56px;
  height: 56px;
  font-size: 24px;
}

/* Animations */
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