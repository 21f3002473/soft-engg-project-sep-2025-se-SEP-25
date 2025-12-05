<template>
  <div id="app">
    <ToastContainer />
    <router-view/>
  </div>
</template>

<script>
import { ToastContainer } from "vue3-toastify";
import "vue3-toastify/dist/index.css";

export default {
  name: 'App',
  components: {
    ToastContainer
  }
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
</style>