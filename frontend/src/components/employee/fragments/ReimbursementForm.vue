<template>
  <transition name="slide-fade">
    <div class="form-shell">
      <h2>Reimbursement Request</h2>
      <form @submit.prevent="submitForm">
        <div class="form-group">
          <label>Employee Name</label>
          <input
            v-model="form.name"
            type="text"
            placeholder="Enter your name"
            required
          />
        </div>

        <div class="form-group">
          <label>Expense Type</label>
          <select v-model="form.expenseType" required>
            <option value="">Select expense type</option>
            <option value="travel">Travel</option>
            <option value="food">Food</option>
            <option value="stationery">Stationery</option>
            <option value="other">Other</option>
          </select>
        </div>

        <div class="form-row">
          <div class="form-group half">
            <label>Amount (₹)</label>
            <input
              v-model="form.amount"
              type="number"
              min="0"
              placeholder="Enter amount"
              required
            />
          </div>
          <div class="form-group half">
            <label>Date of Expense</label>
            <input v-model="form.date" type="date" required />
          </div>
        </div>

        <div class="form-group">
          <label>Remarks</label>
          <textarea
            v-model="form.remarks"
            rows="3"
            placeholder="Add any remarks..."
          ></textarea>
        </div>

        <div class="btn-wrap">
          <button class="submit-btn" type="submit">Submit Request</button>
        </div>
      </form>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'ReimbursementForm',
  data() {
    return {
      form: { name: '', expenseType: '', amount: '', date: '', remarks: '' }
    };
  },
  methods: {
    submitForm() {
      alert(`Reimbursement submitted for ₹${this.form.amount || 0}`);
    }
  }
};
</script>

<style scoped>
.form-shell {
  background: #f9fbff;
  border: 1px solid #d9e6ff;
  border-radius: 12px;
  padding: 24px;
  max-width: 700px;
  margin: 30px auto 10px;
  box-shadow: 0 4px 14px rgba(0, 102, 255, 0.08);
  transition: all 0.3s ease;
}

h2 {
  font-size: 1.6rem;
  font-weight: 600;
  color: #007bff;
  text-align: center;
  margin-bottom: 24px;
  letter-spacing: 0.5px;
}

.form-group {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 500;
  margin-bottom: 6px;
  color: #333;
}

.form-row {
  display: flex;
  gap: 16px;
}

.half {
  flex: 1;
}

input,
select,
textarea {
  padding: 10px 12px;
  border: 1px solid #cfdaf7;
  border-radius: 8px;
  outline: none;
  font-size: 15px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

input:focus,
select:focus,
textarea:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1);
}

textarea {
  resize: none;
}

.btn-wrap {
  display: flex;
  justify-content: flex-end;
}

.submit-btn {
  background: #007bff;
  color: #fff;
  border: none;
  padding: 10px 20px;
  font-size: 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.3);
}

.submit-btn:hover {
  background: #0066d3;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.4);
}

.slide-fade-enter-active {
  transition: all 0.4s ease;
}
.slide-fade-leave-active {
  transition: all 0.3s ease;
  opacity: 0;
  transform: translateY(-10px);
}
.slide-fade-enter-from {
  opacity: 0;
  transform: translateY(-15px);
}
.slide-fade-enter-to {
  opacity: 1;
  transform: translateY(0);
}
</style>