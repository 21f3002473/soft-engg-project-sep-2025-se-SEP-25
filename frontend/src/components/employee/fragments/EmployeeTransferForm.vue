<template>
  <transition name="slide-fade">
    <div class="card border-0 shadow-sm p-4 mx-auto mt-4" style="max-width: 700px; background-color: #f9fbff;">
      <h2 class="h3 text-primary fw-bold text-center mb-4">{{ isViewMode ? 'Transfer Details' : 'Transfer Request' }}</h2>
      <form @submit.prevent="submitForm">
        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <label class="form-label fw-bold">Current Department</label>
            <input
              v-model="form.currentDept"
              type="text"
              class="form-control"
              placeholder="e.g., HR, Finance"
              required
            />
          </div>
          <div class="col-md-6">
            <label class="form-label fw-bold">Requested Department</label>
            <input
              v-model="form.requestedDept"
              type="text"
              class="form-control"
              placeholder="e.g., Marketing, R&D"
              required
            />
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label fw-bold">Reason for Transfer</label>
          <textarea
            v-model="form.reason"
            rows="3"
            class="form-control"
            placeholder="Briefly explain the reason..."
            required
          ></textarea>
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
  name: 'EmployeeTransferForm',
  data() {
    return {
      form: {
        currentDept: '',
        requestedDept: '',
        reason: ''
      },
      isViewMode: false
    };
  },
  mounted() {
    if (history.state && history.state.requestData) {
      const data = history.state.requestData.raw;
      if (data) {
        this.isViewMode = true;
        this.form.currentDept = data.current_department || '';
        this.form.requestedDept = data.request_department || '';
        this.form.reason = data.reason || '';
      }
    }
  },
  methods: {
    async submitForm() {
      if (this.isViewMode) return;

      try {
        const payload = {
          current_department: this.form.currentDept,
          request_department: this.form.requestedDept,
          reason: this.form.reason
        };

        await make_postrequest('/api/employee/requests/transfer', payload);
        useNotify().success('Transfer request submitted successfully!');
        this.$router.push('/employee/requests');
      } catch (error) {
        console.error("Failed to submit transfer request:", error);
        useNotify().error('Failed to submit transfer request. Please try again.');
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
