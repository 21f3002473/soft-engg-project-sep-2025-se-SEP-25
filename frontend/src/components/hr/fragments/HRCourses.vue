<template>
    <div class="hr-courses">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h5 class="mb-0 text-secondary fw-bold">Learning Courses</h5>
            <button class="btn btn-primary btn-sm shadow-sm me-2" @click="openAssignModal()">
                <i class="bi bi-person-plus me-1"></i> Assign Course
            </button>
            <button class="btn btn-primary btn-sm shadow-sm" @click="openModal()">
                <i class="bi bi-plus-lg me-1"></i> Add Course
            </button>
        </div>

        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>

        <div v-else-if="courses.length === 0" class="text-center py-5 bg-light rounded-3 border border-dashed">
            <i class="bi bi-book-half text-muted fs-1 mb-3 d-block"></i>
            <p class="text-muted mb-0">No courses available.</p>
        </div>

        <div v-else class="row g-4">
            <div v-for="course in courses" :key="course.id" class="col-md-6 col-lg-4">
                <div class="card h-100 shadow-sm border-0 course-card">
                    <div class="card-body d-flex flex-column p-4">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <div class="rounded-circle bg-primary bg-opacity-10 p-3 text-primary">
                                <i class="bi bi-journal-check fs-4"></i>
                            </div>
                            <div class="dropdown">
                                <button class="btn btn-link text-muted p-0" type="button" data-bs-toggle="dropdown">
                                    <i class="bi bi-three-dots"></i>
                                </button>
                                <ul class="dropdown-menu dropdown-menu-end border-0 shadow">
                                    <li><button class="dropdown-item" @click="openModal(course)">Edit</button></li>
                                    <li><button class="dropdown-item text-danger"
                                            @click="confirmDelete(course)">Delete</button></li>
                                </ul>
                            </div>
                        </div>

                        <h5 class="card-title fw-bold text-dark text-truncate mb-2" :title="course.course_name">
                            {{ course.course_name }}
                        </h5>

                        <p class="card-text text-muted small mb-4 flex-grow-1">
                            <i class="bi bi-tags me-1"></i>
                            <span v-if="course.topics" :title="course.topics">
                                {{ truncate(course.topics, 50) }}
                            </span>
                            <span v-else>No topics listed</span>
                        </p>

                        <div class="mt-auto pt-3 border-top">
                            <a v-if="course.course_link" :href="course.course_link" target="_blank"
                                class="btn btn-outline-primary w-100 btn-sm">
                                <i class="bi bi-box-arrow-up-right me-1"></i> Access Course
                            </a>
                            <button v-else class="btn btn-outline-secondary w-100 btn-sm disabled">
                                No Link Available
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="modal fade" id="courseModal" tabindex="-1" ref="modal">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content border-0 shadow">
                    <div class="modal-header bg-primary text-white border-bottom-0">
                        <h5 class="modal-title fw-bold">{{ isEditing ? 'Edit' : 'Create' }} Course</h5>
                        <button type="button" class="btn-close btn-close-white" @click="closeModal"></button>
                    </div>
                    <div class="modal-body p-4">
                        <form @submit.prevent="submitForm">
                            <div class="mb-3">
                                <label class="form-label fw-medium">Course Name</label>
                                <input v-model="form.course_name" type="text" class="form-control" required
                                    placeholder="E.g., Intro to Python">
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-medium">Topics (comma separated)</label>
                                <input v-model="form.topics" type="text" class="form-control"
                                    placeholder="E.g., Coding, Data Science">
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-medium">Course Link</label>
                                <input v-model="form.course_link" type="url" class="form-control"
                                    placeholder="https://...">
                                <div class="form-text">Full URL to the external learning resource.</div>
                            </div>
                            <div class="d-flex justify-content-end pt-2">
                                <button type="button" class="btn btn-secondary me-2" @click="closeModal">Cancel</button>
                                <button type="submit" class="btn btn-primary shadow-sm">
                                    {{ isEditing ? 'Update Course' : 'Add Course' }}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <div class="modal fade" id="assignModal" tabindex="-1" ref="assignModal">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content border-0 shadow">
                    <div class="modal-header bg-primary text-white border-bottom-0">
                        <h5 class="modal-title fw-bold">Assign Course</h5>
                        <button type="button" class="btn-close btn-close-white" @click="closeAssignModal"></button>
                    </div>
                    <div class="modal-body p-4">
                        <form @submit.prevent="submitAssignment">
                            <div class="mb-3">
                                <label class="form-label fw-medium">Select Employee</label>
                                <select v-model="assignForm.employee_id" class="form-select" required>
                                    <option value="" disabled>Choose an employee...</option>
                                    <option v-for="emp in employees" :key="emp.id" :value="emp.id">
                                        {{ emp.name }}
                                    </option>
                                </select>
                                <div class="form-text">Only employees (not PMs) are listed.</div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-medium">Select Course</label>
                                <select v-model="assignForm.course_id" class="form-select" required>
                                    <option value="" disabled>Choose a course...</option>
                                    <option v-for="course in courses" :key="course.id" :value="course.id">
                                        {{ course.course_name }}
                                    </option>
                                </select>
                            </div>
                            <div class="d-flex justify-content-end pt-2">
                                <button type="button" class="btn btn-secondary me-2"
                                    @click="closeAssignModal">Cancel</button>
                                <button type="submit" class="btn btn-primary shadow-sm">
                                    Assign Course
                                </button>
                            </div>
                        </form>
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
import bootstrap from "bootstrap/dist/js/bootstrap.bundle";

export default {
    name: "HRCourses",
    data() {
        return {
            courses: [],
            employees: [],
            loading: false,
            isEditing: false,
            modalInstance: null,
            assignModalInstance: null,
            form: {
                id: null,
                course_name: "",
                course_link: "",
                topics: ""
            },
            assignForm: {
                employee_id: "",
                course_id: ""
            }
        };
    },
    setup() {
        return { notify: useNotify() };
    },
    mounted() {
        this.modalInstance = new bootstrap.Modal(this.$refs.modal);
        this.assignModalInstance = new bootstrap.Modal(this.$refs.assignModal);
        this.fetchCourses();
    },
    methods: {
        truncate(str, n) {
            if (!str) return "";
            return (str.length > n) ? str.substr(0, n - 1) + '...' : str;
        },
        async fetchCourses() {
            this.loading = true;
            try {
                const data = await make_getrequest("/api/hr/course");
                this.courses = data || [];
            } catch (error) {
                console.error("Error fetching courses:", error);
                this.notify.error("Failed to load courses");
            } finally {
                this.loading = false;
            }
        },
        async fetchEmployees() {
            try {
                const res = await make_getrequest("/api/hr/employees");
                this.employees = (res.employees || []).filter(e => (e.role || "").toLowerCase() === "employee");
            } catch (error) {
                console.error("Error fetching employees:", error);
                this.notify.error("Failed to load employees list");
            }
        },
        openModal(course = null) {
            if (course) {
                this.isEditing = true;
                this.form.id = course.id;
                this.form.course_name = course.course_name;
                this.form.course_link = course.course_link;
                this.form.topics = course.topics;
            } else {
                this.isEditing = false;
                this.form.id = null;
                this.form.course_name = "";
                this.form.course_link = "";
                this.form.topics = "";
            }
            this.modalInstance.show();
        },
        closeModal() {
            this.modalInstance.hide();
            this.form = { id: null, course_name: "", course_link: "", topics: "" };
            this.isEditing = false;
        },
        openAssignModal() {
            this.assignForm = { employee_id: "", course_id: "" };
            this.fetchEmployees();
            this.assignModalInstance.show();
        },
        closeAssignModal() {
            this.assignModalInstance.hide();
            this.assignForm = { employee_id: "", course_id: "" };
        },
        async submitAssignment() {
            const { employee_id, course_id } = this.assignForm;
            if (!employee_id || !course_id) {
                this.notify.error("Please select both an employee and a course.");
                return;
            }

            try {
                await make_postrequest(`/api/hr/course/assign/${employee_id}`, { course_id });
                this.notify.success("Course assigned successfully");
                this.closeAssignModal();
            } catch (error) {
                console.error("Error assigning course:", error);
                const msg = error.response?.data?.detail || "Failed to assign course";
                this.notify.error(msg);
            }
        },
        async submitForm() {
            try {
                if (this.isEditing) {
                    await make_putrequest(`/api/hr/course/${this.form.id}`, {
                        course_name: this.form.course_name,
                        course_link: this.form.course_link,
                        topics: this.form.topics
                    });
                    this.notify.success("Course updated successfully");
                } else {
                    await make_postrequest("/api/hr/course", {
                        course_name: this.form.course_name,
                        course_link: this.form.course_link,
                        topics: this.form.topics
                    });
                    this.notify.success("Course created successfully");
                }
                this.closeModal();
                this.fetchCourses();
            } catch (error) {
                console.error("Error submitting course:", error);
                this.notify.error("Failed to save course");
            }
        },
        async confirmDelete(course) {
            const result = await Swal.fire({
                title: "Are you sure?",
                text: "Do you really want to delete this course?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#dc3545",
                cancelButtonColor: "#6c757d",
                confirmButtonText: "Yes, delete it!"
            });

            if (result.isConfirmed) {
                try {
                    await make_deleterequest(`/api/hr/course/${course.id}`);
                    this.notify.success("Course deleted.");
                    this.fetchCourses();
                } catch (error) {
                    console.error("Error deleting course:", error);
                    this.notify.error("Failed to delete course");
                }
            }
        }
    }
};
</script>

<style scoped>
.course-card {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.course-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 1rem 3rem rgba(0, 0, 0, .10) !important;
}

.bg-primary-subtle {
    background-color: rgba(13, 110, 253, 0.1);
}

.border-dashed {
    border-style: dashed !important;
}
</style>
