<template>
    <div class="header-row">
      <div class="spacer"></div>
      <div class="header-right">
        <input v-model="search" class="search" type="search" placeholder="Search" />
      </div>
    </div>

    <section class="section">
      <h2 class="section-heading">HR FAQs</h2>
      <div class="placeholder large" aria-hidden="true"></div>
    </section>

    <section class="section">
      <h2 class="section-heading">Help</h2>
      <div class="placeholder large" aria-hidden="true"></div>
    </section>
</template>

<script>
import UserLayout from './UserLayout.vue';

export default {
  name: 'UserHRFAQs',
  components: { UserLayout },
  data() {
    return {
      search: ''
    };
  }
};
</script>

<style scoped>
.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}
.spacer { flex: 1; }
.header-right .search {
  width: 360px;
  max-width: 45%;
  padding: 10px 14px;
  border-radius: 24px;
  border: 1px solid #ddd;
  background: #fff;
}

/* Sections */
.section {
  margin-bottom: 28px;
}
.section-heading {
  font-size: 24px;
  margin: 6px 0 12px;
  font-weight: 600;
}

/* Large placeholder boxes to match wireframe hero areas */
.placeholder {
  border: 1px solid #ddd;
  border-radius: 6px;
  background-color: #fff;
  position: relative;
  overflow: hidden;
}

/* make a visible "X" using layered gradients for the wireframe look */
.placeholder::before,
.placeholder::after {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  background-repeat: no-repeat;
  background-position: center;
  opacity: 0.08;
  pointer-events: none;
}
.placeholder::before {
  background-image: linear-gradient(135deg, transparent 44%, #000 44%, #000 56%, transparent 56%);
}
.placeholder::after {
  background-image: linear-gradient(225deg, transparent 44%, #000 44%, #000 56%, transparent 56%);
}

.placeholder.large {
  height: 180px;
  min-height: 140px;
}

/* responsive tweaks */
@media (max-width: 700px) {
  .header-right .search { width: 100%; max-width: none; }
  .placeholder.large { height: 140px; }
}
</style>
