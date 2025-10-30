<template>
  <Transition name="slide">
    <div v-if="isOpen" class="chat-popup">
      <div class="chat-header">
        <div class="chat-header-info">
          <div class="chat-avatar">AI</div>
          <div>
            <h3>AI Assistant</h3>
            <span class="status">Online</span>
          </div>
        </div>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>

      <div class="chat-messages" ref="messagesContainer">
        <div v-for="(msg, idx) in messages" 
             :key="idx" 
             :class="['message', msg.sender]"
             :data-time="msg.time">
          <div class="message-content">{{ msg.text }}</div>
          <div class="message-time">{{ formatTime(msg.time) }}</div>
        </div>
        <div v-if="isTyping" class="typing-indicator">
          <span></span><span></span><span></span>
        </div>
      </div>

      <div class="chat-input">
        <input type="text" 
               v-model="newMessage" 
               @keyup.enter="sendMessage"
               placeholder="Type your message..." />
        <button @click="sendMessage" :disabled="!newMessage.trim()">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
        </button>
      </div>
    </div>
  </Transition>
</template>

<script>
export default {
  name: 'ChatPopup',
  props: {
    isOpen: Boolean
  },
  data() {
    return {
      messages: [
        { 
          text: 'Hello! How can I assist you today?',
          sender: 'bot',
          time: new Date()
        }
      ],
      newMessage: '',
      isTyping: false
    }
  },
  methods: {
    formatTime(date) {
      return new Intl.DateTimeFormat('en', {
        hour: 'numeric',
        minute: 'numeric'
      }).format(date);
    },
    async sendMessage() {
      if (!this.newMessage.trim()) return;
      
      // Add user message
      this.messages.push({
        text: this.newMessage,
        sender: 'user',
        time: new Date()
      });
      const userMessage = this.newMessage;
      this.newMessage = '';
      
      // Show typing indicator
      this.isTyping = true;
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Add bot response
      this.isTyping = false;
      this.messages.push({
        text: `I understand you're asking about "${userMessage}". Let me help you with that.`,
        sender: 'bot',
        time: new Date()
      });
    }
  }
}
</script>

<style scoped>
.chat-popup {
  position: fixed;
  right: 30px;
  bottom: 100px;
  width: 360px;
  height: 520px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 5px 25px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateY(30px);
  opacity: 0;
}

.chat-header {
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chat-avatar {
  width: 36px;
  height: 36px;
  background: #007bff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.status {
  font-size: 12px;
  color: #28a745;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 0 4px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message {
  padding: 8px 12px;
  border-radius: 12px;
  max-width: 80%;
  word-break: break-word;
}

.message-content {
  white-space: pre-wrap;
}

.message.bot {
  background: #f0f0f0;
  align-self: flex-start;
}

.message.user {
  background: #007bff;
  color: white;
  align-self: flex-end;
}

.typing-indicator {
  padding: 8px;
  display: flex;
  gap: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #e0e0e0;
  border-radius: 50%;
  animation: typing 1s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

.message-time {
  font-size: 11px;
  color: #666;
  margin-top: 4px;
}

.chat-input {
  padding: 12px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 8px;
}

.chat-input input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.chat-input button {
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.chat-input button:hover {
  background: #0056b3;
}
</style>
