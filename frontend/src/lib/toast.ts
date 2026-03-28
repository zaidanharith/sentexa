import toast, { ToastOptions } from "react-hot-toast";

const baseToastOptions: ToastOptions = {
  duration: 3600,
  style: {
    border: "1px solid #e2e8f0",
    padding: "12px 14px",
    color: "#0f172a",
    background: "#ffffff",
    boxShadow: "0 10px 30px rgba(2, 6, 23, 0.08)",
  },
};

export const appToast = {
  success(message: string, options?: ToastOptions) {
    return toast.success(message, {
      ...baseToastOptions,
      ...options,
    });
  },

  error(message: string, options?: ToastOptions) {
    return toast.error(message, {
      ...baseToastOptions,
      duration: 4200,
      ...options,
    });
  },

  warning(message: string, options?: ToastOptions) {
    return toast(message, {
      ...baseToastOptions,
      icon: "!",
      ...options,
    });
  },

  info(message: string, options?: ToastOptions) {
    return toast(message, {
      ...baseToastOptions,
      icon: "i",
      ...options,
    });
  },
};
