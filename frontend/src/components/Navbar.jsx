import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Button from "./Button";
import Logo from "./Logo";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 text-white">
            <Logo className="h-5 w-5" />
          </span>
          <span className="text-lg font-bold tracking-tight text-slate-900">SchoolHub</span>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden text-right sm:block">
            <p className="text-sm font-medium text-slate-900">{user?.email}</p>
            <p className="text-xs capitalize text-slate-500">{user?.role}</p>
          </div>
          <Button variant="secondary" onClick={handleLogout}>
            Sign out
          </Button>
        </div>
      </div>
    </header>
  );
}