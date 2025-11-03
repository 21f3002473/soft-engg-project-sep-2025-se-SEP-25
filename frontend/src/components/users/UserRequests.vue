<template>
  <div class="user-requests">
    <!-- Header -->
    <div class="page-header">
      <h1 class="page-title">Requests</h1>
      <div class="header-right">
        <input
          v-model="search"
          placeholder="Search requests..."
          class="search"
          type="search"
        />
      </div>
    </div>

    <!-- Requests + Nested Form -->
    <section class="panel">
      <!-- Requests List -->
      <transition name="fade">
        <div v-if="filteredItems.length" class="requests-grid">
          <div
            class="request-card"
            v-for="item in filteredItems"
            :key="item.id"
            @click="openForm(item)"
          >
            <div class="request-info">
              <h2 class="request-title">{{ item.title }}</h2>
              <p class="request-desc">{{ item.description }}</p>
            </div>
            <router-link
              :to="`/user/requests/${item.title.toLowerCase()}`"
              class="form-btn"
              @click.stop
            >
              Open Form
            </router-link>
          </div>
        </div>
      </transition>


      <!-- Form Display Area -->
      <transition name="slide-fade">
        <div v-if="$route.params.id || $route.path.includes('requests/')" class="form-section">
          <router-view />
        </div>
      </transition>
    </section>
  </div>
</template>

<script>
export default {
  name: "UserRequests",
  data() {
    return {
      search: "",
      items: [
        {
          id: 1,
          title: "Leave",
          description: "Apply for leaves and view leave history.",
        },
        {
          id: 2,
          title: "Reimbursement",
          description: "Request expense reimbursements for official purposes.",
        },
        {
          id: 3,
          title: "Transfer",
          description: "Apply for department or location transfers.",
        },
      ],
    };
  },
  computed: {
    filteredItems() {
      const q = this.search.trim().toLowerCase();
      if (!q) return this.items;
      return this.items.filter((i) => i.title.toLowerCase().includes(q));
    },
  },
  methods: {
    openForm(item) {
      this.$router.push(`/user/requests/${item.title.toLowerCase()}`);
    },
  },
};
</script>

<style scoped>
.user-requests {
  padding: 24px 32px;
  color: #1e293b;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}
.page-title {
  font-size: 28px;
  font-weight: 800;
  color: #1d4ed8;
}
.search {
  width: 300px;
  padding: 10px 16px;
  border-radius: 24px;
  border: 1px solid #cbd5e1;
  background: #f8fafc;
  font-size: 15px;
  transition: all 0.25s ease;
}
.search:focus {
  outline: none;
  border-color: #2563eb;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
}

/* Panel */
.panel {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 24px;
  transition: all 0.3s ease;
}

/* Requests Grid */
.requests-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}
.request-card {
  background: #f9fafb;
  border-radius: 14px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: all 0.25s ease;
  cursor: pointer;
  border: 1px solid #e2e8f0;
}
.request-card:hover {
  transform: translateY(-5px);
  background: #ffffff;
  border-color: #2563eb;
  box-shadow: 0 8px 22px rgba(37, 99, 235, 0.12);
}
.request-info {
  margin-bottom: 12px;
}
.request-title {
  font-size: 18px;
  font-weight: 700;
  color: #1e3a8a;
  margin-bottom: 4px;
}
.request-desc {
  font-size: 14px;
  color: #64748b;
}
.form-btn {
  align-self: flex-start;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff;
  padding: 8px 16px;
  border-radius: 20px;
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.25s ease;
}
.form-btn:hover {
  background: linear-gradient(135deg, #1e40af, #1d4ed8);
  transform: translateY(-2px);
}

/* Form Section (below the list) */
.form-section {
  background: #eeeff1;
  border-radius: 12px;
  padding: 16px;
  box-shadow: inset 0 4px 8px rgba(37, 99, 235, 0.05);
}
.form-title {
  font-size: 22px;
  font-weight: 700;
  color: #1d4ed8;
  margin-bottom: 16px;
}
.form-content {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
}

/* Animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
.slide-fade-enter-active {
  transition: all 0.4s ease;
}
.slide-fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

/* Responsive */
@media (max-width: 768px) {
  .search {
    width: 100%;
  }
  .requests-grid {
    grid-template-columns: 1fr;
  }
}
</style>
