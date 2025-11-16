<template>
  <div class="dashboard">
    <main class="dashboard-content">
      <div class="content-header">
        <h1>{{ title }}</h1>
        <div class="search-bar">
          <svg class="icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
            <path d="M11 4a7 7 0 1 1 0 14 7 7 0 0 1 0-14zm0-2a9 9 0 1 0 5.293 16.293l4.707 4.707-1.414 1.414-4.707-4.707A9 9 0 0 0 11 2z" />
          </svg>
          <input class="search-input" type="text" placeholder="Search" v-model="searchQuery" aria-label="Search employees by name" />
          </div>
      </div>

  <div class="main-area">
        
        <div class="employee-list">
          <div class="employee-item" v-for="emp in filteredEmployees" :key="emp.id">
            <span class="emp-name">{{ emp.name }}</span>
            <span class="emp-status" :class="emp.status.toLowerCase().replace('!', '')">
              {{ emp.status }}
            </span>
            <button class="btn" @click="changeStatus">Change Status</button>
            <select class="status-dropdown">
              <option value="">Status Change Dropdown</option>
              <option value="active">Set Active</option>
              <option value="pending">Set Pending</option>
              <option value="disabled">Set Disabled</option>
            </select>
          </div>
        </div>

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
            aria-modal="true"
            aria-label="AI Assistant"
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
                autocomplete="off"
                />
                <button type="submit" :disabled="!draft.trim()">Send</button>
            </form>
            </section>
        </transition>
        </div>

      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'AdminDashboard',
  props: {
    title: {
      type: String,
      default: 'Super Admin Dashboard'
    }
  },
  data() {
    return {
      employees: [
        { id: 1, name: 'EMP1', status: 'New!' },
        { id: 2, name: 'EMP2', status: 'Old' },
        { id: 3, name: 'EMP3', status: 'New!' },
        { id: 4, name: 'EMP4', status: 'New!' },
        { id: 5, name: 'EMP5', status: 'New!' },
        { id: 6, name: 'EMP6', status: 'New!' }
      ],
      isChatbotOpen: this?.isChatbotOpen ?? false,
        messages: [{ from: 'ai', text: "Hi! I'm your assistant. How can I help?" }],
        draft: '',
        searchQuery: '',
    };
  },
  computed: {
    filteredEmployees() {
      console.log('Search query changed to:', this.searchQuery);

      
      if (!this.searchQuery) {
        return this.employees;
      }

      return this.employees.filter(emp => {
        return emp.name.toLowerCase().includes(this.searchQuery.toLowerCase());
      });
    }
  },
  watch: {
    searchQuery(newQuery) {
      console.log('Search query Typed by Admin:', newQuery);
    }
  },
  methods: {
    async fetchData() {
      console.log('Fetching data...');
      // API call would go here
    },
    changeStatus() {
      console.log('Change status');
      // Logic to change status would go here
    },
    sendMessage() {
      if (!this.draft.trim()) return;

      // Add user message
      this.messages.push({ from: 'user', text: this.draft.trim() });

      // Simulate AI response
      setTimeout(() => {
        this.messages.push({ from: 'ai', text: "This is a simulated AI response." });
        this.$nextTick(() => {
          const chatBody = this.$refs.scrollArea;
          chatBody.scrollTop = chatBody.scrollHeight;
        });
      }, 1000);

      // Clear draft
      this.draft = '';
    },
  },
  mounted() {
    // Code to run when the component is mounted
    this.fetchData();
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

/* 1. Header Navigation */
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

/* 2. Main Content Area */
.dashboard-content {
  padding: 25px 30px;
}

/* 2a. Content Header (Title + Search) */
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

/* Search Bar */
.search-bar {
  position: relative;
  width: 260px;
  display: flex;
  align-items: center;
}
.search-bar .icon {
  position: absolute;
  left: 14px;
  width: 18px;
  height: 18px;
  fill: #6b7280; /* gray-500 */
  pointer-events: none;
}
.search-bar .search-input {
  width: 100%;
  padding: 10px 14px 10px 40px;
  border: 1px solid #d1d5db; /* gray-300 */
  border-radius: 10px;
  background: #ffffff;
  font-size: 14px;
  color: #1f2937; /* gray-800 */
  transition: border-color 0.18s ease, box-shadow 0.18s ease, background 0.25s ease;
}
.search-bar .search-input::placeholder {
  color: #9ca3af; /* gray-400 */
}
.search-bar .search-input:focus {
  outline: none;
  border-color: #2563eb; /* blue-600 */
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
  background: #f8fafc; /* slate-50 */
}
.search-bar .search-input:hover:not(:focus) {
  border-color: #9ca3af; /* gray-400 */
}

/* 2b. Main Area (List + Chat) */
.main-area {
  display: flex;
  gap: 25px; 
}

/* Employee List (Left) */
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

/* Chatbot Panel (Right) */
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

/* Floating trigger button */
.chat-trigger {
  position: fixed;
  right: 24px;
  bottom: 24px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  background: #111827; /* near-black */
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

/* Chat window container */
.chat-window {
  position: fixed;
  right: 24px;
  bottom: 90px;
  width: 340px;
  max-height: 70vh;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border: 1px solid #e5e7eb; /* gray-200 */
  border-radius: 12px;
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.22);
  overflow: hidden;
  z-index: 2000;
}

/* Header */
.chat-header {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  background: #f8fafc; /* slate-50 */
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
  color: #6b7280; /* gray-500 */
}
.chat-header .close:hover {
  color: #111827; /* gray-900 */
}

/* Body */
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
  background: #f1f5f9; /* slate-100 */
  color: #0f172a;       /* slate-900 */
  border-top-left-radius: 4px;
}
.message.user {
  align-self: flex-end;
  background: #2563eb; /* blue-600 */
  color: #ffffff;
  border-top-right-radius: 4px;
}

/* Input area */
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
  border-color: #93c5fd; /* blue-300 */
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15); /* blue-500/15% */
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

/* Open/close transition */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(6px) scale(0.995);
}
</style>