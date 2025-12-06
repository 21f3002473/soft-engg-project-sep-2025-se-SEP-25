<template>
  <transition name="slide-fade">
    <div class="card border-0 shadow-sm p-4 mx-auto mt-4" style="max-width: 700px; background-color: #f9fbff;">
      <h2 class="h3 text-primary fw-bold text-center mb-4">{{ isViewMode ? 'Leave Details' : 'Leave Application' }}</h2>
      <form @submit.prevent="submitForm">
        <div class="mb-3">
          <label class="form-label fw-bold">Leave Type</label>
          <select v-model="form.type" class="form-select" required>
            <option value="">Select type</option>
            <option value="casual">Casual Leave</option>
            <option value="sick">Sick Leave</option>
            <option value="earned">Earned Leave</option>
          </select>
        </div>

        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <label class="form-label fw-bold">From</label>
            <input v-model="form.from" type="date" class="form-control" required />
          </div>
          <div class="col-md-6">
            <label class="form-label fw-bold">To</label>
            <input v-model="form.to" type="date" class="form-control" required />
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label fw-bold">Reason</label>
          <textarea v-model="form.reason" rows="3" class="form-control" placeholder="State your reason..."
            required></textarea>
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
  name: 'EmployeeLeaveForm',
  data() {
    return {
      form: { type: '', from: '', to: '', reason: '' },
      isViewMode: false
    };
  },
  mounted() {
    if (history.state && history.state.requestData) {
      const data = history.state.requestData.raw;
      if (data) {
        this.isViewMode = true;
        this.form.type = data.leave_type ? data.leave_type.toLowerCase() : '';
        this.form.from = data.from_date ? data.from_date.split('T')[0] : '';
        this.form.to = data.to_date ? data.to_date.split('T')[0] : '';
        this.form.reason = data.reason || '';
      }
    }
  },
  methods: {
    async submitForm() {
      if (this.isViewMode) return;

      try {
        const payload = {
          leave_type: this.form.type,
          from_date: this.form.from,
          to_date: this.form.to,
          reason: this.form.reason
        };

        await make_postrequest('/api/employee/requests/leave', payload);
        useNotify().success('Leave request submitted successfully!');
        this.$router.push('/employee/requests');
      } catch (error) {
        console.error("Failed to submit leave request:", error);
        useNotify().error('Failed to submit leave request. Please try again.');
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