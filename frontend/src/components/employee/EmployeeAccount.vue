<template>
  <div class="container-fluid py-4" style="max-width: 850px;">
    <section class="card border-0 shadow-sm mb-4">
      <div class="card-body p-4 d-flex align-items-center gap-4 flex-wrap flex-sm-nowrap">
        <div class="avatar flex-shrink-0">
          <img v-if="user.img_base64" :src="user.img_base64" alt="Profile" class="avatar-img rounded-circle" />
          <span v-else>{{ userInitials }}</span>
        </div>
        <div class="profile-info">
          <h2 class="h3 mb-1 text-dark">{{ user.name }}</h2>
          <p class="fw-medium text-secondary mb-1">{{ user.role }}</p>
          <p class="small text-muted mb-0">{{ user.department }}</p>
        </div>
      </div>
    </section>

    <section class="card border-0 shadow-sm mb-4">
      <div class="card-body p-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h3 class="h5 mb-0 text-dark fw-bold">Account Information</h3>
          <button class="btn btn-outline-secondary btn-sm" @click="resetForm" :disabled="loading">
            Reset
          </button>
        </div>

        <div v-if="loading" class="text-center py-4 text-muted fst-italic">
          Loading account details...
        </div>

        <div v-else class="row g-3">
          <div class="col-md-6" v-for="(value, key) in editableFields" :key="key">
            <label :for="key" class="form-label fw-medium text-secondary">{{ keyLabels[key] }}</label>
            <input :id="key" v-model="user[key]" :readonly="key === 'department'" :type="inputTypes[key]"
              class="form-control" :class="{ 'bg-light': key === 'department' }" />
          </div>
        </div>
      </div>
    </section>

    <section class="card border-0 shadow-sm mb-4">
      <div class="card-body p-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h3 class="h5 mb-0 text-dark fw-bold">Skills & Expertise</h3>
          <button class="btn btn-primary btn-sm" @click="openAddSkillModal">
            <i class="bi bi-plus-lg me-1"></i> Add Skill
          </button>
        </div>

        <div v-if="skillsLoading" class="text-center py-4 text-muted fst-italic">
          Loading skills...
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light text-secondary">
              <tr>
                <th class="border-0">Skill Name</th>
                <th class="border-0">Proficiency</th>
                <th class="border-0">Experience (Yrs)</th>
                <th class="border-0 text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="skill in skills" :key="skill.id">
                <td class="fw-medium text-dark">{{ skill.skill_name }}</td>
                <td>
                  <span class="badge rounded-pill fw-normal px-3"
                    :class="getProficiencyBadgeClass(skill.proficiency_level)">
                    {{ skill.proficiency_level }}
                  </span>
                </td>
                <td class="text-secondary">{{ skill.years_of_experience }}</td>
                <td class="text-end">
                  <button class="btn btn-sm btn-link text-primary p-0 me-3" @click="openEditSkillModal(skill)"
                    title="Edit">
                    <i class="bi bi-pencil-fill"></i>
                  </button>
                  <button class="btn btn-sm btn-link text-danger p-0" @click="deleteSkill(skill)" title="Delete">
                    <i class="bi bi-trash-fill"></i>
                  </button>
                </td>
              </tr>
              <tr v-if="skills.length === 0">
                <td colspan="4" class="text-center py-4 text-muted">
                  No skills added yet. Add your skills to showcase your expertise.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <div class="d-flex justify-content-between align-items-center mb-5">
      <button class="btn btn-primary px-4" @click="updateProfile" :disabled="loading">
        Update Profile
      </button>
      <button class="btn btn-danger px-4" @click="logout" :disabled="loading">
        Logout
      </button>
    </div>

    <Teleport to="body">
      <div class="modal fade" id="skillModal" tabindex="-1" ref="skillModal">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content border-0 shadow">
            <div class="modal-header bg-primary text-white border-bottom-0">
              <h5 class="modal-title fw-bold">{{ editingSkillId ? 'Edit Skill' : 'Add Skill' }}</h5>
              <button type="button" class="btn-close btn-close-white" @click="closeSkillModal"></button>
            </div>
            <div class="modal-body p-4">
              <form @submit.prevent="saveSkill">
                <div class="mb-3">
                  <label for="skillName" class="form-label fw-medium text-secondary">Skill Name</label>
                  <input type="text" class="form-control" id="skillName" v-model="skillForm.skill_name" required
                    placeholder="e.g. Python, Project Management">
                </div>
                <div class="mb-3">
                  <label for="proficiency" class="form-label fw-medium text-secondary">Proficiency Level</label>
                  <select class="form-select" id="proficiency" v-model="skillForm.proficiency_level" required>
                    <option v-for="opt in proficiencyOptions" :key="opt" :value="opt">{{ opt }}</option>
                  </select>
                </div>
                <div class="mb-4">
                  <label for="experience" class="form-label fw-medium text-secondary">Years of Experience</label>
                  <input type="number" step="0.5" min="0" class="form-control" id="experience"
                    v-model.number="skillForm.years_of_experience" required>
                </div>
                <div class="d-flex justify-content-end gap-2">
                  <button type="button" class="btn btn-secondary" @click="closeSkillModal">Cancel</button>
                  <button type="submit" class="btn btn-primary px-4 shadow-sm" :disabled="skillSubmitting">
                    {{ skillSubmitting ? 'Saving...' : 'Save Skill' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script>
import { make_getrequest, make_putrequest, make_postrequest, make_deleterequest } from "@/store/appState.js";
import { useNotify } from "@/utils/useNotify.js";
import Swal from 'sweetalert2';
import 'bootstrap-icons/font/bootstrap-icons.css';
import bootstrap from "bootstrap/dist/js/bootstrap.bundle";

export default {
  name: "EmployeeAccount",
  data() {
    return {
      user: {
        name: "",
        email: "",
        role: "",
        department: "",
        img_base64: null,
      },
      originalUser: {},
      loading: false,

      skills: [],
      skillsLoading: false,
      showSkillModal: false,
      skillSubmitting: false,
      editingSkillId: null,
      skillForm: {
        skill_name: '',
        proficiency_level: 'Intermediate',
        years_of_experience: 0
      },
      proficiencyOptions: ['Beginner', 'Intermediate', 'Advanced', 'Expert'],
      modalInstance: null,

      keyLabels: {
        name: "Full Name",
        email: "Email",
        department: "Department",
      },
      inputTypes: {
        name: "text",
        email: "email",
        department: "text",
      },
    };
  },
  computed: {
    editableFields() {
      const fields = {};
      if (this.user.name !== undefined) fields.name = this.user.name;
      if (this.user.email !== undefined) fields.email = this.user.email;
      if (this.user.department !== undefined) fields.department = this.user.department;
      return fields;
    },
    userInitials() {
      if (!this.user.name) return "";
      return this.user.name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2);
    },
  },
  mounted() {
    this.modalInstance = new bootstrap.Modal(this.$refs.skillModal);
    this.fetchAccount();
    this.fetchSkills();
  },
  methods: {
    async fetchAccount() {
      this.loading = true;
      try {
        const data = await make_getrequest("/api/employee/account");
        this.user = {
          name: data.name,
          email: data.email,
          role: data.role,
          department: data.department_name || "Not Assigned",
          img_base64: data.img_base64,
          department_id: data.department_id,
          reporting_manager: data.reporting_manager,
        };
        this.originalUser = JSON.parse(JSON.stringify(this.user));
      } catch (error) {
        console.error("Failed to fetch account:", error);
        useNotify().error("Failed to load account information.");
      } finally {
        this.loading = false;
      }
    },
    async updateProfile() {
      this.loading = true;
      try {
        const payload = {
          name: this.user.name,
          email: this.user.email,
        };

        await make_putrequest("/api/employee/account", payload);

        this.originalUser = JSON.parse(JSON.stringify(this.user));
        useNotify().success("Profile updated successfully!");
      } catch (error) {
        console.error("Failed to update profile:", error);
        useNotify().error("Failed to update profile. Please try again.");
      } finally {
        this.loading = false;
      }
    },
    resetForm() {
      Swal.fire({
        title: 'Reset Changes?',
        text: "Are you sure you want to discard your changes?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, reset it!'
      }).then((result) => {
        if (result.isConfirmed) {
          this.user = JSON.parse(JSON.stringify(this.originalUser));
          useNotify().info('Changes reset.');
        }
      });
    },

    async fetchSkills() {
      this.skillsLoading = true;
      try {
        const data = await make_getrequest("/api/employee/account/skills");
        this.skills = data || [];
      } catch (error) {
        console.error("Failed to fetch skills:", error);
      } finally {
        this.skillsLoading = false;
      }
    },
    openAddSkillModal() {
      this.editingSkillId = null;
      this.skillForm = {
        skill_name: '',
        proficiency_level: 'Intermediate',
        years_of_experience: 0
      };
      this.modalInstance.show();
    },
    openEditSkillModal(skill) {
      this.editingSkillId = skill.id;
      this.skillForm = {
        skill_name: skill.skill_name,
        proficiency_level: skill.proficiency_level,
        years_of_experience: skill.years_of_experience
      };
      this.modalInstance.show();
    },
    closeSkillModal() {
      this.modalInstance.hide();
      this.skillSubmitting = false;
    },
    async saveSkill() {
      this.skillSubmitting = true;
      try {
        if (this.editingSkillId) {
          await make_putrequest(`/api/employee/account/skills/${this.editingSkillId}`, this.skillForm);
          useNotify().success("Skill updated successfully.");
        } else {
          await make_postrequest("/api/employee/account/skills", this.skillForm);
          useNotify().success("Skill added successfully.");
        }
        await this.fetchSkills();
        this.closeSkillModal();
      } catch (error) {
        console.error("Failed to save skill:", error);
        useNotify().error("Failed to save skill. " + (error.message || ''));
      } finally {
        this.skillSubmitting = false;
      }
    },
    async deleteSkill(skill) {
      const result = await Swal.fire({
        title: 'Delete Skill?',
        text: `Are you sure you want to delete ${skill.skill_name}?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Yes, delete it!'
      });

      if (result.isConfirmed) {
        try {
          await make_deleterequest(`/api/employee/account/skills/${skill.id}`);
          useNotify().success("Skill deleted.");
          await this.fetchSkills();
        } catch (error) {
          console.error("Failed to delete skill:", error);
          useNotify().error("Failed to delete skill.");
        }
      }
    },
    getProficiencyBadgeClass(level) {
      const map = {
        'Beginner': 'bg-info-subtle text-info border border-info-subtle',
        'Intermediate': 'bg-primary-subtle text-primary border border-primary-subtle',
        'Advanced': 'bg-success-subtle text-success border border-success-subtle',
        'Expert': 'bg-warning-subtle text-warning border border-warning-subtle'
      };
      return map[level] || 'bg-secondary-subtle text-secondary';
    },

    async logout() {
      const result = await Swal.fire({
        title: 'Logout?',
        text: "Are you sure you want to logout?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, logout!'
      });

      if (result.isConfirmed) {
        this.loading = true;
        this.$store.dispatch('logout');
        this.$router.push({ name: "Login" });
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.avatar {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: linear-gradient(135deg, #007bff, #0056d2);
  color: #fff;
  font-weight: 600;
  font-size: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

@media (max-width: 576px) {
  .avatar {
    width: 70px;
    height: 70px;
    font-size: 22px;
  }
}
</style>