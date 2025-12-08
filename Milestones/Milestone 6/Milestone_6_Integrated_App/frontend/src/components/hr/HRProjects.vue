<template>
  <div class="projects-content">
    <header class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h4 mb-0">Projects Overview</h1>
    </header>
    <div class="card border-0 shadow-sm rounded-3">
      <div class="card-body">
        <div class="mb-3">
          <input type="text" v-model="searchQuery" class="form-control"
            placeholder="Search by Project Name or Manager..." />
        </div>

        <div class="table-responsive">
          <table class="table table-striped table-hover mb-0">
            <thead class="table-dark">
              <tr>
                <th scope="col">Project Name</th>
                <th scope="col">Project Manager</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(project, index) in filteredProjects" :key="index">
                <td>{{ project.name }}</td>
                <td>{{ project.manager }}</td>
              </tr>
              <tr v-if="filteredProjects.length === 0">
                <td colspan="2" class="text-center fst-italic">
                  No matching projects found.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { make_getrequest } from "@/store/appState.js";
import { useNotify } from "@/utils/useNotify.js";

export default {
  name: "HRProjects",

  setup() {
    return { notify: useNotify() };
  },

  data() {
    return {
      searchQuery: "",
      projects: [],
    };
  },

  computed: {
    filteredProjects() {
      if (!this.searchQuery.trim()) return this.projects;
      const q = this.searchQuery.toLowerCase();
      return this.projects.filter(
        (p) =>
          p.name.toLowerCase().includes(q) ||
          p.manager.toLowerCase().includes(q)
      );
    },
  },

  mounted() {
    this.fetchProjects();
  },

  methods: {
    async fetchProjects() {
      try {
        const data = await make_getrequest("/api/hr/projects-overview");
        this.projects = data.projects || [];
      } catch (err) {
        console.error("Error fetching projects:", err);
        this.notify.error("Failed to load projects");
      }
    },
  },
};
</script>