import { toast } from "vue3-toastify";
import "vue3-toastify/dist/index.css";

export function useNotify() {
    return {
        success: (msg, options = {}) =>
            toast.success(msg, {...options }),

        error: (msg, options = {}) =>
            toast.error(msg, {...options }),

        info: (msg, options = {}) =>
            toast.info(msg, {...options }),

        warn: (msg, options = {}) =>
            toast.warn(msg, {...options }),

        custom: (msg, options = {}) =>
            toast(msg, {...options }),
    };
}