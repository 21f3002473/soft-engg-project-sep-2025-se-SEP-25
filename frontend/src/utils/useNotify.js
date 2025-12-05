import { toast } from "vue3-toastify";
import "vue3-toastify/dist/index.css";

export function useNotify() {
    return {
        success: (msg, options = {}) =>
            toast.success(msg, { autoClose: 3000, ...options }),

        error: (msg, options = {}) =>
            toast.error(msg, { autoClose: 3000, ...options }),

        info: (msg, options = {}) =>
            toast.info(msg, { autoClose: 3000, ...options }),

        warn: (msg, options = {}) =>
            toast.warn(msg, { autoClose: 3000, ...options }),

        custom: (msg, options = {}) =>
            toast(msg, { autoClose: 3000, ...options }),
    };
}