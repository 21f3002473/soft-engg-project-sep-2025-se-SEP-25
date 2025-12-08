<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;

  font-family: "Raleway", sans-serif;
  font-optical-sizing: auto;
  font-style: normal;
}

.Toastify__toast {
  border-radius: 12px !important;
  padding: 8px !important;
  font-size: 1rem !important;
  font-weight: 600 !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15) !important;
}

.Toastify__toast--success {
  background: #2ecc71 !important;
  color: white !important;
}

.Toastify__toast--error {
  background: #e74c3c !important;
  color: white !important;
}

.Toastify__toast--info {
  background: #3498db !important;
  color: white !important;
}

.Toastify__progress-bar {
  height: 4px !important;
  border-radius: 2px !important;
}
</style>