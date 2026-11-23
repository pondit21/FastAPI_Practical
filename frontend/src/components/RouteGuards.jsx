import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { PageSpinner } from "./Spinner";

const homePath = (user) => (user.role === "admin" ? "/admin" : "/dashboard");

// শুধু লগইন করা (এবং ঠিক role-এর) ইউজারদের জন্য
export function ProtectedRoute({ role, children }) {
  const { user, loading } = useAuth();

  if (loading) return <PageSpinner />;
  if (!user) return <Navigate to="/login" replace />;
  if (role && user.role !== role) return <Navigate to={homePath(user)} replace />;

  return children;
}

// লগইন/রেজিস্টার পেজ: লগইন করা থাকলে ঢুকতে দেবে না
export function GuestRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) return <PageSpinner />;
  if (user) return <Navigate to={homePath(user)} replace />;

  return children;
}

// "/" এ এলে role অনুযায়ী পাঠায়
export function HomeRedirect() {
  const { user, loading } = useAuth();

  if (loading) return <PageSpinner />;
  if (!user) return <Navigate to="/login" replace />;

  return <Navigate to={homePath(user)} replace />;
}