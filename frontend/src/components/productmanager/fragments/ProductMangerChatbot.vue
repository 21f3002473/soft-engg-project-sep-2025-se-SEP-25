<template>
    <div class="chatbot">
        <div class="chat-header">
            <h3>Demo Chatbot</h3>
            <small>Simple demo with dummy data</small>
        </div>

        <div ref="messagesContainer" class="messages">
            <div
                v-for="msg in messages"
                :key="msg.id"
                :class="['message', msg.sender === 'bot' ? 'bot' : 'user']"
            >
                <div class="bubble">
                    <div class="text">{{ msg.text }}</div>
                    <div class="meta">{{ msg.time }}</div>
                </div>
            </div>
        </div>

        <form class="composer" @submit.prevent="sendMessage">
            <input
                v-model="input"
                type="text"
                placeholder="Type a message and press Enter..."
                @keydown.enter.exact.prevent="sendMessage"
            />
            <button type="button" @click="sendMessage">Send</button>
        </form>
    </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

let idCounter = 1
const formatTime = () => new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

const messages = ref([
    { id: idCounter++, sender: 'bot', text: 'Hello! I am a demo chatbot. How can I help you today?', time: formatTime() },
    { id: idCounter++, sender: 'user', text: 'Show me some demo features.', time: formatTime() },
    { id: idCounter++, sender: 'bot', text: 'I can answer simple questions, echo text, or return canned replies.', time: formatTime() },
])

const input = ref('')
const messagesContainer = ref(null)

function scrollToBottom() {
    nextTick(() => {
        const el = messagesContainer.value
        if (el) el.scrollTop = el.scrollHeight
    })
}

const canned = [
    "I'm a demo bot — try asking about 'price', 'hours', or say 'hello'.",
    "Prices depend on the product. This is demo data.",
    "We are open 9am–5pm in this demo.",
    "Nice to meet you!",
    "I don't understand fully, but this is a sample reply."
]

function botReply(userText) {
    const text = (userText || '').toLowerCase()

    let reply = ''
    if (!userText || text.trim() === '') {
        reply = "You didn't type anything — try a question."
    } else if (text.includes('price') || text.includes('cost')) {
        reply = "Demo prices: Basic $10, Pro $30. (dummy values)"
    } else if (text.includes('hello') || text.includes('hi')) {
        reply = "Hello! How can I help in this demo?"
    } else if (text.includes('hours') || text.includes('open')) {
        reply = "Demo hours: Mon–Fri 9am–5pm."
    } else if (text.includes('features')) {
        reply = "This demo supports sending messages and getting canned replies."
    } else {
        reply = canned[Math.floor(Math.random() * canned.length)]
    }

    setTimeout(() => {
        messages.value.push({ id: idCounter++, sender: 'bot', text: reply, time: formatTime() })
        scrollToBottom()
    }, 700 + Math.random() * 600)
}

function sendMessage() {
    const text = input.value.trim()
    if (!text) return

    messages.value.push({ id: idCounter++, sender: 'user', text, time: formatTime() })
    input.value = ''
    scrollToBottom()

    botReply(text)
}

scrollToBottom()
</script>

<style scoped>
.chatbot {
    width: 100%;
    max-width: 480px;
    min-height: 400px;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    background: #fafafa;
    font-family: Arial, Helvetica, sans-serif;
}

.chat-header {
    padding: 12px 16px;
    border-bottom: 1px solid #eee;
    background: #fff;
}

.messages {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    background: linear-gradient(180deg,#fafafa,#fff);
}

.message {
    display: flex;
}

.message.user {
    justify-content: flex-end;
}

.message.bot {
    justify-content: flex-start;
}

.bubble {
    max-width: 78%;
    padding: 8px 10px;
    border-radius: 12px;
    box-shadow: 0 1px 0 rgba(0,0,0,0.04);
}

.message.user .bubble {
    background: #0b93f6;
    color: #fff;
    border-bottom-right-radius: 4px;
}

.message.bot .bubble {
    background: #f1f1f1;
    color: #222;
    border-bottom-left-radius: 4px;
}

.meta {
    font-size: 10px;
    opacity: 0.7;
    margin-top: 6px;
    text-align: right;
}

.composer {
    display: flex;
    gap: 8px;
    padding: 10px;
    border-top: 1px solid #eee;
    background: #fff;
}

.composer input {
    flex: 1;
    padding: 8px 10px;
    border: 1px solid #ddd;
    border-radius: 6px;
    outline: none;
}

.composer input:focus {
    border-color: #a6d1ff;
    box-shadow: 0 0 0 3px rgba(11,147,246,0.08);
}

.composer button {
    padding: 8px 12px;
    background: #0b93f6;
    color: #fff;
    border: none;
    border-radius: 6px;
    cursor: pointer;
}

.composer button:hover {
    opacity: 0.95;
}
</style>