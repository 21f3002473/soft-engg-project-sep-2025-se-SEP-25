<template>
  <transition name="slide-fade">
    <div class="card border-0 shadow-sm p-4 mx-auto mt-4" style="max-width: 700px;">
      <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-3">
        <h2 class="h3 fw-bold text-dark mb-0">Leave Details</h2>
        <span class="badge rounded-pill text-capitalize" :class="getStatusClass(status)">{{ status }}</span>
      </div>
      
      <div class="d-flex flex-column gap-4">
        <div class="row">
          <div class="col-md-6">
            <label class="text-uppercase text-muted fw-bold small mb-2">Leave Type</label>
            <div class="fw-medium text-dark">{{ leaveType }}</div>
          </div>
          <div class="col-md-6">
            <label class="text-uppercase text-muted fw-bold small mb-2">Request ID</label>
            <div class="fw-medium text-dark">#{{ requestId }}</div>
          </div>
        </div>

        <div class="row">
          <div class="col-md-6">
            <label class="text-uppercase text-muted fw-bold small mb-2">From Date</label>
            <div class="fw-medium text-dark">{{ formatDate(fromDate) }}</div>
          </div>
          <div class="col-md-6">
            <label class="text-uppercase text-muted fw-bold small mb-2">To Date</label>
            <div class="fw-medium text-dark">{{ formatDate(toDate) }}</div>
          </div>
        </div>

        <div>
          <label class="text-uppercase text-muted fw-bold small mb-2">Reason</label>
          <div class="bg-light p-3 rounded border">{{ reason || 'No reason provided' }}</div>
        </div>

        <div>
          <label class="text-uppercase text-muted fw-bold small mb-2">Applied On</label>
          <div class="fw-medium text-dark">{{ formatDate(createdDate) }}</div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'EmployeeLeaveDetail',
  data() {
    return {
      requestId: '',
      leaveType: '',
      fromDate: '',
      toDate: '',
      reason: '',
      status: '',
      createdDate: ''
    };
  },
  mounted() {
    if (history.state && history.state.requestData) {
      const data = history.state.requestData;
      const raw = data.raw;
      
      this.requestId = data.uniqueKey.split('-')[1];
      this.leaveType = raw.leave_type;
      this.fromDate = raw.from_date;
      this.toDate = raw.to_date;
      this.reason = raw.reason;
      this.status = data.status;
      this.createdDate = data.date;
    }
  },
  methods: {
    formatDate(dateStr) {
      if (!dateStr) return '-';
      return new Date(dateStr).toLocaleDateString(undefined, {
        year: 'numeric', month: 'long', day: 'numeric'
      });
    },
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
