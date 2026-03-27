export default function DashboardFooter() {
  return (
    <footer className="border-t border-gray-200 bg-white px-6 py-3">
      <div className="flex flex-col gap-2 text-xs text-gray-500 sm:flex-row sm:items-center sm:justify-between">
        <p>© {new Date().getFullYear()} Sentexa Dashboard</p>
      </div>
    </footer>
  );
}
