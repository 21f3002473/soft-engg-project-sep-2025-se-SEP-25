<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <div class="nav-links">
        <router-link :to="{ name: 'AdminDashboard' }" class="router-link-exact-active">Dashboard</router-link>
        <router-link :to="{ name: 'AdminAddEmployee' }" class="router-link-exact-active">Add Employee</router-link>
        <router-link :to="{ name: 'AdminLogs' }" class="router-link-exact-active">Logs</router-link>
        <router-link :to="{ name: 'AdminUpdates' }" class="router-link-exact-active">Updates</router-link>
        <router-link :to="{ name: 'AdminBackups' }" class="router-link-exact-active">Backups</router-link>
      </div>
      <div class="account-link">
        <router-link :to="{ name: 'AdminAccount' }">Account</router-link>
        <button class="btn logout-btn" @click="logout">Logout</button>
      </div>
    </header>

    <main class="dashboard-content">
      <router-view />
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
.dashboard {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background-color: #f4f7f6;
  height: 100vh;
  color: #333;
}

a {
  text-decoration: none;
  color: #555;
  font-size: 14px;
}

a:hover {
  color: #000;
}

.btn {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: #f9f9f9;
  cursor: pointer;
  font-size: 14px;
}

.btn:hover {
  background-color: #eee;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  background-color: #ffffff;
  border-bottom: 1px solid #ddd;
}

.nav-links a {
  margin-right: 25px;
}

.account-link a {
  font-weight: bold;

}

.dashboard-content {
  padding: 25px 30px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.content-header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
}

.main-area {
  display: flex;
  gap: 25px;
}

.employee-list {
  flex: 3;
  background-color: #ffffff;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.employee-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.employee-item:last-child {
  border-bottom: none;
}

.emp-name {
  font-weight: 600;
  flex-basis: 10%;
}

.emp-status {
  flex-basis: 10%;
  text-align: center;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.emp-status.new {
  background-color: #e0f8e0;
  color: #006400;
}

.emp-status.old {
  background-color: #eee;
  color: #555;
}

.status-dropdown {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: #f9f9f9;
  flex-grow: 1;
}

.chatbot-panel {
  flex: 1;
  background-color: #ffffff;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.chatbot-panel h3 {
  margin-top: 0;
  margin-bottom: 15px;
  text-align: center;
  font-weight: 600;
}

.chat-history {
  flex-grow: 1;
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 15px;
  min-height: 250px;
  font-family: monospace;
  color: #666;
  overflow-y: auto;
}

.btn-ai {
  background-color: #ececec;
  border: none;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  font-weight: bold;
  align-self: center;
  margin-top: auto;
}

.chat-trigger {
  position: fixed;
  right: 24px;
  bottom: 24px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  background: #111827;
  color: #fff;
  font-weight: 700;
  letter-spacing: 0.5px;
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.25);
  cursor: pointer;
  z-index: 2000;
  transition: transform 0.15s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.chat-trigger:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 34px rgba(0, 0, 0, 0.28);
  background: #0b1220;
}

.chat-window {
  position: fixed;
  right: 24px;
  bottom: 90px;
  width: 340px;
  max-height: 70vh;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.22);
  overflow: hidden;
  z-index: 2000;
}

.chat-header {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
}

.chat-header .title {
  font-weight: 600;
  font-size: 14px;
}

.chat-header .spacer {
  flex: 1;
}

.chat-header .close {
  border: none;
  background: transparent;
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
  color: #6b7280;
}

.chat-header .close:hover {
  color: #111827;
}

.chat-body {
  padding: 12px;
  gap: 8px;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  background: #ffffff;
}

.message {
  max-width: 80%;
  padding: 8px 10px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.35;
  word-wrap: break-word;
}

.message.ai {
  align-self: flex-start;
  background: #f1f5f9;
  color: #0f172a;
  border-top-left-radius: 4px;
}

.message.user {
  align-self: flex-end;
  background: #2563eb;
  color: #ffffff;
  border-top-right-radius: 4px;
}

.chat-input {
  display: flex;
  gap: 8px;
  border-top: 1px solid #e5e7eb;
  padding: 10px;
  background: #fafafa;
}

.chat-input input {
  flex: 1;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 13px;
  outline: none;
}

.chat-input input:focus {
  border-color: #93c5fd;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.chat-input button {
  border: none;
  border-radius: 10px;
  padding: 10px 14px;
  font-weight: 600;
  background: #111827;
  color: #fff;
  cursor: pointer;
}

.chat-input button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(6px) scale(0.995);
}

.logout-btn {
  margin-left: 20px;
  padding: 6px 12px;
  background-color: #ef4444;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
}

.logout-btn:hover {
  background-color: #dc2626;
}
</style>