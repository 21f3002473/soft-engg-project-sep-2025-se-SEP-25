<template>
  <div class="user-hr-faqs container-fluid p-0">
    <div class="d-flex justify-content-end mb-4">
      <div class="w-100" style="max-width: 360px;">
        <input
          type="text"
          class="form-control rounded-pill shadow-sm"
          placeholder="Search FAQs..."
          v-model="search"
          style="border-color: #d2d8f3;"
        />
      </div>
    </div>

    <section class="mb-5">
      <h2 class="h4 text-primary fw-semibold mb-3">HR FAQs</h2>
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <div v-else class="card border-0 shadow-sm rounded-3 overflow-hidden">
        <div class="list-group list-group-flush">
          <div
            class="list-group-item list-group-item-action p-0 border-bottom-0"
            v-for="(faq, i) in filteredFaqs"
            :key="i"
            @click="toggleFAQ(i)"
            style="cursor: pointer;"
          >
            <div class="d-flex justify-content-between align-items-center p-3 fw-medium text-dark bg-white hover-bg-light transition-bg">
              <span>{{ faq.question }}</span>
              <span class="fs-5 fw-bold text-primary">
                {{ activeIndex === i ? "−" : "+" }}
              </span>
            </div>
            <transition name="fade">
              <div v-if="activeIndex === i" class="px-3 pb-3 text-secondary" style="font-size: 0.95rem; line-height: 1.5;">
                {{ faq.answer }}
              </div>
            </transition>
            <div class="border-bottom" v-if="i < filteredFaqs.length - 1"></div>
          </div>
        </div>
      </div>
    </section>

    <section class="mb-5">
      <h2 class="h4 text-primary fw-semibold mb-3">Need More Help?</h2>
      <div class="help-box p-4 text-center rounded-3 shadow-sm">
        <p class="mb-3 text-dark">
          Still can’t find what you’re looking for?  
          Reach out to our HR support team for assistance.
        </p>
        <button class="btn btn-primary fw-medium px-4 py-2 shadow-sm" @click="contactHR">Contact HR</button>
      </div>
    </section>
  </div>
</template>

<script>
import { make_getrequest } from '@/store/appState.js';
import { useNotify } from "@/utils/useNotify.js";

export default {
  name: 'EmployeeHRFAQs',
  data() {
    return {
      search: '',
      activeIndex: null,
      faqs: [],
      loading: false
    };
  },
  computed: {
    filteredFaqs() {
      const q = this.search.trim().toLowerCase();
      if (!q) return this.faqs;
      return this.faqs.filter(
        f =>
          f.question.toLowerCase().includes(q) ||
          f.answer.toLowerCase().includes(q)
      );
    }
  },
  mounted() {
    this.fetchFAQs();
  },
  methods: {
    async fetchFAQs() {
      this.loading = true;
      try {
        const response = await make_getrequest('/api/employee/hr-faqs');
        this.faqs = response.faqs;
      } catch (err) {
        console.error('Failed to fetch FAQs:', err);
        useNotify().error('Failed to load FAQs. Please try again later.');
      } finally {
        this.loading = false;
      }
    },
    toggleFAQ(index) {
      this.activeIndex = this.activeIndex === index ? null : index;
    },
    contactHR() {
      useNotify().info('Redirecting to HR contact page...');
    }
  }
};
</script>

<style scoped>
.user-hr-faqs {
  animation: fadeIn 0.4s ease-in;
}

.help-box {
  background: linear-gradient(145deg, #f0f6ff, #e7f0ff);
  border: 1px solid #d2e4ff;
}

.hover-bg-light:hover {
  background-color: #f8faff !important;
}

.transition-bg {
  transition: background-color 0.2s ease;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>