import React from "react";

interface DashboardPageContentProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  line?: boolean;
}

const DashboardPageContent: React.FC<DashboardPageContentProps> = ({
  children,
  className = "",
  title,
  subtitle,
  line = true,
}) => {
  return (
    <section
      className={`w-full rounded-2xl border border-slate-200 bg-white shadow-sm px-8 py-6 ${className}`}
    >
      <div className="flex flex-col gap-px">
        {title && <h1 className="font-bold text-lg">{title}</h1>}
        {subtitle && <p className="text-gray-500 text-xs">{subtitle}</p>}
      </div>
      {(title || subtitle) && line && (
        <hr className="mt-3.5 mb-5 border border-slate-200" />
      )}
      <div>{children}</div>
    </section>
  );
};

export default DashboardPageContent;
