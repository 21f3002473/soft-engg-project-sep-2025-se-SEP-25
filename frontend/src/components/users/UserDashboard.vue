<template>
  <div class="page-shell">
      <div class="dashboard">
        <p>Welcome to the employee dashboard. Here you can manage your tasks, view reports, and configure settings.</p>
      </div>
  </div>
</template>

<script>
export default {
  name: 'UserDashboard',
  data() {
    return {
    };
  },
  methods: {
  },
  mounted() {
  }
};
</script>

<style scoped>
.content {
  max-width: 1100px;
  margin: 20px auto;
  padding: 12px;
}
.dashboard p {
  color: #555;
}
</style>