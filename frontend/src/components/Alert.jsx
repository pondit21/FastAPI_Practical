const styles = {
  error: "bg-red-50 text-red-800 ring-red-200",
  success: "bg-emerald-50 text-emerald-800 ring-emerald-200",
};

export default function Alert({ type = "error", children }) {
  if (!children) return null;
  return (
    <div role="alert" className={`rounded-lg px-4 py-3 text-sm ring-1 ${styles[type]}`}>
      {children}
    </div>
  );
}