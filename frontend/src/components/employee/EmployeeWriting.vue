<template>
  <div class="writing-container my-3">
    <div class="writing-header">
      <h2>Quick Notes</h2>
      <p class="subtitle">Jot down your thoughts, tasks, or reminders — all in one place.</p>
    </div>

    <div class="writing-area">
      <textarea
        v-model="text"
        placeholder="Start typing your notes here..."
        class="text-input"
      ></textarea>

      <div class="actions">
        <button @click="saveText" class="btn primary">Save</button>
        <button @click="clearText" class="btn secondary">Clear</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EmployeeWriting',
  data() {
    return {
      text: ''
    };
  },
  methods: {
    saveText() {
      console.log('Saving:', this.text);
      alert('Your note has been saved temporarily!');
    },
    clearText() {
      if (confirm('Clear your notes?')) this.text = '';
    }
  }
};
</script>

<style scoped>
.writing-container {
  background: #f9fbff;
  border-radius: 16px;
  padding: 30px;
  max-width: 800px;
  margin: 0 auto;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: 0.3s ease-in-out;
}

.writing-container:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.writing-header {
  margin-bottom: 20px;
  text-align: left;
}

.writing-header h2 {
  color: #0066cc;
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 4px;
}

.subtitle {
  font-size: 14px;
  color: #555;
}

.writing-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.text-input {
  flex: 1;
  padding: 16px;
  border: 1.5px solid #d0d7de;
  border-radius: 10px;
  resize: none;
  font-size: 16px;
  line-height: 1.6;
  transition: border 0.2s ease, box-shadow 0.2s ease;
  min-height: 240px;
  background: #fff;
}

.text-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.15);
}

.actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn {
  padding: 10px 18px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 15px;
  transition: all 0.2s ease-in-out;
}

.btn.primary {
  background: linear-gradient(90deg, #007bff, #0056d2);
  color: white;
  border: none;
}

.btn.primary:hover {
  background: linear-gradient(90deg, #0069d9, #004ab3);
  transform: translateY(-1px);
}

.btn.secondary {
  background: #f8f9fa;
  border: 1px solid #ccc;
  color: #333;
}

.btn.secondary:hover {
  background: #e9ecef;
}
</style>
