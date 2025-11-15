<template>
  <div class="chatbot-container d-flex flex-column h-100">
    <!-- Chat Messages Area -->
    <div class="chat-messages flex-grow-1 overflow-auto mb-3 p-2" ref="messageContainer">
      <div v-if="messages.length === 0" class="text-center text-muted py-4">
        <i class="bi bi-chat-quote fs-1"></i>
        <p class="mt-2">Start a conversation about {{ clientName || 'this client' }}</p>
      </div>
      
      <div 
        v-for="(message, index) in messages" 
        :key="index"
        :class="['message', message.sender === 'user' ? 'user-message' : 'ai-message']"
      >
        <div class="message-content">
          <div class="message-header d-flex align-items-center mb-1">
            <i :class="message.sender === 'user' ? 'bi bi-person-circle' : 'bi bi-robot'" class="me-2"></i>
            <strong>{{ message.sender === 'user' ? 'You' : 'AI Assistant' }}</strong>
            <small class="ms-auto text-muted">{{ message.timestamp }}</small>
          </div>
          <p class="mb-0">{{ message.text }}</p>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="chat-input">
      <form @submit.prevent="sendMessage" class="d-flex gap-2">
        <input
          v-model="userInput"
          type="text"
          class="form-control"
          placeholder="Ask about requirements, tasks, or client details..."
          :disabled="isSending"
        />
        <button 
          type="submit" 
          class="btn btn-primary"
          :disabled="!userInput.trim() || isSending"
        >
          <span v-if="isSending" class="spinner-border spinner-border-sm me-1"></span>
          <i v-else class="bi bi-send-fill"></i>
        </button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProductMangerChatbot',
  props: {
    clientId: {
      type: [String, Number],
      required: false
    },
    clientName: {
      type: String,
      default: 'Client'
    }
  },
  data() {
    return {
      messages: [],
      userInput: '',
      isSending: false
    };
  },
  methods: {
    async sendMessage() {
      if (!this.userInput.trim()) return;

      const userMessage = {
        sender: 'user',
        text: this.userInput,
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      };

      this.messages.push(userMessage);
      const query = this.userInput;
      this.userInput = '';
      this.isSending = true;

      // Scroll to bottom
      this.$nextTick(() => {
        this.scrollToBottom();
      });

      // Simulate AI response (replace with actual API call)
      setTimeout(() => {
        const aiMessage = {
          sender: 'ai',
          text: `I understand you're asking about "${query}" for ${this.clientName}. This is a simulated response. In production, this would connect to your AI backend.`,
          timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
        };
        this.messages.push(aiMessage);
        this.isSending = false;
        
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      }, 1000);
    },
    scrollToBottom() {
      const container = this.$refs.messageContainer;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    }
  },
  mounted() {
    // Welcome message
    this.messages.push({
      sender: 'ai',
      text: `Hello! I'm here to help you with ${this.clientName}'s requirements and project details. How can I assist you today?`,
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    });
  }
};
</script>

<style scoped>
.chatbot-container {
  min-height: 400px;
  max-height: 500px;
}

.chat-messages {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  display: flex;
  margin-bottom: 0.5rem;
}

.user-message {
  justify-content: flex-end;
}

.user-message .message-content {
  background-color: #0d6efd;
  color: white;
  border-radius: 12px 12px 0 12px;
  max-width: 70%;
  padding: 0.75rem;
}

.ai-message {
  justify-content: flex-start;
}

.ai-message .message-content {
  background-color: #f8f9fa;
  color: #212529;
  border: 1px solid #dee2e6;
  border-radius: 12px 12px 12px 0;
  max-width: 70%;
  padding: 0.75rem;
}

.message-header {
  font-size: 0.875rem;
}

.chat-input {
  border-top: 1px solid #dee2e6;
  padding-top: 0.75rem;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 10px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>