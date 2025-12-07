<template>
  <div class="policies-content container-fluid">

    <div class="row g-4 align-items-stretch">

      <div class="col-12 col-md-6 d-flex">
        <div class="card flex-fill border-0 shadow-sm rounded-3">
          <div class="card-body p-0">
            <div class="ratio ratio-4x3 h-100">
              <iframe
                src="/docs/Human Resources Policy.pdf"
                frameborder="0"
                class="w-100 h-100 rounded-top"
              ></iframe>
            </div>
          </div>
          <div class="card-footer text-muted small bg-white rounded-bottom">
            Company Policies
          </div>
        </div>
      </div>

      <div class="col-12 col-md-6 d-flex">
        <div class="card flex-fill border-0 shadow-sm rounded-3">

          <div class="card-header bg-primary text-white rounded-top">
            HR Policies Management
          </div>

          <div class="card-body d-flex flex-column gap-2">

            <div class="d-flex gap-2 flex-wrap">
              <button
                v-for="policy in policies"
                :key="policy.id"
                class="btn btn-outline-primary"
                @click="selectAndLoadPolicy(policy)"
              >
                {{ policy.title }}
              </button>
            </div>

            <div v-if="isHR" class="mt-3 border p-3 rounded">
              <h6>Create New Policy</h6>
              <input
                v-model="newPolicy.title"
                placeholder="Policy Title"
                class="form-control mb-2"
              />
              <textarea
                v-model="newPolicy.content"
                placeholder="Policy Content"
                class="form-control mb-2"
                rows="3"
              ></textarea>
              <button class="btn btn-primary" @click="addPolicy">Add Policy</button>
            </div>

            <div
              v-if="selectedPolicy"
              class="mt-3 p-3 border rounded bg-light"
            >
              <h5>Selected Policy</h5>

              <label class="fw-bold">Title:</label>
              <input
                v-model="selectedPolicyEdit.title"
                class="form-control mb-2"
                :readonly="!isHR"
              />

              <label class="fw-bold">Content:</label>
              <textarea
                v-model="selectedPolicyEdit.content"
                class="form-control mb-2"
                rows="4"
                :readonly="!isHR"
              ></textarea>

              <div v-if="isHR" class="d-flex gap-2 mt-2">
                <button class="btn btn-primary" @click="updatePolicy">Update</button>
                <button class="btn btn-danger" @click="deletePolicy">Delete</button>
              </div>
            </div>

          </div>
        </div>
      </div>

    </div>

    <div class="row mt-4">
      <div class="col-12">
        <div class="chat-card card border-0 shadow-sm rounded-3">

          <div class="card-header bg-primary text-white rounded-top">
            HR Policies — Ask Here
          </div>

          <div
            ref="chatBody"
            class="chat-body p-3 flex-grow-1 d-flex flex-column"
          >
            <div
              v-for="(msg, index) in messages"
              :key="index"
              :class="['message', msg.role, 'p-2', 'px-3', 'rounded-4']"
            >
              <div class="message-content text-break">{{ msg.text }}</div>
            </div>
          </div>

          <!-- CHAT INPUT -->
          <div class="card-footer p-3 bg-light d-flex gap-2 rounded-bottom">
            <textarea
              v-model="query"
              class="form-control"
              rows="2"
              placeholder="Type your question..."
              @keyup.enter.exact.prevent="submitQuery"
            ></textarea>

            <button class="btn btn-primary" @click="submitQuery" :disabled="loading">
              {{ loading ? "Asking..." : "Ask" }}
            </button>
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

export default {
  name: "HRPolicies",

  setup() {
    return { notify: useNotify() };
  },

  data() {
    return {
      query: "",
      messages: [],
      loading: false,

      policies: [],
      selectedPolicy: null,
      selectedPolicyEdit: { title: "", content: "" },

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

    selectAndLoadPolicy(policy) {
      this.selectedPolicy = policy;
      this.selectedPolicyEdit = { ...policy };
    },

    async addPolicy() {
      if (!this.newPolicy.title || !this.newPolicy.content) return;

      try {
        const data = await make_postrequest("/api/hr/policy/create", this.newPolicy);
        this.policies.push(data.policy);

        this.newPolicy = { title: "", content: "" };
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

        Object.assign(this.selectedPolicy, data.policy);
        this.notify.success("Policy updated successfully");
      } catch (err) {
        console.error(err);
        this.notify.error(err.message);
      }
    },

    async deletePolicy() {
      if (!this.selectedPolicy) return;

      //const confirm = await Swal.fire({
        //title: "Are you sure?",
        //text: "Do you really want to delete this policy?",
        //icon: "warning",
        //showCancelButton: true,
        //confirmButtonColor: "#dc3545",
        //confirmButtonColor: "#6c757d",
        //confirmButtonText: "Yes, delete it!",
      //});

      const confirm = await Swal.fire({
      title: "Are you sure?",
      text: "Do you really want to delete this policy?",
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

      this.messages.push({ role: "user", text: this.query });

      const ask = this.query;
      this.query = "";
      this.loading = true;

      try {
        const data = await make_postrequest("/api/hr/assistant", { question: ask });
        const answer = data.answer || "No response.";

        this.messages.push({ role: "ai", text: answer });

        this.$nextTick(() => {
          const chat = this.$refs.chatBody;
          if (chat) chat.scrollTop = chat.scrollHeight;
        });
      } catch (err) {
        console.error(err);
        this.messages.push({ role: "ai", text: "Server error." });
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.message {
  max-width: 80%;
  word-break: break-word;
  animation: fadeIn 0.2s ease;
  margin-bottom: 10px;
}

.message.user {
  background: linear-gradient(90deg, #007bff, #0056d2);
  color: #fff;
  align-self: flex-end;
}

.message.ai {
  background: #e8f0ff;
  color: #004085;
  border: 1px solid #d0e0ff;
  align-self: flex-start;
}

.chat-body {
  min-height: 300px;
  max-height: 500px;
  overflow-y: auto;
  background: #f8faff !important;
}

.chat-card {
  display: flex;
  flex-direction: column;
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
