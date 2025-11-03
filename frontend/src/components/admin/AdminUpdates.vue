<template>
  <div class="dashboard">
    <!-- <header class="dashboard-header">
      <div class="nav-links">
        <router-link to="/systemStatus">System Status</router-link>
        <router-link to="/logs">Logs</router-link>
        <router-link to="/updates" class="router-link-exact-active">Updates</router-link>
        <router-link to="/chatbotConfig">Chatbot Config</router-link>
      </div>
      <div class="account-link">
        <router-link to="/account">Account</router-link>
      </div>
    </header> -->

    <main class="dashboard-content">
      <h1>Updates</h1>
      <div class="content-placeholder">
        <p>Software update status, package versions, and a "Check for Updates" button would be displayed here.</p>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'AdminUpdates',
  data() {
    return {
    };
  }
};
</script>

<style scoped>
/* All styles are identical to ChatbotConfig.vue */
.dashboard {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background-color: #f4f7f6;
  height: 100vh;
  color: #333;
}
a { text-decoration: none; color: #555; font-size: 14px; }
a:hover { color: #000; }
.router-link-exact-active { color: #007bff; font-weight: bold; }
.dashboard-header { display: flex; justify-content: space-between; align-items: center; padding: 15px 30px; background-color: #ffffff; border-bottom: 1px solid #ddd; }
.nav-links a { margin-right: 25px; }
.account-link a { font-weight: bold; }
.dashboard-content { padding: 25px 30px; }
.dashboard-content h1 { margin: 0; font-size: 28px; font-weight: 600; margin-bottom: 20px; }
.content-placeholder { background-color: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 20px; min-height: 200px; }
</style>