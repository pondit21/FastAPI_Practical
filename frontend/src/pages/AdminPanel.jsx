import { useEffect, useState } from "react";
import api from "../api/client";
import AdminStudentModal from "../components/AdminStudentModal";
import Alert from "../components/Alert";
import Avatar from "../components/Avatar";
import Button from "../components/Button";
import ConfirmModal from "../components/ConfirmModal";
import Navbar from "../components/Navbar";
import { PageSpinner } from "../components/Spinner";
import { getErrorMessage } from "../utils/errors";

const PAGE_SIZE = 10;

function formatDate(value) {
  return new Date(`${value}T00:00:00`).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function CgpaBadge({ value }) {
  const color =
    value >= 3.5
      ? "bg-emerald-50 text-emerald-700 ring-emerald-200"
      : value >= 3
        ? "bg-indigo-50 text-indigo-700 ring-indigo-200"
        : "bg-amber-50 text-amber-700 ring-amber-200";
  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ${color}`}>
      {value.toFixed(2)}
    </span>
  );
}

export default function AdminPanel() {
  const [students, setStudents] = useState([]);
  const [hasNext, setHasNext] = useState(false);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [query, setQuery] = useState("");
  const [modal, setModal] = useState(null); // null | { student: null } | { student: {...} }
  const [toDelete, setToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let ignore = false;

    async function load() {
      setLoading(true);
      try {
        const { data } = await api.get("/students", {
          params: { skip: page * PAGE_SIZE, limit: PAGE_SIZE + 1 },
        });
        if (ignore) return;

        if (data.length === 0 && page > 0) {
          setPage((p) => p - 1);
          return;
        }
        setStudents(data.slice(0, PAGE_SIZE));
        setHasNext(data.length > PAGE_SIZE);
        setError("");
      } catch (err) {
        if (!ignore) setError(getErrorMessage(err));
      } finally {
        if (!ignore) setLoading(false);
      }
    }

    load();
    return () => {
      ignore = true;
    };
  }, [page, reloadKey]);

  const reload = () => setReloadKey((k) => k + 1);

  async function confirmDelete() {
    setDeleting(true);
    try {
      await api.delete(`/students/${toDelete.id}`);
      setSuccess(`${toDelete.name}'s profile was deleted.`);
      reload();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setDeleting(false);
      setToDelete(null);
    }
  }

  function handleSaved(message) {
    setModal(null);
    setSuccess(message);
    reload();
  }

  const q = query.trim().toLowerCase();
  const visible = q
    ? students.filter((s) => `${s.name} ${s.class_name} ${s.email}`.toLowerCase().includes(q))
    : students;

  const from = page * PAGE_SIZE + 1;
  const to = page * PAGE_SIZE + students.length;

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />

      <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">Students</h1>
            <p className="mt-1 text-sm text-slate-600">
              Add students, edit their details and photos, or remove records.
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Filter this page by name, class or email"
              className="w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-sm shadow-xs placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 focus:outline-none sm:w-80"
            />
            <Button
              onClick={() => {
                setSuccess("");
                setModal({ student: null });
              }}
            >
              + Add student
            </Button>
          </div>
        </div>

        <div className="mt-6 space-y-3">
          <Alert>{error}</Alert>
          <Alert type="success">{success}</Alert>
        </div>

        <div className="mt-6 overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-200">
          {loading ? (
            <PageSpinner />
          ) : visible.length === 0 ? (
            <p className="px-6 py-16 text-center text-sm text-slate-500">
              {students.length === 0
                ? "No students yet. Use “Add student” to create the first one."
                : "No students match your filter."}
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                  <tr>
                    <th className="px-6 py-3">ID</th>
                    <th className="px-6 py-3">Student</th>
                    <th className="px-6 py-3">Class</th>
                    <th className="px-6 py-3">CGPA</th>
                    <th className="px-6 py-3">Started</th>
                    <th className="px-6 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {visible.map((s) => (
                    <tr key={s.id} className="hover:bg-slate-50">
                      <td className="px-6 py-4 text-slate-500">#{s.id}</td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <Avatar
                            url={`/students/${s.id}/photo`}
                            hasPhoto={s.has_photo}
                            version={reloadKey}
                            name={s.name}
                            className="h-10 w-10 text-sm"
                          />
                          <div className="min-w-0">
                            <p className="font-medium text-slate-900">{s.name}</p>
                            <p className="truncate text-xs text-slate-500">{s.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-slate-700">{s.class_name}</td>
                      <td className="px-6 py-4">
                        <CgpaBadge value={s.cgpa} />
                      </td>
                      <td className="px-6 py-4 text-slate-700">{formatDate(s.start_date)}</td>
                      <td className="whitespace-nowrap px-6 py-4 text-right">
                        <button
                          onClick={() => {
                            setSuccess("");
                            setModal({ student: s });
                          }}
                          className="text-sm font-semibold text-indigo-600 hover:text-indigo-700"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => setToDelete(s)}
                          className="ml-4 text-sm font-semibold text-red-600 hover:text-red-700"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {!loading && students.length > 0 && (
            <div className="flex items-center justify-between border-t border-slate-200 px-6 py-3">
              <p className="text-sm text-slate-600">
                Showing {from}–{to}
              </p>
              <div className="flex gap-2">
                <Button variant="secondary" disabled={page === 0} onClick={() => setPage((p) => p - 1)}>
                  Previous
                </Button>
                <Button variant="secondary" disabled={!hasNext} onClick={() => setPage((p) => p + 1)}>
                  Next
                </Button>
              </div>
            </div>
          )}
        </div>
      </main>

      {modal && (
        <AdminStudentModal
          key={modal.student?.id ?? "new"}
          student={modal.student}
          onClose={() => setModal(null)}
          onSaved={handleSaved}
          onChanged={reload}
        />
      )}

      <ConfirmModal
        open={Boolean(toDelete)}
        title="Delete student profile?"
        message={`This permanently removes ${toDelete?.name ?? "this student"}'s profile and photo. Their login account is kept, so they can create a new profile later.`}
        confirmLabel="Delete"
        loading={deleting}
        onConfirm={confirmDelete}
        onCancel={() => setToDelete(null)}
      />
    </div>
  );
}