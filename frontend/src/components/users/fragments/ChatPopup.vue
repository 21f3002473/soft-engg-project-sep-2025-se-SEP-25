<template>
  <Transition name="slide">
    <div v-if="isOpen" class="chat-popup">
      <!-- Header -->
      <div class="chat-header">
        <div class="chat-header-info">
          <div class="chat-avatar">🤖</div>
          <div>
            <h3>Sync’em AI Assistant</h3>
            <span class="status-dot"></span><span class="status">Online</span>
          </div>
        </div>
      </div>

      <!-- Messages -->
      <div class="chat-messages" ref="messagesContainer">
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          :class="['message', msg.sender]"
        >
          <div class="message-content">{{ msg.text }}</div>
          <div class="message-time">{{ formatTime(msg.time) }}</div>
        </div>

        <div v-if="isTyping" class="typing-indicator">
          <span></span><span></span><span></span>
        </div>
      </div>

      <!-- Input -->
      <div class="chat-input">
        <input
          type="text"
          v-model="newMessage"
          @keyup.enter="sendMessage"
          placeholder="Ask me anything..."
        />
        <button @click="sendMessage" :disabled="!newMessage.trim()">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
          </svg>
        </button>
      </div>
    </div>
  </Transition>
</template>

<script>
export default {
  name: "ChatPopup",
  props: { isOpen: Boolean },
  data() {
    return {
      messages: [
        {
          text: "Hey there! I’m your Sync’em AI assistant. How can I help today?",
          sender: "bot",
          time: new Date()
        }
      ],
      newMessage: "",
      isTyping: false
    };
  },
  methods: {
    formatTime(date) {
      return new Intl.DateTimeFormat("en", {
        hour: "2-digit",
        minute: "2-digit"
      }).format(date);
    },
    async sendMessage() {
      if (!this.newMessage.trim()) return;

      // Add user message
      this.messages.push({
        text: this.newMessage,
        sender: "user",
        time: new Date()
      });
      const userMessage = this.newMessage;
      this.newMessage = "";

      // Simulate typing
      this.isTyping = true;
      await new Promise((r) => setTimeout(r, 1200));

      // Bot response
      this.isTyping = false;
      this.messages.push({
        text: `Got it! You mentioned "${userMessage}". Let me process that for you.`,
        sender: "bot",
        time: new Date()
      });

      this.$nextTick(() => {
        const el = this.$refs.messagesContainer;
        el.scrollTop = el.scrollHeight;
      });
    }
  }
};
</script>

<style scoped>
/* Overall popup container */
.chat-popup {
  position: fixed;
  right: 28px;
  bottom: 100px;
  width: 380px;
  height: 540px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(16px);
  border-radius: 20px;
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: fadeIn 0.3s ease;
}

/* Entry animation */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Slide transition */
.slide-enter-active, .slide-leave-active {
  transition: all 0.3s ease;
}
.slide-enter-from, .slide-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

/* Header */
.chat-header {
  padding: 14px 18px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(90deg, #007bff, #0056d2);
  color: #fff;
}

.chat-header-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chat-avatar {
  width: 36px;
  height: 36px;
  background: #fff;
  color: #007bff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #2ecc71;
  border-radius: 50%;
  display: inline-block;
  margin-right: 4px;
}

/* Messages */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: #f8faff;
}

.message {
  padding: 10px 14px;
  border-radius: 14px;
  max-width: 80%;
  word-break: break-word;
  position: relative;
  animation: fadeIn 0.2s ease;
}

.message.bot {
  background: #e8f0ff;
  color: #004085;
  align-self: flex-start;
  border: 1px solid #d0e0ff;
}

.message.user {
  background: linear-gradient(90deg, #007bff, #0056d2);
  color: #fff;
  align-self: flex-end;
}

.message-time {
  font-size: 11px;
  color: #666;
  margin-top: 3px;
  text-align: right;
}

/* Typing dots */
.typing-indicator {
  display: flex;
  gap: 5px;
  padding: 6px;
  align-self: flex-start;
}
.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #cbd5e1;
  border-radius: 50%;
  animation: typing 1s infinite ease-in-out;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 100% { transform: translateY(0); opacity: 0.6; }
  50% { transform: translateY(-4px); opacity: 1; }
}

/* Input area */
.chat-input {
  padding: 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
  display: flex;
  gap: 10px;
  background: #fff;
}

.chat-input input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #ccc;
  border-radius: 20px;
  outline: none;
  transition: border 0.2s;
}

.chat-input input:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.15);
}

.chat-input button {
  background: linear-gradient(90deg, #007bff, #0056d2);
  color: white;
  border: none;
  border-radius: 50%;
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.chat-input button:hover {
  background: linear-gradient(90deg, #0069d9, #004ab3);
  transform: translateY(-2px);
}
</style>
