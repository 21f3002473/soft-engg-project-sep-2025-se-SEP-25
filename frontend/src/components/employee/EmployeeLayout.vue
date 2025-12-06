<template>
  <div class="user-shell d-flex flex-column min-vh-100">
    <UserNavBar />

    <main class="container-xl flex-grow-1 my-4 px-3" style="max-width: 1200px;">
      <transition name="fade-slide" mode="out-in">
        <div v-if="title" key="title" class="mb-4 text-start">
          <h1 class="fw-bold mb-2" style="color: #1e3a8a; font-size: 28px;">{{ title }}</h1>
          <div class="bg-primary rounded-pill" style="height: 3px; width: 50px;"></div>
        </div>
      </transition>

      <section class="page-body shadow p-4 rounded-4 bg-white bg-opacity-75"
        style="backdrop-filter: blur(5px); min-height: 250px;">
        <router-view />
      </section>
    </main>

    <button class="chat-toggle btn position-fixed shadow-lg d-flex align-items-center justify-content-center border-0"
      @click="toggleChat" :class="isChatOpen ? 'btn-danger rounded-circle' : 'btn-primary rounded-pill'"
      :style="chatButtonStyle">
      <span v-if="!isChatOpen" class="fw-semibold d-flex align-items-center">
        <i class="bi bi-robot me-2 fs-5"></i>AI Assistant
      </span>
      <i v-else class="bi bi-x-lg fs-4"></i>
    </button>

    <ChatPopup :is-open="isChatOpen" @close="toggleChat" />
  </div>
</template>

<script>
import UserNavBar from './fragments/EmployeeNavBar.vue';
import ChatPopup from './fragments/EmployeeChatPopup.vue';

export default {
  name: 'EmployeeLayout',
  components: { UserNavBar, ChatPopup },
  props: {
    title: { type: String, default: '' }
  },
  data() {
    return { isChatOpen: false };
  },
  computed: {
    chatButtonStyle() {
      const baseStyle = {
        right: '30px',
        bottom: '30px',
        zIndex: 1000,
        transition: 'all 0.3s ease'
      };

      if (this.isChatOpen) {
        return {
          ...baseStyle,
          width: '56px',
          height: '56px',
          padding: '0'
        };
      }

      return {
        ...baseStyle,
        padding: '14px 28px',
        background: 'linear-gradient(135deg, #2563eb, #1d4ed8)'
      };
    }
  },
  methods: {
    toggleChat() {
      this.isChatOpen = !this.isChatOpen;
    }
  }
};
</script>

<style scoped>
.user-shell {
  background: linear-gradient(135deg, #e9f1ff 0%, #f9fbff 100%);
}

.chat-toggle:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(37, 99, 235, 0.5) !important;
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