<template>
    <div class="header-row">
      <div class="spacer"></div>
      <div class="header-right">
        <input v-model="search" class="search" type="search" placeholder="search" />
      </div>
    </div>

    <section class="section">
      <h2 class="section-heading">Personalized Learning</h2>
      <div class="courses-grid">
        <article class="course-card" v-for="course in filteredCourses" :key="course.id" @click="openCourse(course)">
          <div class="thumb" aria-hidden="true"></div>
          <div class="meta">
            <div class="course-title">{{ course.title }}</div>
            <div class="course-desc">{{ course.description }}</div>
          </div>
        </article>
      </div>
    </section>

    <section class="section">
      <h2 class="section-heading">Recommendations</h2>
      <div class="recommendations-row">
        <div class="rec-card" v-for="rec in filteredRecs" :key="rec.id" @click="openCourse(rec)">
          <div class="rec-thumb" aria-hidden="true"></div>
        </div>
      </div>
    </section>

</template>

<script>
import UserLayout from './UserLayout.vue';

export default {
  name: 'UserLearning',
  components: { UserLayout },
  data() {
    return {
      search: '',
      courses: [
        { id: 1, title: 'Course A', description: 'Brief description of Course A' },
        { id: 2, title: 'Course B', description: 'Brief description of Course B' },
        { id: 3, title: 'Course C', description: 'Brief description of Course C' },
        { id: 4, title: 'Course D', description: 'Brief description of Course D' }
      ],
      recommendations: [
        { id: 'r1', title: 'Rec 1' },
        { id: 'r2', title: 'Rec 2' },
        { id: 'r3', title: 'Rec 3' },
        { id: 'r4', title: 'Rec 4' }
      ]
    };
  },
  computed: {
    filteredCourses() {
      const q = this.search.trim().toLowerCase();
      if (!q) return this.courses;
      return this.courses.filter(c => (c.title + ' ' + c.description).toLowerCase().includes(q));
    },
    filteredRecs() {
      const q = this.search.trim().toLowerCase();
      if (!q) return this.recommendations;
      return this.recommendations.filter(r => r.title.toLowerCase().includes(q));
    }
  },
  methods: {
    openCourse(item) {
      // placeholder — wire up to real course viewer later
      alert(`Open: ${item.title}`);
    },
    openChat() {
      // placeholder chat action
      alert('Open ChatBot');
    }
  }
};
</script>

<style scoped>
.header-row { display:flex; align-items:center; justify-content:space-between; margin-bottom:18px; }
.spacer { flex:1; }
.header-right .search {
  width: 360px;
  max-width: 45%;
  padding: 10px 14px;
  border-radius: 24px;
  border: 1px solid #ddd;
  background: #fff;
}

/* Sections */
.section { margin-bottom: 28px; }
.section-heading { font-size: 22px; margin: 6px 0 12px; font-weight:600; }

/* Courses grid */
.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 18px;
}
.course-card {
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow .12s ease, transform .08s ease;
}
.course-card:hover { box-shadow: 0 6px 18px rgba(0,0,0,0.06); transform: translateY(-4px); }
.thumb {
  width:100%;
  padding-top: 56%;
  background: linear-gradient(135deg,#f3f3f3,#ffffff);
  display:block;
}
.meta { padding: 10px 12px; }
.course-title { font-weight:600; margin-bottom:6px; }
.course-desc { color:#666; font-size:13px; }

/* Recommendations row */
.recommendations-row { display:flex; gap:18px; flex-wrap:wrap; align-items:center; }
.rec-card {
  width:120px;
  height:90px;
  background:#fff;
  border:1px solid #e6e6e6;
  border-radius:6px;
  display:flex;
  align-items:center;
  justify-content:center;
  cursor:pointer;
  transition:box-shadow .12s;
}
.rec-card:hover { box-shadow: 0 8px 18px rgba(0,0,0,0.06); }
.rec-thumb {
  width:88%;
  height:70%;
  background: linear-gradient(135deg,#eee,#fafafa);
  border-radius:4px;
}

/* ChatBot floating button */
.chatbot {
  position: fixed;
  right: 20px;
  bottom: 24px;
  background: #fff;
  border: 1px solid #d0d0d0;
  padding: 10px 14px;
  border-radius: 16px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.08);
  cursor: pointer;
}

/* Responsive */
@media (max-width: 720px) {
  .header-right .search { width: 100%; max-width: none; }
  .rec-card { width: 44%; }
}
</style>
