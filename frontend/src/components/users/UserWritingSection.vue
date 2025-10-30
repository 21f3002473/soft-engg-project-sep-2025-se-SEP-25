<template>
    <div class="writing-container">
      <div class="writing-area">
        <textarea
          v-model="text"
          placeholder="Write your text here..."
          class="text-input"
        ></textarea>
        <div class="actions">
          <button @click="saveText" class="btn save">Save</button>
          <button @click="clearText" class="btn">Clear</button>
        </div>
      </div>
    </div>
</template>

<script>

export default {
  name: 'UserWritingSection',
  components: { },
  data() {
    return {
      text: '',
      isChatOpen: false
    }
  },
  methods: {
    saveText() {
      // Implement save functionality
      console.log('Saving:', this.text);
    },
    clearText() {
      if (confirm('Are you sure you want to clear the text?')) {
        this.text = '';
      }
    },
    toggleChat() {
      this.isChatOpen = !this.isChatOpen;
    }
  }
}
</script>

<style scoped>
.writing-container {
  position: relative;
  height: calc(100vh - 200px);
}

.writing-area {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.text-input {
  flex: 1;
  padding: 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: none;
  font-size: 16px;
  line-height: 1.5;
}

.actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  background: white;
}

.btn.save {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.chat-toggle {
  position: fixed;
  right: 20px;
  bottom: 20px;
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  z-index: 100;
}
</style>
