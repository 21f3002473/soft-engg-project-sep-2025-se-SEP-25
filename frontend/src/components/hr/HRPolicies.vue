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
                  @click="selectAndLoadPolicy(policy)">
                  {{ policy.title }}
                </button>
              </div>

              <div v-if="isHR" class="mt-3 border p-3 rounded">
                <h6>Create New Policy</h6>
                <input v-model="newPolicy.title" placeholder="Policy Title" class="form-control mb-2" />
                <textarea v-model="newPolicy.content" placeholder="Policy Content" class="form-control mb-2"
                  rows="3"></textarea>
                <button class="btn btn-success" @click="addPolicy">Add Policy</button>
              </div>

              <div v-if="selectedPolicy" class="mt-3 p-3 border rounded bg-light">
                <h5>Selected Policy</h5>

                <label class="fw-bold">Title:</label>
                <input v-model="selectedPolicyEdit.title" class="form-control mb-2" :readonly="!isHR" />

                <label class="fw-bold">Content:</label>
                <textarea v-model="selectedPolicyEdit.content" class="form-control mb-2" rows="4"
                  :readonly="!isHR"></textarea>

                <div v-if="isHR" class="d-flex gap-2 mt-2">
                  <button class="btn btn-primary" @click="updatePolicy">Update</button>
                  <button class="btn btn-danger" @click="deletePolicy">Delete</button>
                </div>
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
              <textarea v-model="query" placeholder="Type your question..." class="form-control" rows="2"
                @keyup.enter.exact.prevent="submitQuery"></textarea>
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
import { make_getrequest, make_postrequest, make_putrequest, make_deleterequest } from "@/store/appState.js";
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
        console.error("Error creating policy", err);
        this.notify.error(err.message || "Failed to create policy");
      }
    },

    async updatePolicy() {
      if (!this.selectedPolicy) return;

      try {
        const data = await make_putrequest(`/api/hr/policy/${this.selectedPolicy.id}`, this.selectedPolicyEdit);
        Object.assign(this.selectedPolicy, data.policy);
        this.notify.success("Policy updated successfully");
      } catch (err) {
        console.error("Update error:", err);
        this.notify.error(err.message || "Failed to update");
      }
    },

    async deletePolicy() {
      if (!this.selectedPolicy) return;

      const result = await Swal.fire({
        title: "Are you sure?",
        text: "Do you really want to delete this policy?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#dc3545",
        cancelButtonColor: "#6c757d",
        confirmButtonText: "Yes, delete it!"
      });

      if (!result.isConfirmed) return;

      try {
        await make_deleterequest(`/api/hr/policy/${this.selectedPolicy.id}`);
        this.policies = this.policies.filter(
          (p) => p.id !== this.selectedPolicy.id
        );

        this.selectedPolicy = null;
        this.selectedPolicyEdit = { title: "", content: "" };

        this.notify.success("Policy deleted successfully");
      } catch (err) {
        console.error("Delete error:", err);
        this.notify.error(err.message || "Failed to delete");
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
        this.messages.push({ role: "ai", text: "Server error." });
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>