import Logo from "./Logo";

export default function AuthLayout({ title, subtitle, footer, children }) {
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="hidden flex-col justify-between bg-linear-to-br from-indigo-600 via-indigo-700 to-slate-900 p-12 text-white lg:flex">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/15">
            <Logo className="h-6 w-6" />
          </span>
          <span className="text-xl font-bold tracking-tight">SchoolHub</span>
        </div>

        <div>
          <h2 className="text-4xl font-bold leading-tight">
            Student records, managed simply and securely.
          </h2>
          <p className="mt-4 max-w-md text-indigo-100">
            Create your profile, keep your details up to date, and let administrators
            manage records, all in one place.
          </p>
        </div>

        <p className="text-sm text-indigo-200">
          © {new Date().getFullYear()} SchoolHub. All rights reserved.
        </p>
      </div>

      <div className="flex items-center justify-center bg-slate-50 px-6 py-12">
        <div className="w-full max-w-md">
          <div className="mb-8 flex items-center gap-2.5 lg:hidden">
            <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 text-white">
              <Logo className="h-5 w-5" />
            </span>
            <span className="text-lg font-bold text-slate-900">SchoolHub</span>
          </div>

          <h1 className="text-3xl font-bold tracking-tight text-slate-900">{title}</h1>
          <p className="mt-2 text-sm text-slate-600">{subtitle}</p>

          <div className="mt-8 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200 sm:p-8">
            {children}
          </div>

          <p className="mt-6 text-center text-sm text-slate-600">{footer}</p>
        </div>
      </div>
    </div>
  );
}