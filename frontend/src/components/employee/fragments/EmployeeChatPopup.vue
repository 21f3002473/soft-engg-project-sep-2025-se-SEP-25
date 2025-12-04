<template>
  <Transition name="slide">
    <div v-if="isOpen" class="chat-popup position-fixed d-flex flex-column bg-white shadow rounded-4 overflow-hidden">
      <div class="chat-header p-3 border-bottom d-flex justify-content-between align-items-center text-white">
        <div class="chat-header-info d-flex align-items-center gap-2">
          <div class="chat-avatar bg-white text-primary rounded-circle d-flex align-items-center justify-content-center fw-bold">🤖</div>
          <div>
            <h3 class="h6 mb-0 fw-bold">Sync’em AI Assistant</h3>
            <div class="small"><span class="status-dot d-inline-block rounded-circle bg-success me-1"></span>Online</div>
          </div>
        </div>
      </div>

      <div class="chat-messages flex-grow-1 overflow-auto p-3 d-flex flex-column gap-2 bg-light" ref="messagesContainer">
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          :class="['message p-2 px-3 rounded-4 position-relative', msg.sender]"
        >
          <div class="message-content text-break" v-html="renderMessage(msg.text)"></div>
          <div class="message-time small opacity-75 text-end mt-1">{{ formatTime(msg.time) }}</div>
        </div>

        <div v-if="isTyping" class="typing-indicator d-flex gap-1 p-2 align-self-start">
          <span></span><span></span><span></span>
        </div>
      </div>

      <div class="chat-input p-3 border-top d-flex gap-2 bg-white">
        <input
          type="text"
          class="form-control rounded-pill shadow-none"
          v-model="newMessage"
          @keyup.enter="sendMessage"
          placeholder="Ask me anything..."
        />
        <button @click="sendMessage" :disabled="!newMessage.trim()" class="btn rounded-circle d-flex align-items-center justify-content-center p-0 text-white border-0 shadow-sm">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
          </svg>
        </button>
      </div>
    </div>
  </Transition>
</template>

<script>
import { make_getrequest, make_postrequest } from "@/store/appState.js";
import MarkdownIt from "markdown-it";
import mk from "markdown-it-katex";
import DOMPurify from "dompurify";

export default {
  name: "EmployeeChatPopup",
  props: { isOpen: Boolean },
  data() {
    return {
      messages: [],
      newMessage: "",
      isTyping: false,
      md: new MarkdownIt({
        html: true,
        linkify: true,
        typographer: true
      }).use(mk)
    };
  },
  mounted() {
    this.fetchHistory();
  },
  watch: {
    isOpen(newVal) {
      if (newVal) {
        this.scrollToBottom();
        this.fetchHistory();
      }
    }
  },
  methods: {
    formatTime(date) {
      if (!date) return "";
      const d = new Date(date);
      return new Intl.DateTimeFormat("en", {
        hour: "2-digit",
        minute: "2-digit"
      }).format(d);
    },
    renderMessage(text) {
      if (!text) return "";
      const rawHtml = this.md.render(text);
      return DOMPurify.sanitize(rawHtml);
    },
    async fetchHistory() {
      try {
        const response = await make_getrequest('/api/employee/assistant/history');
        
        if (response && response.messages) {
          this.messages = response.messages.map(msg => ({
            text: msg.message,
            sender: msg.role === "assistant" ? "bot" : "user",
            time: msg.created_at
          }));
          
          if (this.messages.length === 0) {
            this.messages.push({
              text: "Hey there! I’m your Sync’em AI assistant. How can I help today?",
              sender: "bot",
              time: new Date()
            });
          }
        }
        this.scrollToBottom();
      } catch (error) {
        console.error("Failed to fetch chat history:", error);
      }
    },
    async sendMessage() {
      if (!this.newMessage.trim()) return;

      const userText = this.newMessage;
      this.newMessage = "";

      this.messages.push({
        text: userText,
        sender: "user",
        time: new Date()
      });
      this.scrollToBottom();

      this.isTyping = true;

      try {
        const response = await make_postrequest('/api/employee/assistant', { message: userText });

        this.isTyping = false;

        if (response && response.reply) {
          this.messages.push({
            text: "",
            sender: "bot",
            time: new Date()
          });
          
          const msgIndex = this.messages.length - 1;
          this.typeWriter(response.reply, msgIndex);
        }
      } catch (error) {
        this.isTyping = false;
        console.error("Failed to send message:", error);
        this.messages.push({
          text: "Sorry, I'm having trouble connecting right now. Please try again later.",
          sender: "bot",
          time: new Date()
        });
        this.scrollToBottom();
      }
    },
    typeWriter(text, index) {
      let i = 0;
      const speed = 15;

      const type = () => {
        if (i < text.length) {
          if (this.messages[index]) {
            this.messages[index].text += text.charAt(i);
            i++;
            this.scrollToBottom();
            setTimeout(type, speed);
          }
        }
      };
      
      type();
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const el = this.$refs.messagesContainer;
        if (el) {
          el.scrollTop = el.scrollHeight;
        }
      });
    }
  }
};
</script>

<style scoped>
.chat-popup {
  right: 28px;
  bottom: 100px;
  width: 380px;
  height: 540px;
  backdrop-filter: blur(16px);
  z-index: 1050;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.slide-enter-active, .slide-leave-active {
  transition: all 0.3s ease;
}
.slide-enter-from, .slide-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

.chat-header {
  background: linear-gradient(90deg, #007bff, #0056d2);
}

.chat-avatar {
  width: 36px;
  height: 36px;
}

.status-dot {
  width: 8px;
  height: 8px;
}

.chat-messages {
  background: #f8faff !important;
}

.message {
  max-width: 80%;
  word-break: break-word;
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

.chat-input input:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.15);
}

.chat-input button {
  background: linear-gradient(90deg, #007bff, #0056d2);
  width: 42px;
  height: 42px;
  transition: all 0.2s ease-in-out;
}

.chat-input button:hover {
  background: linear-gradient(90deg, #0069d9, #004ab3);
  transform: translateY(-2px);
}

.message-content :deep(p:last-child) {
  margin-bottom: 0;
}

.message-content :deep(pre) {
  background: rgba(0,0,0,0.1);
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>