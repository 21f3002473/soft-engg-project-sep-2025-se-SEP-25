<template>
  <div class="container-fluid py-4">
    <div class="container">
      <div class="row g-4">

        <div class="col-12 col-md-6">
          <div class="card h-100">
            <div class="card-body p-0">
              <div class="ratio ratio-4x3">
                <iframe src="/docs/Human Resources Policy.pdf" frameborder="0" class="w-100 h-100"></iframe>
              </div>
            </div>
            <div class="card-footer text-muted small">Company Policies</div>
          </div>
        </div>

        <div class="col-12 col-md-6 d-flex flex-column">

          <div class="card mb-3">
            <div class="card-header bg-primary text-white">
              HR Policies Management
            </div>
            <div class="card-body d-flex flex-column gap-2">

              <div class="d-flex gap-2 flex-wrap">
                <button v-for="policy in policies" :key="policy.id" class="btn btn-outline-primary"
                  @click="viewPolicy(policy)">
                  {{ policy.title }}
                </button>
              </div>

              <div v-if="isHR" class="mt-3">
                <input v-model="newPolicy.title" placeholder="Policy Title" class="form-control mb-2" />
                <textarea v-model="newPolicy.content" placeholder="Policy Content" class="form-control mb-2"
                  rows="3"></textarea>
                <button class="btn btn-primary" @click="addPolicy">Add Policy</button>
              </div>

              <div v-if="selectedPolicy" class="mt-3 p-3 border rounded bg-light">
                <h5>{{ selectedPolicy.title }}</h5>
                <p>{{ selectedPolicy.content }}</p>
              </div>

            </div>
          </div>

          <div class="chat-card card flex-grow-1 d-flex flex-column">
            <div class="card-header bg-primary text-white">
              HR Policies — Ask Here
            </div>

            <div class="chat-body flex-grow-1 p-3" ref="chatBody">
              <div v-for="(msg, index) in messages" :key="index" :class="['chat-message', msg.role]">
                <div class="message-text">{{ msg.text }}</div>
              </div>
            </div>

            <div class="card-footer p-3 bg-light d-flex gap-2">
              <textarea v-model="query" placeholder="Type your question about HR policies..." class="form-control"
                rows="2" @keyup.enter.exact.prevent="submitQuery"></textarea>
              <button class="btn btn-primary" @click="submitQuery" :disabled="loading">
                {{ loading ? "Asking..." : "Ask" }}
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { make_getrequest, make_postrequest } from "@/store/appState.js";

export default {
  name: "HRPolicies",
  data() {
    return {
      query: "",
      messages: [],
      loading: false,
      policies: [],
      selectedPolicy: null,
      newPolicy: { title: "", content: "" },
      isHR: true,
    };
  },
  mounted() {
    this.fetchPolicies();
  },
  methods: {
    async fetchPolicies() {
      try {
        const data = await make_getrequest("/api/hr/policies");
        this.policies = data.policies || [];
      } catch (err) {
        console.error("Failed to fetch policies", err);
      }
    },
    viewPolicy(policy) {
      this.selectedPolicy = policy;
    },
    async addPolicy() {
      if (!this.newPolicy.title || !this.newPolicy.content) return;

      try {
        const data = await make_postrequest("/api/hr/policy/create", this.newPolicy);
        this.policies.push(data.policy);
        this.newPolicy = { title: "", content: "" };
      } catch (err) {
        console.error("Error creating policy", err);
        alert(err.message || "Failed to create policy");
      }
    },
    async submitQuery() {
      if (!this.query.trim()) return;

      this.messages.push({ role: "user", text: this.query });
      const userQuery = this.query;
      this.query = "";
      this.loading = true;

      try {
        const data = await make_postrequest("/api/hr/assistant", { question: userQuery });
        const answer = data.answer || "No response.";

        this.messages.push({ role: "ai", text: answer });

        this.$nextTick(() => {
          const chat = this.$refs.chatBody;
          chat.scrollTop = chat.scrollHeight;
        });
      } catch (err) {
        console.error(err);
        this.messages.push({ role: "ai", text: "Error communicating with server." });
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>