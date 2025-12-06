<template>
    <div class="container py-4" style="max-width: 850px;">
        <section class="card border-0 shadow-sm mb-4">
            <div class="card-body p-4 d-flex align-items-center gap-4 flex-wrap flex-sm-nowrap">
                <div class="avatar flex-shrink-0">
                    <img v-if="user.img_base64" :src="user.img_base64" alt="Profile"
                        class="avatar-img rounded-circle" />
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

        <div class="d-flex justify-content-between align-items-center">
            <button class="btn btn-primary px-4" @click="updateProfile" :disabled="loading">
                Update
            </button>
            <button class="btn btn-danger px-4" @click="logout" :disabled="loading">
                Logout
            </button>
        </div>
    </div>
</template>

<script>
import { make_getrequest, make_putrequest } from "@/store/appState.js";
import { useNotify } from "@/utils/useNotify.js";
import Swal from 'sweetalert2';

export default {
    name: "HRAccount",
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
        this.fetchAccount();
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
