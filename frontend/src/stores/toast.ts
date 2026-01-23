import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface Toast {
    id: string
    message: string
    type: ToastType
    duration?: number
}

export const useToastStore = defineStore('toast', () => {
    const toasts = ref<Toast[]>([])

    function add(message: string, type: ToastType = 'info', duration = 3000) {
        const id = Date.now().toString()
        toasts.value.push({ id, message, type, duration })

        if (duration > 0) {
            setTimeout(() => {
                remove(id)
            }, duration)
        }
    }

    function remove(id: string) {
        const index = toasts.value.findIndex((t) => t.id === id)
        if (index > -1) {
            toasts.value.splice(index, 1)
        }
    }

    function success(message: string, duration = 3000) {
        add(message, 'success', duration)
    }

    function error(message: string, duration = 5000) {
        add(message, 'error', duration)
    }

    function warning(message: string, duration = 4000) {
        add(message, 'warning', duration)
    }

    function info(message: string, duration = 3000) {
        add(message, 'info', duration)
    }

    return {
        toasts,
        add,
        remove,
        success,
        error,
        warning,
        info,
    }
})
