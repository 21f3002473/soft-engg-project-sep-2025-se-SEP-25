<template>
  <div class="user-shell">
    <UserNavBar />
 
    <main class="content">
      <div class="page-header" v-if="title">
        <h1>{{ title }}</h1>
      </div>
      <section class="page-body">
        <router-view />
      </section>
    </main>

    <button class="chat-toggle" @click="toggleChat" :class="{ 'is-open': isChatOpen }">
      <span v-if="!isChatOpen">Need Help?</span>
      <span v-else>&times;</span>
    </button>
    
    <ChatPopup :is-open="isChatOpen" @close="toggleChat" />
  </div>
</template>
 
<script>
import UserNavBar from './UserNavBar.vue';
import ChatPopup from './ChatPopup.vue';

export default {
  name: 'UserLayout',
  components: { UserNavBar, ChatPopup },
  props: {
    title: { type: String, default: '' }
  },
  data() {
    return {
      isChatOpen: false
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
.user-shell { min-height: 100vh; background: #fafafa; }
.content { max-width:1100px; margin:20px auto; padding:12px; }
.page-header h1 { margin:0 0 12px 0; font-size:28px; font-weight:600; }
.page-body { background:#fff; border:1px solid #e6e6e6; border-radius:6px; padding:16px; min-height:200px; }

.chat-toggle {
  position: fixed;
  right: 30px;
  bottom: 30px;
  padding: 12px 24px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 24px;
  cursor: pointer;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  transition: all 0.3s ease;
  z-index: 1000;
}

.chat-toggle:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.2);
}

.chat-toggle.is-open {
  background: #dc3545;
  padding: 12px 16px;
  border-radius: 50%;
}
</style>
