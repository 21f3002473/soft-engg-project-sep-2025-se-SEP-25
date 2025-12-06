<template>
    <div class="hr-faqs">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h5 class="mb-0 text-secondary fw-bold">Frequently Asked Questions</h5>
            <button class="btn btn-primary btn-sm shadow-sm" @click="openModal()">
                <i class="bi bi-plus-lg me-1"></i> Add FAQ
            </button>
        </div>

        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>

        <div v-else-if="faqs.length === 0" class="text-center py-5 bg-light rounded-3 border border-dashed">
            <i class="bi bi-question-circle text-muted fs-1 mb-3 d-block"></i>
            <p class="text-muted mb-0">No FAQs available.</p>
        </div>

        <div v-else class="accordion shadow-sm" id="faqAccordion">
            <div v-for="(faq, index) in faqs" :key="faq.id" class="accordion-item border-0 border-bottom">
                <h2 class="accordion-header" :id="'heading' + index">
                    <button class="accordion-button collapsed fw-medium" type="button" data-bs-toggle="collapse"
                        :data-bs-target="'#collapse' + index" aria-expanded="false" :aria-controls="'collapse' + index">
                        {{ faq.question }}
                    </button>
                </h2>
                <div :id="'collapse' + index" class="accordion-collapse collapse" :aria-labelledby="'heading' + index"
                    data-bs-parent="#faqAccordion">
                    <div class="accordion-body bg-light text-secondary">
                        <p class="mb-3" style="white-space: pre-line;">{{ faq.answer }}</p>
                        <div class="d-flex justify-content-end border-top pt-2">
                            <button class="btn btn-sm btn-link text-decoration-none me-3" @click="openModal(faq)">
                                <i class="bi bi-pencil me-1"></i> Edit
                            </button>
                            <button class="btn btn-sm btn-link text-danger text-decoration-none"
                                @click="confirmDelete(faq)">
                                <i class="bi bi-trash me-1"></i> Delete
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="modal fade" id="faqModal" tabindex="-1" ref="modal">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content border-0 shadow">
                    <div class="modal-header bg-primary text-white border-bottom-0">
                        <h5 class="modal-title fw-bold">{{ isEditing ? 'Edit' : 'Create' }} FAQ</h5>
                        <button type="button" class="btn-close btn-close-white" @click="closeModal"></button>
                    </div>
                    <div class="modal-body p-4">
                        <form @submit.prevent="submitForm">
                            <div class="mb-3">
                                <label class="form-label fw-medium">Question</label>
                                <input v-model="form.question" type="text" class="form-control" required
                                    placeholder="E.g., What is the leave policy?">
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-medium">Answer</label>
                                <textarea v-model="form.answer" class="form-control" rows="5" required
                                    placeholder="Enter the detailed answer..."></textarea>
                            </div>
                            <div class="d-flex justify-content-end pt-2">
                                <button type="button" class="btn btn-secondary me-2" @click="closeModal">Cancel</button>
                                <button type="submit" class="btn btn-primary shadow-sm">
                                    {{ isEditing ? 'Update FAQ' : 'Save FAQ' }}
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
    name: "HRFAQs",
    data() {
        return {
            faqs: [],
            loading: false,
            isEditing: false,
            modalInstance: null,
            form: {
                id: null,
                question: "",
                answer: ""
            }
        };
    },
    setup() {
        return { notify: useNotify() };
    },
    mounted() {
        this.modalInstance = new bootstrap.Modal(this.$refs.modal);
        this.fetchFAQs();
    },
    methods: {
        async fetchFAQs() {
            this.loading = true;
            try {
                const res = await make_getrequest("/api/employee/hr-faqs");
                this.faqs = res.faqs || [];
            } catch (error) {
                console.error("Error fetching FAQs:", error);
                this.notify.error("Failed to load FAQs");
            } finally {
                this.loading = false;
            }
        },
        openModal(faq = null) {
            if (faq) {
                this.isEditing = true;
                this.form.id = faq.id;
                this.form.question = faq.question;
                this.form.answer = faq.answer;
            } else {
                this.isEditing = false;
                this.form.id = null;
                this.form.question = "";
                this.form.answer = "";
            }
            this.modalInstance.show();
        },
        closeModal() {
            this.modalInstance.hide();
            this.form = { id: null, question: "", answer: "" };
            this.isEditing = false;
        },
        async submitForm() {
            try {
                if (this.isEditing) {
                    await make_putrequest(`/api/hr/faq/${this.form.id}`, {
                        question: this.form.question,
                        answer: this.form.answer
                    });
                    this.notify.success("FAQ updated successfully");
                } else {
                    await make_postrequest("/api/hr/faq", {
                        question: this.form.question,
                        answer: this.form.answer
                    });
                    this.notify.success("FAQ created successfully");
                }
                this.closeModal();
                this.fetchFAQs();
            } catch (error) {
                console.error("Error submitting FAQ:", error);
                this.notify.error("Failed to save FAQ");
            }
        },
        async confirmDelete(faq) {
            const result = await Swal.fire({
                title: "Are you sure?",
                text: "Do you really want to delete this FAQ?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#dc3545",
                cancelButtonColor: "#6c757d",
                confirmButtonText: "Yes, delete it!"
            });

            if (result.isConfirmed) {
                try {
                    await make_deleterequest(`/api/hr/faq/${faq.id}`);
                    this.notify.success("FAQ deleted.");
                    this.fetchFAQs();
                } catch (error) {
                    console.error("Error deleting FAQ:", error);
                    this.notify.error("Failed to delete FAQ");
                }
            }
        }
    }
};
</script>

<style scoped>
.accordion-button:not(.collapsed) {
    background-color: #e7f1ff;
    color: #0d6efd;
    box-shadow: none;
}

.accordion-button:focus {
    box-shadow: none;
    border-color: rgba(0, 0, 0, .125);
}

.border-dashed {
    border-style: dashed !important;
}
</style>