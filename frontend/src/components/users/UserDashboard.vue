<template>
  <div class="dashboard-page">
    <!-- Welcome Section -->
    <section class="welcome-section">
      <div class="welcome-card">
        <h2>Welcome back, <span class="highlight">User</span></h2>
        <p>Here’s what’s happening in your workspace today.</p>
      </div>
    </section>

    <!-- Quick Stats Section -->
    <section class="stats-section">
      <div class="stat-card" v-for="(item, index) in stats" :key="index">
        <div class="stat-icon" :class="item.colorClass">
          <i :class="item.icon"></i>
        </div>
        <div class="stat-info">
          <h3>{{ item.value }}</h3>
          <p>{{ item.label }}</p>
        </div>
      </div>
    </section>

    <!-- Tasks and Announcements -->
    <section class="content-section">
      <div class="tasks">
        <h3>Your Tasks</h3>
        <ul>
          <li v-for="(task, i) in tasks" :key="i">
            <input type="checkbox" v-model="task.completed" />
            <span :class="{ done: task.completed }">{{ task.title }}</span>
          </li>
        </ul>
      </div>

      <div class="announcements">
        <h3>Announcements</h3>
        <div class="announcement" v-for="(item, i) in announcements" :key="i">
          <h4>{{ item.title }}</h4>
          <p>{{ item.message }}</p>
          <small>{{ item.time }}</small>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'UserDashboard',
  data() {
    return {
      stats: [
        { label: 'Pending Tasks', value: 8, icon: 'fas fa-tasks', colorClass: 'blue' },
        { label: 'Completed', value: 12, icon: 'fas fa-check-circle', colorClass: 'green' },
        { label: 'Requests', value: 3, icon: 'fas fa-envelope-open-text', colorClass: 'purple' },
        { label: 'Courses Completed', value: 5, icon: 'fas fa-bell', colorClass: 'orange' }
      ],
      tasks: [
        { title: 'Submit monthly report', completed: false },
        { title: 'Review HR policy updates', completed: true },
        { title: 'Prepare project summary', completed: false }
      ],
      announcements: [
        { title: 'Cloud Course', message: 'Join and complete the new course on cloud.', time: '2 hours ago' },
        { title: 'Policy Update', message: 'Work-from-home requests must be submitted 2 days in advance.', time: '1 day ago' }
      ]
    };
  }
};
</script>

<style scoped>
.dashboard-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  font-family: "Inter", sans-serif;
  color: #1e293b;
}

/* Welcome Section */
.welcome-card {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.2);
  text-align: left;
  margin-bottom: 20px;
}

.welcome-card h2 {
  font-size: 26px;
  margin-bottom: 8px;
  font-weight: 700;
}

.welcome-card .highlight {
  color: #fffacd;
}

.welcome-card p {
  font-size: 15px;
  opacity: 0.9;
}

/* Stats Section */
.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: #fff;
  border-radius: 14px;
  display: flex;
  align-items: center;
  padding: 18px 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.2);
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  color: white;
  font-size: 20px;
  margin-right: 14px;
}

.stat-icon.blue {
  background: #3b82f6;
}

.stat-icon.green {
  background: #10b981;
}

.stat-icon.purple {
  background: #8b5cf6;
}

.stat-icon.orange {
  background: #f59e0b;
}

.stat-info h3 {
  font-size: 22px;
  margin: 0;
  color: #1e3a8a;
}

.stat-info p {
  margin: 2px 0 0;
  color: #475569;
  font-size: 14px;
}

/* Tasks & Announcements */
.content-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.tasks, .announcements {
  background: #fff;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.tasks h3, .announcements h3 {
  margin-bottom: 14px;
  font-weight: 600;
  color: #1e40af;
}

.tasks ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tasks li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  font-size: 15px;
}

.tasks li span.done {
  text-decoration: line-through;
  color: #94a3b8;
}

.announcement {
  margin-bottom: 16px;
  border-left: 4px solid #2563eb;
  padding-left: 12px;
}

.announcement h4 {
  margin: 0 0 4px;
  color: #1e3a8a;
}

.announcement p {
  margin: 0 0 4px;
  color: #475569;
  font-size: 14px;
}

.announcement small {
  color: #94a3b8;
  font-size: 13px;
}

/* Responsiveness */
@media (max-width: 900px) {
  .content-section {
    grid-template-columns: 1fr;
  }
}
</style>
