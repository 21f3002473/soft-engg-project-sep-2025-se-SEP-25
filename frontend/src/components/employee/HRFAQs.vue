<template>
  <div class="user-hr-faqs">
    <div class="header-row">
      <div class="spacer"></div>
      <div class="header-right">
      </div>
    </div>

    <section class="section">
      <h2 class="section-heading">HR FAQs</h2>
      <div class="faq-container">
        <div
          class="faq-item"
          v-for="(faq, i) in filteredFaqs"
          :key="i"
          @click="toggleFAQ(i)"
        >
          <div class="faq-question">
            <span>{{ faq.question }}</span>
            <span class="faq-icon">
              {{ activeIndex === i ? "−" : "+" }}
            </span>
          </div>
          <transition name="fade">
            <div v-if="activeIndex === i" class="faq-answer">
              {{ faq.answer }}
            </div>
          </transition>
        </div>
      </div>
    </section>

    <section class="section">
      <h2 class="section-heading">Need More Help?</h2>
      <div class="help-box">
        <p>
          Still can’t find what you’re looking for?  
          Reach out to our HR support team for assistance.
        </p>
        <button class="contact-btn" @click="contactHR">Contact HR</button>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'HRFAQs',
  data() {
    return {
      search: '',
      activeIndex: null,
      faqs: [
        {
          question: 'How do I apply for leave?',
          answer:
            'You can apply for leave from the Requests → Leave section in your dashboard.'
        },
        {
          question: 'How can I update my personal information?',
          answer:
            'You can edit your details in the Profile section under Settings.'
        },
        {
          question: 'When will I receive my reimbursement?',
          answer:
            'Reimbursements are typically processed within 7–10 business days after submission.'
        },
        {
          question: 'Who do I contact for payroll issues?',
          answer:
            'For payroll-related queries, contact hr.payroll@syncem.com.'
        },
        {
          question: 'When will I receive my reimbursement?',
          answer:
            'Reimbursements are typically processed within 7–10 business days after submission.'
        }
      ]
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
  methods: {
    toggleFAQ(index) {
      this.activeIndex = this.activeIndex === index ? null : index;
    },
    contactHR() {
      alert('Redirecting to HR contact page...');
    }
  }
};
</script>

<style scoped>
.user-hr-faqs {
  animation: fadeIn 0.4s ease-in;
}

.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 22px;
}
.spacer {
  flex: 1;
}
.header-right .search {
  width: 360px;
  max-width: 45%;
  padding: 10px 16px;
  border-radius: 24px;
  border: 1px solid #d2d8f3;
  background: #fff;
  transition: all 0.2s ease;
}
.header-right .search:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1);
}

.section {
  margin-bottom: 32px;
}
.section-heading {
  font-size: 22px;
  margin-bottom: 14px;
  font-weight: 600;
  color: #007bff;
}

.faq-container {
  background: #fff;
  border: 1px solid #e1e5f2;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.04);
}
.faq-item {
  border-bottom: 1px solid #f0f2fa;
  cursor: pointer;
  transition: 0.2s ease;
}
.faq-item:last-child {
  border-bottom: none;
}
.faq-item:hover {
  background: #f8faff;
}
.faq-question {
  display: flex;
  justify-content: space-between;
  padding: 14px 18px;
  font-weight: 500;
  color: #333;
}
.faq-icon {
  font-size: 20px;
  font-weight: bold;
  color: #007bff;
}
.faq-answer {
  padding: 0 18px 16px 18px;
  color: #555;
  font-size: 15px;
  line-height: 1.5;
}

.help-box {
  background: linear-gradient(145deg, #f0f6ff, #e7f0ff);
  border: 1px solid #d2e4ff;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 102, 255, 0.05);
}
.help-box p {
  font-size: 15px;
  color: #333;
  margin-bottom: 14px;
}
.contact-btn {
  background: #007bff;
  color: #fff;
  border: none;
  padding: 10px 20px;
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.3);
}
.contact-btn:hover {
  background: #0066d3;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.4);
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

@media (max-width: 720px) {
  .header-right .search {
    width: 100%;
    max-width: none;
  }
  .section-heading {
    font-size: 20px;
  }
}
</style>
