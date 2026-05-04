import React from "react";

interface DashboardPageContentProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
}

const DashboardPageContent: React.FC<DashboardPageContentProps> = ({
  children,
  title,
  subtitle,
}) => {
  return (
    <section className="w-full rounded-2xl border border-slate-200 bg-white shadow-sm px-8 py-6">
      <div className="flex flex-col gap-px">
        {title && <h1 className="font-bold text-lg">{title}</h1>}
        {subtitle && <p className="text-gray-500 text-xs">{subtitle}</p>}
      </div>
      {(title || subtitle) && (
        <hr className="mt-3.5 mb-5 border border-slate-200" />
      )}
      <div>{children}</div>
    </section>
  );
};

export default DashboardPageContent;
