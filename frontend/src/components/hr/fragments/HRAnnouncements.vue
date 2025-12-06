<template>
    <div class="hr-announcements">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h5 class="mb-0 text-secondary fw-bold">Recent Announcements</h5>
            <button class="btn btn-primary btn-sm shadow-sm" @click="openModal()">
                <i class="bi bi-plus-lg me-1"></i> New Announcement
            </button>
        </div>

        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>

        <div v-else-if="announcements.length === 0" class="text-center py-5 bg-light rounded-3 border border-dashed">
            <i class="bi bi- megaphone text-muted fs-1 mb-3 d-block"></i>
            <p class="text-muted mb-0">No announcements posted yet.</p>
        </div>

        <div v-else class="d-flex flex-column gap-3">
            <div v-for="ann in announcements" :key="ann.id"
                class="card shadow-sm border-0 border-start border-4 border-primary announcement-card">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <p class="mb-2 fs-6 text-dark" style="white-space: pre-line;">{{ ann.announcement }}</p>
                            <div class="d-flex align-items-center text-muted small">
                                <i class="bi bi-calendar3 me-2"></i>
                                <span>{{ formatDate(ann.created_at) }}</span>
                            </div>
                        </div>
                        <div class="dropdown ms-3">
                            <button class="btn btn-link text-muted p-0" type="button" data-bs-toggle="dropdown"
                                aria-expanded="false">
                                <i class="bi bi-three-dots-vertical"></i>
                            </button>
                            <ul class="dropdown-menu dropdown-menu-end border-0 shadow">
                                <li>
                                    <button class="dropdown-item" @click="openModal(ann)">
                                        <i class="bi bi-pencil me-2 text-primary"></i> Edit
                                    </button>
                                </li>
                                <li>
                                    <button class="dropdown-item text-danger" @click="confirmDelete(ann)">
                                        <i class="bi bi-trash me-2"></i> Delete
                                    </button>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="modal fade" id="announcementModal" tabindex="-1" ref="modal">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content border-0 shadow">
                    <div class="modal-header bg-primary text-white border-bottom-0">
                        <h5 class="modal-title fw-bold">{{ isEditing ? 'Edit' : 'Create' }} Announcement</h5>
                        <button type="button" class="btn-close btn-close-white" @click="closeModal"></button>
                    </div>
                    <div class="modal-body p-4">
                        <form @submit.prevent="submitForm">
                            <div class="mb-3">
                                <label class="form-label fw-medium">Content</label>
                                <textarea v-model="form.announcement" class="form-control bg-light" rows="5" required
                                    placeholder="Type your announcement here..."></textarea>
                                <div class="form-text">Visible to all employees immediately.</div>
                            </div>
                            <div class="d-flex justify-content-end pt-2">
                                <button type="button" class="btn btn-secondary me-2" @click="closeModal">Cancel</button>
                                <button type="submit" class="btn btn-primary shadow-sm">
                                    {{ isEditing ? 'Update Announcement' : 'Post Announcement' }}
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
    name: "HRAnnouncements",
    data() {
        return {
            announcements: [],
            loading: false,
            isEditing: false,
            modalInstance: null,
            form: {
                id: null,
                announcement: ""
            },
            currentUserId: null
        };
    },
    setup() {
        return { notify: useNotify() };
    },
    mounted() {
        this.modalInstance = new bootstrap.Modal(this.$refs.modal);
        const user = JSON.parse(localStorage.getItem("user") || "{}");
        this.currentUserId = user.id;
        this.fetchAnnouncements();
    },
    methods: {
        formatDate(dateStr) {
            if (!dateStr) return "";
            return new Date(dateStr).toLocaleString(undefined, {
                dateStyle: 'medium',
                timeStyle: 'short'
            });
        },
        async fetchAnnouncements() {
            this.loading = true;
            try {
                const data = await make_getrequest("/api/hr/annoucements");
                this.announcements = data;
            } catch (error) {
                console.error("Error fetching announcements:", error);
                this.notify.error("Failed to load announcements");
            } finally {
                this.loading = false;
            }
        },
        openModal(ann = null) {
            if (ann) {
                this.isEditing = true;
                this.form.id = ann.id;
                this.form.announcement = ann.announcement;
            } else {
                this.isEditing = false;
                this.form.id = null;
                this.form.announcement = "";
            }
            this.modalInstance.show();
        },
        closeModal() {
            this.modalInstance.hide();
            this.form = { id: null, announcement: "" };
            this.isEditing = false;
        },
        async submitForm() {
            try {
                if (this.isEditing) {
                    await make_putrequest(`/api/hr/annoucement/edit/${this.form.id}`, {
                        announcement: this.form.announcement
                    });
                    this.notify.success("Announcement updated successfully");
                } else {
                    await make_postrequest(`/api/hr/annoucement`, {
                        announcement: this.form.announcement
                    });
                    this.notify.success("Announcement posted successfully");
                }
                this.closeModal();
                this.fetchAnnouncements();
            } catch (error) {
                console.error("Error submitting announcement:", error);
                this.notify.error("Failed to save announcement");
            }
        },
        async confirmDelete(ann) {
            const result = await Swal.fire({
                title: "Are you sure?",
                text: "This will remove the announcement for all employees.",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#dc3545",
                cancelButtonColor: "#6c757d",
                confirmButtonText: "Yes, delete it!"
            });

            if (result.isConfirmed) {
                try {
                    await make_deleterequest(`/api/hr/annoucement/edit/${ann.id}`);
                    this.notify.success("Announcement deleted.");
                    this.fetchAnnouncements();
                } catch (error) {
                    console.error("Error deleting announcement:", error);
                    this.notify.error("Failed to delete announcement");
                }
            }
        }
    }
};
</script>

<style scoped>
.announcement-card {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.announcement-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 .5rem 1rem rgba(0, 0, 0, .10) !important;
}

.border-dashed {
    border-style: dashed !important;
}
</style>