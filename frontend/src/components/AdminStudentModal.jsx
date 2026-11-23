import { useState } from "react";
import api from "../api/client";
import { getErrorMessage } from "../utils/errors";
import Alert from "./Alert";
import Avatar from "./Avatar";
import Modal from "./Modal";
import PhotoUploader from "./PhotoUploader";
import StudentForm from "./StudentForm";

// student = null হলে নতুন student যোগ, নইলে এডিট
export default function AdminStudentModal({ student, onClose, onSaved, onChanged }) {
  const isEdit = Boolean(student);
  const [current, setCurrent] = useState(student);
  const [photoVersion, setPhotoVersion] = useState(0);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(values) {
    setSaving(true);
    setError("");
    try {
      if (isEdit) {
        await api.put(`/students/${student.id}`, values);
        onSaved(`${values.name}'s details were updated.`);
      } else {
        const { data } = await api.post("/students", values);
        onSaved(
          `Account created for ${data.email}. Share the email and temporary password with the student.`
        );
      }
    } catch (err) {
      setError(getErrorMessage(err));
      setSaving(false);
    }
  }

  async function uploadPhoto(file) {
    const form = new FormData();
    form.append("file", file);
    const { data } = await api.put(`/students/${student.id}/photo`, form);
    setCurrent(data);
    setPhotoVersion((v) => v + 1);
    onChanged();
  }

  async function removePhoto() {
    const { data } = await api.delete(`/students/${student.id}/photo`);
    setCurrent(data);
    setPhotoVersion((v) => v + 1);
    onChanged();
  }

  return (
    <Modal title={isEdit ? "Edit student" : "Add student"} onClose={onClose}>
      <div className="space-y-6">
        <Alert>{error}</Alert>

        {isEdit ? (
          <div className="flex items-center gap-4 rounded-xl bg-slate-50 p-4 ring-1 ring-slate-200">
            <Avatar
              url={`/students/${student.id}/photo`}
              hasPhoto={current.has_photo}
              version={photoVersion}
              name={current.name}
              className="h-16 w-16 text-xl"
            />
            <div className="min-w-0">
              <p className="truncate text-sm font-medium text-slate-900">{student.email}</p>
              <div className="mt-2">
                <PhotoUploader
                  hasPhoto={current.has_photo}
                  onUpload={uploadPhoto}
                  onRemove={removePhoto}
                />
              </div>
            </div>
          </div>
        ) : (
          <p className="rounded-lg bg-indigo-50 px-4 py-3 text-sm text-indigo-800 ring-1 ring-indigo-100">
            This creates a student account and profile together. You can add a photo afterwards
            by choosing Edit on the student.
          </p>
        )}

        <StudentForm
          initial={student}
          withAccount={!isEdit}
          saving={saving}
          submitLabel={isEdit ? "Save changes" : "Create student"}
          onSubmit={handleSubmit}
          onCancel={onClose}
        />
      </div>
    </Modal>
  );
}