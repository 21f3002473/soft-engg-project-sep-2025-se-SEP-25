<template>
  <div class="container py-4">
    <section class="mb-5">
      <h2 class="h2 fw-bold text-primary mb-4">Personalized Learning</h2>
      
      <div v-if="loading" class="text-muted fs-5">Loading courses...</div>
      <div v-else-if="filteredCourses.length === 0" class="text-muted fs-5">No enrolled courses yet.</div>
      
      <div v-else class="row g-4">
        <div class="col-md-6 col-lg-4 col-xl-3" v-for="course in filteredCourses" :key="course.course_id">
          <article class="card h-100 border-0 shadow-sm rounded-4 hover-card" @click="openCourse(course)">
            <div class="course-thumb rounded-top-4"></div>
            <div class="card-body p-4 d-flex flex-column">
              <h3 class="h5 fw-bold text-dark mb-2">{{ course.course_name }}</h3>
              <p class="card-text text-secondary small mb-3 flex-grow-1">{{ course.topics }}</p>
              <div class="d-flex justify-content-between align-items-center mt-auto">
                <span class="badge bg-light text-dark border">{{ course.status }}</span>
                <button class="btn btn-primary rounded-pill px-4 btn-sm fw-semibold">Continue</button>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>

    <section class="mb-4">
      <h2 class="h2 fw-bold text-primary mb-4">Recommended for You</h2>
      
      <div v-if="loading" class="text-muted fs-5">Loading recommendations...</div>
      <div v-else-if="filteredRecs.length === 0" class="text-muted fs-5">No recommendations available.</div>
      
      <div v-else class="row g-4">
        <div class="col-md-4 col-lg-3 col-6" v-for="rec in filteredRecs" :key="rec.course_id">
          <div class="card h-100 border-0 shadow-sm rounded-4 hover-card rec-card-bg" @click="openCourse(rec)">
            <div class="rec-top rounded-top-4 d-flex align-items-center justify-content-center">
              <i class="bi bi-lightbulb-fill text-white fs-4"></i>
            </div>
            <div class="card-body text-center p-3">
              <h3 class="h6 fw-bold text-primary mb-1">{{ rec.course_name }}</h3>
              <p class="small text-secondary mb-0">{{ rec.topics || 'Tap to explore' }}</p>
            </div>
            <div class="card-footer bg-transparent border-top-0 text-center pb-3 pt-0">
              <span class="text-primary small fw-bold rec-action">Learn More <i class="bi bi-arrow-right ms-1"></i></span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { make_getrequest } from "@/store/appState.js";

export default {
  name: 'EmployeeLearning',
  data() {
    return {
      courses: [],
      recommendations: [],
      loading: false
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
  mounted() {
    this.fetchLearningData();
  },
  methods: {
    async fetchLearningData() {
      this.loading = true;
      try {
        const coursesData = await make_getrequest('/api/employee/courses');
        if (Array.isArray(coursesData)) {
          this.courses = coursesData.map(c => ({
            course_id: c.course_id,
            course_name: c.course_name,
            status: c.status,
            topics: c.topics,
            course_link: c.course_link
          }));
        }

        const recsData = await make_getrequest('/api/employee/recommendations');
        if (recsData.recommended_courses) {
          this.recommendations = recsData.recommended_courses.map(r => ({
            course_id: r.id,
            course_name: r.course_name,
            topics: r.topics,
            course_link: r.course_link
          }));
        }
      } catch (error) {
        console.error("Failed to fetch learning data:", error);
      } finally {
        this.loading = false;
      }
    },
    openCourse(item) {
      if (item.course_link) {
        window.open(item.course_link, '_blank');
      } else {
        alert(`Course: ${item.course_name} (No link available)`);
      }
    }
  }
};
</script>

<style scoped>
.hover-card {
  cursor: pointer;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.hover-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(37, 99, 235, 0.15) !important;
}

.course-thumb {
  width: 100%;
  padding-top: 56%;
  background: linear-gradient(135deg, #bfdbfe, #eff6ff);
}

.rec-card-bg {
  background: linear-gradient(135deg, #dbeafe, #eff6ff);
  backdrop-filter: blur(10px);
}

.rec-top {
  height: 60px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.rec-action {
  transition: color 0.3s ease;
}

.hover-card:hover .rec-action {
  color: #1e3a8a !important;
}
</style>
