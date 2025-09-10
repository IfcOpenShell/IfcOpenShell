import { toast } from "svelte-sonner";

/**
 * Show an error toast notification
 * @param {string} message - The error message to display
 */
export function error(message) {
    toast.error(message);
}

/**
 * Show a success toast notification
 * @param {string} message - The success message to display
 */
export function success(message) {
    toast.success(message);
}

/**
 * Show an info toast notification
 * @param {string} message - The info message to display
 */
export function info(message) {
    toast.info(message);
}

/**
 * Show a warning toast notification
 * @param {string} message - The warning message to display
 */
export function warning(message) {
    toast.warning(message);
}

/**
 * Show a loading toast notification
 * @param {string} message - The loading message to display
 * @returns {string} - Toast ID for dismissing later
 */
export function loading(message) {
    return toast.loading(message);
}

/**
 * Dismiss a specific toast
 * @param {string} toastId - The toast ID to dismiss
 */
export function dismiss(toastId) {
    toast.dismiss(toastId);
}

/**
 * Show a promise-based toast that updates based on promise state
 * @param {Promise} promise - The promise to track
 * @param {Object} messages - Messages for different states
 * @param {string} messages.loading - Loading message
 * @param {string} messages.success - Success message
 * @param {string} messages.error - Error message
 */
export function promise(promiseToTrack, messages) {
    return toast.promise(promiseToTrack, {
        loading: messages.loading,
        success: messages.success,
        error: messages.error,
    });
}