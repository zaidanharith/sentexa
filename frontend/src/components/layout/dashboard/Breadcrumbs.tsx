"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

type DashboardNavItem = {
  label: string;
  href: string;
  badge?: string;
};

function toLabel(segment: string, segmentLabels: Record<string, string>) {
  if (segmentLabels[segment]) {
    return segmentLabels[segment];
  }

  return segment
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export default function Breadcrumbs({
  navItems,
}: {
  navItems: DashboardNavItem[];
}) {
  const pathname = usePathname();
  const segments = pathname.split("/").filter(Boolean);
  const segmentLabels = navItems.reduce<Record<string, string>>(
    (acc, item) => {
      const parts = item.href.split("/").filter(Boolean);
      const segment = parts[parts.length - 1];

      if (segment) {
        acc[segment] = item.label;
      }

      return acc;
    },
    {
      settings: "Pengaturan",
      help: "Bantuan",
    },
  );

  const crumbs = segments.map((segment, index) => {
    const href = `/${segments.slice(0, index + 1).join("/")}`;

    return {
      href,
      label: toLabel(segment, segmentLabels),
      isLast: index === segments.length - 1,
    };
  });

  return (
    <nav aria-label="Breadcrumb" className="w-full overflow-x-auto">
      <ol className="flex items-center gap-2 text-sm whitespace-nowrap text-gray-500">
        {crumbs.map((crumb) => (
          <li key={crumb.href} className="flex items-center gap-2">
            {crumb.isLast ? (
              <span className="font-semibold text-gray-800">{crumb.label}</span>
            ) : (
              <Link
                href={crumb.href}
                className="hover:text-sky-500 transition-colors"
              >
                {crumb.label}
              </Link>
            )}
            {!crumb.isLast ? <span className="text-gray-300">/</span> : null}
          </li>
        ))}
      </ol>
    </nav>
  );
}
