import React from "react";

interface DashboardPageTitleProps {
  title: string;
  subtitle?: string;
  isPremiumOnly?: boolean;
}

const DashboardPageTitle: React.FC<DashboardPageTitleProps> = ({
  title,
  subtitle,
  isPremiumOnly = false,
}) => {
  return (
    <section
      className={`w-full rounded-2xl border border-slate-200 bg-white shadow-sm px-8 py-4 flex flex-col gap-1 ${isPremiumOnly ? "border-yellow-500 bg-yellow-50" : ""}`}
    >
      <h1 className="font-bold text-2xl">{title}</h1>
      {subtitle && <p className="text-gray-500 text-sm">{subtitle}</p>}
    </section>
  );
};

export default DashboardPageTitle;
