
<template>
  <div class="container-fluid py-4">
    <div class="container">
      <div class="row g-4">

        <!-- PDF Viewer -->
        <div class="col-12 col-md-6">
          <div class="card h-100"> 
            <div class="card-body p-0">
              <div class="ratio ratio-4x3"> 
                <iframe
                  src="/docs/Human Resources Policy.pdf"
                  frameborder="0"
                  class="w-100 h-100"
                ></iframe>
              </div>
            </div>
            <div class="card-footer text-muted small">Company Policies</div>
          </div>
        </div>

        <!-- HR Policies Management & Chat -->
        <div class="col-12 col-md-6 d-flex flex-column">

          <!-- Policy Buttons Section -->
          <div class="card mb-3">
            <div class="card-header bg-primary text-white">
              HR Policies Management
            </div>
            <div class="card-body d-flex flex-column gap-2">

              <div class="d-flex gap-2 flex-wrap">
                <button
                  v-for="policy in policies"
                  :key="policy.id"
                  class="btn btn-outline-primary"
                  @click="viewPolicy(policy)"
                >
                  {{ policy.title }}
                </button>
              </div>

              <!-- New Policy Form (visible only if HR) -->
              <div v-if="isHR" class="mt-3">
                <input v-model="newPolicy.title" placeholder="Policy Title" class="form-control mb-2"/>
                <textarea v-model="newPolicy.content" placeholder="Policy Content" class="form-control mb-2" rows="3"></textarea>
                <button class="btn btn-primary" @click="addPolicy">Add Policy</button>
              </div>

              <!-- Display selected policy -->
              <div v-if="selectedPolicy" class="mt-3 p-3 border rounded bg-light">
                <h5>{{ selectedPolicy.title }}</h5>
                <p>{{ selectedPolicy.content }}</p>
              </div>

            </div>
          </div>

          <!-- HR Assistant Chat (unchanged) -->
          <div class="chat-card card flex-grow-1 d-flex flex-column">
            <div class="card-header bg-primary text-white">
              HR Policies — Ask Here
            </div>

            <div class="chat-body flex-grow-1 p-3" ref="chatBody">
              <div
                v-for="(msg, index) in messages"
                :key="index"
                :class="['chat-message', msg.role]"
              >
                <div class="message-text">{{ msg.text }}</div>
              </div>
            </div>

            <div class="card-footer p-3 bg-light d-flex gap-2">
              <textarea
                v-model="query"
                placeholder="Type your question about HR policies..."
                class="form-control"
                rows="2"
                @keyup.enter.exact.prevent="submitQuery"
              ></textarea>
              <button
                class="btn btn-primary"
                @click="submitQuery"
                :disabled="loading"
              >
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
      isHR: true, // Set dynamically based on user role
    };
  },
  mounted() {
    this.fetchPolicies();
  },
  methods: {
    async fetchPolicies() {
      try {
        //const res = await fetch("http://127.0.0.1:8000/api/hr/policies");
        const res = await fetch("http://127.0.0.1:8000/api/hr/policies", {
        headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        });
        const data = await res.json();
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
        const res = await fetch("http://127.0.0.1:8000/api/hr/policy/create", {
          method: "POST",
          //headers: { "Content-Type": "application/json" },
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },

          body: JSON.stringify(this.newPolicy),
        });

        const data = await res.json();
        if (res.ok) {
          this.policies.push(data.policy);
          this.newPolicy = { title: "", content: "" };
        } else {
          alert(data.error || "Failed to create policy");
        }
      } catch (err) {
        console.error("Error creating policy", err);
      }
    },
    async submitQuery() {
      if (!this.query.trim()) return;

      this.messages.push({ role: "user", text: this.query });
      const userQuery = this.query;
      this.query = "";
      this.loading = true;

      try {
        const res = await fetch("http://127.0.0.1:8000/api/hr/assistant", {
          method: "POST",
          //headers: { "Content-Type": "application/json" },
          headers: {
          "Content-Type": "application/json",
           Authorization: `Bearer ${localStorage.getItem("token")}`,
          },

          body: JSON.stringify({ question: userQuery }),
        });

        const data = await res.json();
        const answer = res.ok ? data.answer : data.error || "No response.";

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


<!-- <style scoped>
.hrpolicies-root {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
  color: #fff;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  /* background: url('../../assets/images/landing/landingPageBackgroundImage.png') no-repeat center center/cover; */
  /* background-color: rgba(20, 40, 108, 0.85);
  background-blend-mode: overlay; */
}

/* Navbar */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(90, 160, 255, 0.1);
  backdrop-filter: blur(4px);
  padding: 20px 40px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  position: sticky;
  top: 0;
  z-index: 10;

  /* ensure navbar does not wrap its children */
  flex-wrap: nowrap;
}

/* left brand (keeps it compact) */
.brand {
  font-style: italic;
  font-weight: 700;
  color: #ffffff;
  font-size: 24px;
  line-height: 1;
  white-space: nowrap;
}

/* right group: always horizontal, with gap between links */
.nav-right {
  display: flex;
  align-items: center;
  gap: 20px;        /* spacing between links */
  flex-wrap: nowrap; /* prevent wrapping into multiple rows */
  justify-content: flex-end;
}

/* ensure each link stays on one line and is inline-flex for vertical centering */
.nav-link {
  display: inline-flex;
  align-items: center;
  white-space: nowrap; /* prevent internal wrapping of long labels */
  color: white;
  text-decoration: none;
  font-size: 18px;
  margin-left: 0;      /* gap handled by .nav-right gap */
  padding: 6px 8px;
  transition: color 0.3s;
}

/* hover / active styles unchanged */
.nav-link:hover,
.nav-link.active {
  color: #dce3ff;
}
.brand {
  font-style: italic;
  font-weight: 700;
  color: #ffffff;
  font-size: 24px;
}
.nav-link {
  color: white;
  text-decoration: none;
  font-size: 18px;
  margin-left: 25px;
  transition: color 0.3s;
}
.nav-link:hover,
.nav-link.active {
  color: #dce3ff;
}

/* Main section */
.hrpolicies-section {
  flex-grow: 1;
  display: flex;
  justify-content: center;
  padding: 60px 20px;
}

/* 🔹 Changed to 50%-50% layout */
.hrpolicies-container {
  display: grid;
  grid-template-columns: 1fr 1fr; /* Equal split */
  gap: 40px;
  width: 90%;
  max-width: 1200px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 40px;
}

/* PDF Viewer */
.pdf-viewer {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
}
.pdf-frame {
  width: 100%;
  height: 600px;
  border: none;
}

/* Ask box */
.ask-box {
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.25);
}
.ask-title {
  font-size: 22px;
  color: #c7d2fe;
  font-weight: 600;
  margin-bottom: 15px;
  text-align: center;
}
.ask-input {
  background: rgba(255, 255, 255, 0.9);
  color: #1e3a8a;
  border: none;
  border-radius: 8px;
  padding: 12px;
  font-size: 16px;
  min-height: 180px;
  resize: vertical;
  outline: none;
}
.ask-button {
  background: linear-gradient(90deg, #6366f1, #3b82f6);
  border: none;
  color: white;
  border-radius: 8px;
  padding: 10px;
  font-size: 16px;
  margin-top: 15px;
  cursor: pointer;
  font-weight: 600;
  transition: transform 0.2s;
}
.ask-button:hover {
  transform: translateY(-2px);
  background: linear-gradient(90deg, #818cf8, #60a5fa);
}
.response-box {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  padding: 12px;
  margin-top: 20px;
  color: #e0e7ff;
  font-size: 15px;
}

/* Footer */
.footer {
  text-align: center;
  padding: 16px 0;
  color: #e5e7eb;
  background: rgba(0, 0, 0, 0.3);
  font-size: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
}

/* Responsive */
@media (max-width: 900px) {
  .hrpolicies-container {
    grid-template-columns: 1fr;
  }
  .pdf-frame {
    height: 400px;
  }
}
</style> -->