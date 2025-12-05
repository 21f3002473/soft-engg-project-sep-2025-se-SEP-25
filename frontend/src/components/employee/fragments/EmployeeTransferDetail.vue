<template>
  <transition name="slide-fade">
    <div class="card border-0 shadow-sm p-4 mx-auto mt-4" style="max-width: 700px;">
      <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-3">
        <h2 class="h3 fw-bold text-dark mb-0">Transfer Details</h2>
        <span class="badge rounded-pill text-capitalize" :class="getStatusClass(status)">{{ status }}</span>
      </div>

      <div class="d-flex flex-column gap-4">
        <div class="row">
          <div class="col-md-6">
            <label class="text-uppercase text-muted fw-bold small mb-2">Request ID</label>
            <div class="fw-medium text-dark">#{{ requestId }}</div>
          </div>
          <div class="col-md-6">
            <label class="text-uppercase text-muted fw-bold small mb-2">Status</label>
            <div class="fw-medium text-dark">{{ status }}</div>
          </div>
        </div>

        <div class="row">
          <div class="col-md-6">
            <label class="text-uppercase text-muted fw-bold small mb-2">Current Department</label>
            <div class="fw-medium text-dark">{{ currentDept }}</div>
          </div>
          <div class="col-md-6">
            <label class="text-uppercase text-muted fw-bold small mb-2">Requested Department</label>
            <div class="fw-bold text-primary">{{ requestedDept }}</div>
          </div>
        </div>

        <div>
          <label class="text-uppercase text-muted fw-bold small mb-2">Reason for Transfer</label>
          <div class="bg-light p-3 rounded border">{{ reason || 'No reason provided' }}</div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'EmployeeTransferDetail',
  data() {
    return {
      requestId: '',
      currentDept: '',
      requestedDept: '',
      reason: '',
      status: ''
    };
  },
  mounted() {
    if (history.state && history.state.requestData) {
      const data = history.state.requestData;
      const raw = data.raw;

      this.requestId = data.uniqueKey.split('-')[1];
      this.currentDept = raw.current_department;
      this.requestedDept = raw.request_department;
      this.reason = raw.reason;
      this.status = data.status;
    }
  },
  methods: {
    getStatusClass(status) {
      switch (status.toLowerCase()) {
        case 'pending': return 'bg-warning-subtle text-warning';
        case 'completed': return 'bg-success-subtle text-success';
        case 'rejected': return 'bg-danger-subtle text-danger';
        default: return 'bg-secondary';
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
