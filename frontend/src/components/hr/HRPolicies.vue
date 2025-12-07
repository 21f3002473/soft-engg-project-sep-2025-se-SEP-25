<template>
  <div class="policies-content container-fluid p-4">
    <div class="row g-4 h-100">
      <div class="col-12 col-xl-7">
        <div class="card border-0 shadow-sm rounded-4 h-100 overflow-hidden bg-white">
          <div class="card-header bg-white border-bottom p-3 d-flex align-items-center gap-2">
            <span class="fs-5">📄</span>
            <h5 class="mb-0 fw-bold text-dark">Company Policy Document</h5>
          </div>
          <div class="card-body p-0 position-relative" style="height: 85vh; min-height: 600px;">
            <iframe src="/docs/Human Resources Policy.pdf" frameborder="0" class="w-100 h-100 border-0"
              style="display: block;"></iframe>
          </div>
        </div>
      </div>

      <div class="col-12 col-xl-5 d-flex flex-column gap-4">

        <div class="ask-card card border-0 shadow-sm rounded-4">
          <div class="card-header bg-white border-bottom p-3">
            <div class="d-flex align-items-center gap-2">
              <span class="fs-5">🤖</span>
              <div>
                <h5 class="mb-0 fw-bold text-dark">Policy Assistant</h5>
                <div class="small text-muted">Ask a question and get an instant response</div>
              </div>
            </div>
          </div>

          <div class="card-body p-4">
            <div class="mb-4">
              <div class="input-group">
                <textarea v-model="query" class="form-control border bg-light shadow-none" rows="2"
                  placeholder="E.g., What is the leave policy?" style="resize: none;"
                  @keyup.enter.exact.prevent="submitQuery"></textarea>
                <button class="btn btn-primary px-4 d-flex align-items-center justify-content-center"
                  @click="submitQuery" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                  <svg v-else viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
                  </svg>
                </button>
              </div>
            </div>

            <div v-if="lastQuestion" class="answer-section fade-in">
              <div class="mb-4">
                <div class="d-flex align-items-center gap-2 mb-2">
                  <span class="badge bg-white border text-dark rounded-pill px-3 py-1 shadow-sm">You asked</span>
                </div>
                <div class="p-3 bg-white rounded-4 border text-dark shadow-sm">
                  {{ lastQuestion }}
                </div>
              </div>

              <div v-if="answer">
                <div class="d-flex align-items-center gap-2 mb-2">
                  <span
                    class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill px-3 py-1">Response</span>
                </div>
                <div class="markdown-content p-3 bg-light rounded-4 border shadow-sm" v-html="renderMessage(answer)">
                </div>
              </div>
            </div>

            <div v-else-if="!loading" class="text-center py-5 text-muted opacity-50">
              <div class="mb-2 fs-1">💬</div>
              <small>Ask a question about company policies to get started.</small>
            </div>
          </div>
        </div>

        <div class="card border-0 shadow-sm rounded-4 flex-grow-1 overflow-hidden">
          <div class="card-header bg-white border-bottom p-3 d-flex justify-content-between align-items-center">
            <h5 class="mb-0 fw-bold text-dark">📝 Policy Management</h5>
            <button v-if="isHR && !createMode && !selectedPolicy"
              class="btn btn-sm btn-primary rounded-pill px-3 fw-medium" @click="createMode = true">
              + New Policy
            </button>
          </div>

          <div class="card-body p-0 d-flex flex-column h-100 position-relative">

            <div v-if="!selectedPolicy && !createMode" class="policy-list overflow-auto" style="max-height: 500px;">
              <div v-if="policies.length > 0" class="list-group list-group-flush">
                <button v-for="policy in policies" :key="policy.id"
                  class="list-group-item list-group-item-action border-0 py-3 px-4 d-flex justify-content-between align-items-center transition-hover"
                  @click="selectAndLoadPolicy(policy)">
                  <span class="fw-medium text-dark">{{ policy.title }}</span>
                  <span class="text-muted opacity-50">›</span>
                </button>
              </div>
              <div v-else class="text-center p-5 text-muted">
                No policies available.
              </div>
            </div>

            <div v-if="createMode" class="p-4 bg-light h-100 overflow-auto">
              <div class="d-flex align-items-center justify-content-between mb-3">
                <h6 class="fw-bold mb-0">Create New Policy</h6>
                <button class="btn btn-sm btn-outline-secondary rounded-pill px-3"
                  @click="createMode = false">Cancel</button>
              </div>
              <div class="mb-3">
                <label class="form-label small text-muted fw-bold">TITLE</label>
                <input v-model="newPolicy.title" class="form-control" placeholder="Enter policy title...">
              </div>
              <div class="mb-3">
                <label class="form-label small text-muted fw-bold">CONTENT</label>
                <textarea v-model="newPolicy.content" class="form-control" rows="6"
                  placeholder="Enter policy details..."></textarea>
              </div>
              <div class="d-grid">
                <button class="btn btn-primary fw-bold py-2" @click="addPolicy">Save Policy</button>
              </div>
            </div>

            <div v-if="selectedPolicy" class="p-4 bg-light h-100 overflow-auto">
              <div class="d-flex align-items-center justify-content-between mb-4">
                <button class="btn btn-sm btn-link text-decoration-none text-muted p-0 fw-medium"
                  @click="selectedPolicy = null">
                  ← Back to list
                </button>
                <div v-if="isHR" class="d-flex gap-2">
                  <button class="btn btn-sm btn-outline-danger bg-white" @click="deletePolicy">Delete</button>
                  <button class="btn btn-sm btn-primary" @click="updatePolicy">Update Changes</button>
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label small text-muted fw-bold">TITLE</label>
                <input v-model="selectedPolicyEdit.title" class="form-control bg-white" :readonly="!isHR">
              </div>
              <div class="mb-3">
                <label class="form-label small text-muted fw-bold">CONTENT</label>
                <textarea v-model="selectedPolicyEdit.content" class="form-control bg-white" rows="10"
                  :readonly="!isHR"></textarea>
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import {
  make_getrequest,
  make_postrequest,
  make_putrequest,
  make_deleterequest,
} from "@/store/appState.js";
import { useNotify } from "@/utils/useNotify.js";
import Swal from "sweetalert2";
import MarkdownIt from "markdown-it";
import mk from "markdown-it-katex";
import DOMPurify from "dompurify";

export default {
  name: "HRPolicies",

  setup() {
    return { notify: useNotify() };
  },

  data() {
    return {
      query: "",
      lastQuestion: "",
      answer: "",
      loading: false,
      md: new MarkdownIt({
        html: true,
        linkify: true,
        typographer: true
      }).use(mk),

      policies: [],
      selectedPolicy: null,
      selectedPolicyEdit: { title: "", content: "" },
      newPolicy: { title: "", content: "" },
      createMode: false,
      isHR: true,
    };
  },

  mounted() {
    this.fetchPolicies();
  },

  methods: {
    renderMessage(text) {
      if (!text) return "";
      const rawHtml = this.md.render(text);
      return DOMPurify.sanitize(rawHtml);
    },

    async fetchPolicies() {
      try {
        const data = await make_getrequest("/api/hr/policies");
        this.policies = data.policies || [];
      } catch (err) {
        console.error("Failed to fetch policies", err);
      }
    },

    selectAndLoadPolicy(policy) {
      this.createMode = false;
      this.selectedPolicy = policy;
      this.selectedPolicyEdit = { ...policy };
    },

    toggleCreateMode() {
      this.selectedPolicy = null;
      this.createMode = !this.createMode;
    },

    async addPolicy() {
      if (!this.newPolicy.title || !this.newPolicy.content) {
        this.notify.error("Please fill in both title and content.");
        return;
      }

      try {
        const data = await make_postrequest("/api/hr/policy/create", this.newPolicy);
        this.policies.push(data.policy);

        this.newPolicy = { title: "", content: "" };
        this.createMode = false;
        this.notify.success("Policy created successfully");
      } catch (err) {
        console.error(err);
        this.notify.error(err.message);
      }
    },

    async updatePolicy() {
      if (!this.selectedPolicy) return;

      try {
        const data = await make_putrequest(
          `/api/hr/policy/${this.selectedPolicy.id}`,
          this.selectedPolicyEdit
        );

        const index = this.policies.findIndex(p => p.id === this.selectedPolicy.id);
        if (index !== -1) {
          this.policies[index] = data.policy;
        }
        Object.assign(this.selectedPolicy, data.policy);

        this.notify.success("Policy updated successfully");
      } catch (err) {
        console.error(err);
        this.notify.error(err.message);
      }
    },

    async deletePolicy() {
      if (!this.selectedPolicy) return;

      const confirm = await Swal.fire({
        title: "Are you sure?",
        text: "This action cannot be undone.",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#dc3545",
        cancelButtonColor: "#6c757d",
        confirmButtonText: "Yes, delete it!",
      });

      if (!confirm.isConfirmed) return;

      try {
        await make_deleterequest(`/api/hr/policy/${this.selectedPolicy.id}`);

        this.policies = this.policies.filter((p) => p.id !== this.selectedPolicy.id);
        this.selectedPolicy = null;
        this.selectedPolicyEdit = { title: "", content: "" };

        this.notify.success("Policy deleted successfully");
      } catch (err) {
        console.error(err);
        this.notify.error(err.message);
      }
    },

    async submitQuery() {
      if (!this.query.trim()) return;

      this.lastQuestion = this.query;
      const ask = this.query;
      this.query = "";
      this.loading = true;
      this.answer = "";

      try {
        const data = await make_postrequest("/api/hr/assistant", { question: ask });
        this.answer = data.answer || "No response received.";
      } catch (err) {
        console.error(err);
        this.answer = "Sorry, I couldn't get an answer at this time. Please try again.";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.transition-hover:hover {
  background-color: #f8f9fa;
  transform: translateX(4px);
  transition: all 0.2s ease;
}

.markdown-content {
  font-size: 0.95rem;
  line-height: 1.6;
  color: #2c3e50;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4) {
  font-weight: 700;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  color: #1a1d20;
}

.markdown-content :deep(p) {
  margin-bottom: 0.8rem;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  padding-left: 1.5rem;
  margin-bottom: 0.8rem;
}

.markdown-content :deep(li) {
  margin-bottom: 0.2rem;
}

.markdown-content :deep(strong) {
  font-weight: 600;
  color: #0d6efd;
}

.markdown-content :deep(a) {
  color: #0d6efd;
  text-decoration: underline;
}

.markdown-content :deep(pre) {
  background: #212529;
  color: #f8f9fa;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin-bottom: 1rem;
}

.markdown-content :deep(code) {
  background: #e9ecef;
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
  font-size: 0.875em;
  color: #d63384;
}
</style>