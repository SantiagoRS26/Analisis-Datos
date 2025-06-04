import { CheckCircle, XCircle, AlertCircle, Clock } from "lucide-react";

interface StatusBadgeProps {
  status: 'success' | 'error' | 'warning' | 'loading';
  children: React.ReactNode;
}

export function StatusBadge({ status, children }: StatusBadgeProps) {
  const variants = {
    success: {
      icon: CheckCircle,
      className: "bg-green-100 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800"
    },
    error: {
      icon: XCircle,
      className: "bg-red-100 text-red-800 border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800"
    },
    warning: {
      icon: AlertCircle,
      className: "bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-400 dark:border-yellow-800"
    },
    loading: {
      icon: Clock,
      className: "bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/20 dark:text-blue-400 dark:border-blue-800"
    }
  };

  const variant = variants[status];
  const Icon = variant.icon;

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full border text-sm font-medium ${variant.className}`}>
      <Icon className="w-4 h-4" />
      {children}
    </div>
  );
}
