import { useEffect, useState } from "react";
import api from "../api/client";
import Alert from "../components/Alert";
import Avatar from "../components/Avatar";
import Button from "../components/Button";
import ChatBot from "../components/ChatBot";
import Navbar from "../components/Navbar";
import PhotoUploader from "../components/PhotoUploader";
import { PageSpinner } from "../components/Spinner";
import StudentForm from "../components/StudentForm";
import { getErrorMessage } from "../utils/errors";

function formatDate(value) {
  return new Date(`${value}T00:00:00`).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function Stat({ label, value }) {
  return (
    <div className="rounded-xl bg-slate-50 p-4 ring-1 ring-slate-200">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-xl font-semibold text-slate-900">{value}</p>
    </div>
  );
}

export default function Dashboard() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [photoVersion, setPhotoVersion] = useState(0);

  useEffect(() => {
    let ignore = false;

    async function load() {
      try {
        const { data } = await api.get("/students/me");
        if (!ignore) setProfile(data);
      } catch (err) {
        if (err.response?.status !== 404 && !ignore) {
          setError(getErrorMessage(err));
        }
      } finally {
        if (!ignore) setLoading(false);
      }
    }

    load();
    return () => {
      ignore = true;
    };
  }, []);

  async function handleSave(values) {
    const isNew = !profile;
    setSaving(true);
    setError("");
    setSuccess("");
    try {
      const { data } = isNew
        ? await api.post("/students/me", values)
        : await api.put("/students/me", values);
      setProfile(data);
      setEditing(false);
      setSuccess(isNew ? "Profile created successfully." : "Profile updated successfully.");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  async function uploadPhoto(file) {
    const form = new FormData();
    form.append("file", file);
    const { data } = await api.put("/students/me/photo", form);
    setProfile(data);
    setPhotoVersion((v) => v + 1);
  }

  async function removePhoto() {
    const { data } = await api.delete("/students/me/photo");
    setProfile(data);
    setPhotoVersion((v) => v + 1);
  }

  const showForm = editing || !profile;

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />

      <main className="mx-auto max-w-4xl px-4 py-10 sm:px-6">
        {loading ? (
          <PageSpinner />
        ) : (
          <div className="space-y-6">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-slate-900">
                {profile ? "My profile" : "Complete your profile"}
              </h1>
              <p className="mt-1 text-sm text-slate-600">
                {profile
                  ? "Your details as they appear in the school records."
                  : "Add your details to finish setting up your account. Your assistant will be ready right after."}
              </p>
            </div>

            <Alert>{error}</Alert>
            <Alert type="success">{success}</Alert>

            {showForm ? (
              <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200 sm:p-8">
                <StudentForm
                  initial={profile}
                  saving={saving}
                  submitLabel={profile ? "Save changes" : "Create profile"}
                  onSubmit={handleSave}
                  onCancel={profile ? () => setEditing(false) : undefined}
                />
              </div>
            ) : (
              <div className="overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-200">
                <div className="h-24 bg-linear-to-r from-indigo-600 to-indigo-400" />
                <div className="px-6 pb-8 sm:px-8">
                  <div className="-mt-10 flex items-end justify-between gap-4">
                    <Avatar
                      url="/students/me/photo"
                      hasPhoto={profile.has_photo}
                      version={photoVersion}
                      name={profile.name}
                      className="h-20 w-20 text-2xl shadow-md ring-4 ring-white"
                    />
                    <Button
                      variant="secondary"
                      onClick={() => {
                        setSuccess("");
                        setEditing(true);
                      }}
                    >
                      Edit profile
                    </Button>
                  </div>

                  <h2 className="mt-4 text-2xl font-bold text-slate-900">{profile.name}</h2>
                  <p className="text-sm text-slate-500">{profile.class_name}</p>

                  <div className="mt-6 grid gap-4 sm:grid-cols-3">
                    <Stat label="CGPA" value={profile.cgpa.toFixed(2)} />
                    <Stat label="Class" value={profile.class_name} />
                    <Stat label="Started" value={formatDate(profile.start_date)} />
                  </div>

                  <div className="mt-6">
                    <h3 className="text-sm font-semibold text-slate-900">About</h3>
                    <p className="mt-1 whitespace-pre-line text-sm text-slate-600">
                      {profile.description || "No description added yet."}
                    </p>
                  </div>

                  <div className="mt-8 border-t border-slate-200 pt-6">
                    <h3 className="text-sm font-semibold text-slate-900">Profile photo</h3>
                    <div className="mt-3">
                      <PhotoUploader
                        hasPhoto={profile.has_photo}
                        onUpload={uploadPhoto}
                        onRemove={removePhoto}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {profile && <ChatBot />}
    </div>
  );
}