<template>
    <div class="page-header">
      <div class="header-right">
        <input v-model="search" placeholder="Search" class="search" />
      </div>
    </div>

    <section class="panel">
      <div class="requests-list">
        <div class="request-row" v-for="item in filteredItems" :key="item.id">
          <div class="request-title">{{ item.title }}</div>
          <div class="request-action">
            <button class="form-btn" @click="openForm(item)">Form</button>
          </div>
        </div>
      </div>
    </section>
</template>

<script>
import UserLayout from './UserLayout.vue';

export default {
  name: 'UserRequests',
  components: { UserLayout },
  data() {
    return {
      search: '',
      items: [
        { id: 1, title: 'Leave' },
        { id: 2, title: 'Reimbursement' },
        { id: 3, title: 'Transfer' }
      ]
    };
  },
  computed: {
    filteredItems() {
      const q = this.search.trim().toLowerCase();
      if (!q) return this.items;
      return this.items.filter(i => i.title.toLowerCase().includes(q));
    }
  },
  methods: {
    openForm(item) {
      alert(`Open form: ${item.title}`);
    }
  }
};
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}
.page-header h1 {
  margin: 0;
  font-size: 32px;
  font-weight: 600;
}
.header-right .search {
  width: 260px;
  padding: 8px 12px;
  border-radius: 20px;
  border: 1px solid #ddd;
}
.panel {
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 18px;
  min-height: 260px;
  overflow: auto;
}
.requests-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.request-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
}
.request-title {
  font-size: 20px;
}
.form-btn {
  background: #fff;
  border: 1px solid #cfcfcf;
  padding: 8px 18px;
  border-radius: 8px;
  cursor: pointer;
}
.form-btn:hover {
  background: #f6f6f6;
}
</style>
