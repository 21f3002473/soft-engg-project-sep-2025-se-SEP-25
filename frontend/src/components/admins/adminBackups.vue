<template>
  <div class="backup-list">
    <h1>{{ title }}</h1>
    <div v-for="backup in backups" :key="backup.id" class="backup-item">
      <h3>{{ backup.name }}</h3>
      <p>Date: {{ backup.date }}</p>
    </div>
  </div>
</template>

<script>

export default defineComponent({
    setup() {
        const title = 'Admin Backups';
        const backups = [
            { id: 1, name: 'Backup 1', date: '2023-09-01' },
            { id: 2, name: 'Backup 2', date: '2023-09-02' },
            { id: 3, name: 'Backup 3', date: '2023-09-03' },
        ];

        return {
            title,
            backups
        };
    },
})
</script>
<style scoped>
.backup-list {
    margin: 20px;
}
.backup-item {
    padding: 10px;
    border: 1px solid #ccc;
    margin-bottom: 10px;
    border-radius: 5px;
}
</style>
