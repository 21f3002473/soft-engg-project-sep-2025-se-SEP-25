<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <div class="nav-links">
        <router-link :to="{ name: 'AdminDashboard' }">Dashboard</router-link>
        <router-link :to="{ name: 'SystemStatus' }">System Status</router-link>
        <router-link :to="{ name: 'Logs' }">Logs</router-link>
        <router-link :to="{ name: 'Updates' }">Updates</router-link>
        <router-link :to="{ name: 'Backups' }">Backups</router-link>
      </div>
      <div class="account-link">
        <router-link :to="{ name: 'Account' }">Account</router-link>
      </div>
    </header>

    <main class="dashboard-content">
      <router-view />
    </main>

    <div class="chat-float">
      <button
        class="chat-trigger"
        @click="isChatbotOpen = !isChatbotOpen"
        aria-label="Open AI chat"
      >
        AI
      </button>
      <transition name="fade-slide">
        <section
          v-if="isChatbotOpen"
          class="chat-window"
          role="dialog"
        >
          <header class="chat-header">
            <div class="title">AI Assistant</div>
            <div class="spacer"></div>
            <button class="close" @click="isChatbotOpen = false" aria-label="Close chat">×</button>
          </header>
          <div class="chat-body" ref="scrollArea" aria-live="polite">
            <div
              v-for="(m, i) in messages"
              :key="i"
              :class="['message', m.from]"
            >
              {{ m.text }}
            </div>
          </div>
          <form class="chat-input" @submit.prevent="sendMessage">
            <input
              v-model="draft"
              type="text"
              placeholder="Type a message…"
            />
            <button type="submit" :disabled="!draft.trim()">Send</button>
          </form>
        </section>
      </transition>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminLayout',
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
  }
};
</script>