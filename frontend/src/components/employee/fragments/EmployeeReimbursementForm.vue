<template>
  <transition name="slide-fade">
    <div class="card border-0 shadow-sm p-4 mx-auto mt-4" style="max-width: 700px; background-color: #f9fbff;">
      <h2 class="h3 text-primary fw-bold text-center mb-4">{{ isViewMode ? 'Reimbursement Details' : 'Reimbursement Request' }}</h2>
      <form @submit.prevent="submitForm">
        <div class="mb-3">
          <label class="form-label fw-bold">Expense Type</label>
          <select v-model="form.expenseType" class="form-select" required>
            <option value="">Select expense type</option>
            <option value="travel">Travel</option>
            <option value="food">Food</option>
            <option value="stationery">Stationery</option>
            <option value="other">Other</option>
          </select>
        </div>

        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <label class="form-label fw-bold">Amount (₹)</label>
            <input v-model="form.amount" type="number" min="0" class="form-control" placeholder="Enter amount"
              required />
          </div>
          <div class="col-md-6">
            <label class="form-label fw-bold">Date of Expense</label>
            <input v-model="form.date" type="date" class="form-control" required />
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label fw-bold">Remarks</label>
          <textarea v-model="form.remarks" rows="3" class="form-control" placeholder="Add any remarks..."></textarea>
        </div>

        <div class="d-flex justify-content-end">
          <button class="btn btn-primary px-4" type="submit">Submit Request</button>
        </div>
      </form>
    </div>
  </transition>
</template>

<script>
import { make_postrequest } from "@/store/appState.js";
import { useNotify } from "@/utils/useNotify.js";

export default {
  name: 'EmployeeReimbursementForm',
  data() {
    return {
      form: { expenseType: '', amount: '', date: '', remarks: '' },
      isViewMode: false
    };
  },
  mounted() {
    if (history.state && history.state.requestData) {
      const data = history.state.requestData.raw;
      if (data) {
        this.isViewMode = true;
        this.form.expenseType = data.expense_type ? data.expense_type.toLowerCase() : '';
        this.form.amount = data.amount;
        this.form.date = data.date_expense ? data.date_expense.split('T')[0] : '';
        this.form.remarks = data.remark || '';
      }
    }
  },
  methods: {
    async submitForm() {
      if (this.isViewMode) return;

      try {
        const payload = {
          expense_type: this.form.expenseType,
          amount: parseFloat(this.form.amount),
          date_expense: this.form.date,
          remark: this.form.remarks
        };

        await make_postrequest('/api/employee/requests/reimbursement', payload);
        useNotify().success('Reimbursement request submitted successfully!');
        this.$router.push('/employee/requests');
      } catch (error) {
        console.error("Failed to submit reimbursement request:", error);
        useNotify().error('Failed to submit reimbursement request. Please try again.');
      }
    }
  }
};
</script>

<style scoped>
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