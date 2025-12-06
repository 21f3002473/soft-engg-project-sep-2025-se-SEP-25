<template>
  <div class="user-learning">
    <section class="section ">
      <h2 class="section-heading">Personalized Learning</h2>
      <div class="courses-grid">
        <article
          class="course-card"
          v-for="course in filteredCourses"
          :key="course.id"
          @click="openCourse(course)"
        >
          <div class="thumb"></div>
          <div class="meta">
            <h3 class="course-title">{{ course.title }}</h3>
            <p class="course-desc">{{ course.description }}</p>
            <button class="start-btn">Start Learning</button>
          </div>
        </article>
      </div>
    </section>

    <section class="section mt-2">
      <h2 class="section-heading">Recommended for You</h2>
      <div class="recommendations-grid">
        <div
          class="rec-card"
          v-for="rec in filteredRecs"
          :key="rec.id"
          @click="openCourse(rec)"
        >
          <div class="rec-top">
            <i class="fas fa-lightbulb rec-icon"></i>
          </div>
          <div class="rec-body">
            <h3 class="rec-title">{{ rec.title }}</h3>
            <p class="rec-sub">Tap to explore</p>
          </div>
          <div class="rec-footer">
            <span class="rec-action">Learn More →</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'EmployeeLearning',
  data() {
    return {
      courses: [
        { id: 1, title: 'Intro to AI', description: 'Get started with the basics of Artificial Intelligence.' },
        { id: 2, title: 'Web Development', description: 'Build modern, responsive web apps from scratch.' },
        { id: 3, title: 'Data Visualization', description: 'Learn to tell stories with interactive dashboards.' },
        { id: 4, title: 'Machine Learning', description: 'Understand models, training, and real-world ML use cases.' }
      ],
      recommendations: [
        { id: 'r1', title: 'Deep Learning Basics' },
        { id: 'r2', title: 'Frontend Mastery' },
        { id: 'r3', title: 'Database Essentials' },
        { id: 'r4', title: 'Python for Data Science' }
      ]
    };
  },
  computed: {
    filteredCourses() {
      return this.courses;
    },
    filteredRecs() {
      return this.recommendations;
    }
  },
  methods: {
    openCourse(item) {
      alert(`Open: ${item.title}`);
    }
  }
};
</script>

<style scoped>
.user-learning {
  padding: 20px 32px;
  color: #1e293b;
  background: #ffffff;
  min-height: 100vh;
}

.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}
.page-title {
  font-size: 28px;
  font-weight: 800;
  color: #1e3a8a;
  letter-spacing: 0.3px;
}

.section {
  margin-bottom: 40px;
}
.section-heading {
  font-size: 30px;
  font-weight: 700;
  color: #1d4ed8;
  margin-bottom: 20px;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}
.course-card {
  background: #ffffff;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  transition: all 0.25s ease;
}
.course-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.15);
}
.thumb {
  width: 100%;
  padding-top: 56%;
  background: linear-gradient(135deg, #bfdbfe, #eff6ff);
}
.meta {
  padding: 16px;
}
.course-title {
  font-size: 17px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}
.course-desc {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 12px;
}
.start-btn {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff;
  border: none;
  border-radius: 24px;
  padding: 8px 18px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}
.start-btn:hover {
  background: linear-gradient(135deg, #1d4ed8, #1e40af);
  transform: translateY(-2px);
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 24px;
}

.rec-card {
  position: relative;
  height: 180px;
  border-radius: 18px;
  background: linear-gradient(135deg, #dbeafe, #eff6ff);
  backdrop-filter: blur(10px);
  box-shadow: 0 6px 14px rgba(37, 99, 235, 0.08);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.35s ease;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.rec-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 10px 25px rgba(37, 99, 235, 0.2);
}

.rec-top {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 60px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}
.rec-icon {
  color: #fff;
  font-size: 24px;
}

.rec-body {
  text-align: center;
  padding: 10px 12px;
}
.rec-title {
  font-size: 16px;
  font-weight: 700;
  color: #1e3a8a;
  margin-bottom: 6px;
}
.rec-sub {
  font-size: 13px;
  color: #475569;
}

.rec-footer {
  text-align: center;
  background: rgba(37, 99, 235, 0.05);
  padding: 8px 0;
  font-weight: 600;
  font-size: 13px;
  color: #2563eb;
  border-top: 1px solid #dbeafe;
  transition: all 0.3s ease;
}
.rec-card:hover .rec-footer {
  background: rgba(37, 99, 235, 0.1);
  color: #1e3a8a;
}

@media (max-width: 768px) {
  .header-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 14px;
  }
  .recommendations-grid {
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  }
}
</style>
