<template>
  <div class="user-shell d-flex flex-column min-vh-100">
    <HRNavBar />

    <main class="container-xl flex-grow-1 my-4 px-3" style="max-width: 1200px;">
      <transition name="fade-slide" mode="out-in">
        <div v-if="$route.meta.title" key="title" class="mb-4 text-start">
          <h1 class="fw-bold mb-2" style="color: #1e3a8a; font-size: 28px;">{{ $route.meta.title }}</h1>
          <div class="bg-primary rounded-pill" style="height: 3px; width: 50px;"></div>
        </div>
      </transition>

      <section class="page-body shadow p-4 rounded-4 bg-white bg-opacity-75"
        style="backdrop-filter: blur(5px); min-height: 250px;">
        <router-view />
      </section>
    </main>
  </div>
</template>

<script>
import HRNavBar from './fragments/HRNavBar.vue';

export default {
  name: "HRLayout",
  components: { HRNavBar }
}
</script>

<style scoped>
.user-shell {
  background: linear-gradient(135deg, #e9f1ff 0%, #f9fbff 100%);
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>