import { useState } from "react";
import Button from "./Button";
import Field from "./Field";

export default function StudentForm({
  initial,
  withAccount = false,
  onSubmit,
  onCancel,
  saving,
  submitLabel,
}) {
  const [values, setValues] = useState({
    email: "",
    password: "",
    name: initial?.name ?? "",
    cgpa: initial?.cgpa ?? "",
    class_name: initial?.class_name ?? "",
    start_date: initial?.start_date ?? "",
    description: initial?.description ?? "",
  });

  function handleChange(e) {
    const { name, value } = e.target;
    setValues((prev) => ({ ...prev, [name]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    const payload = {
      name: values.name.trim(),
      cgpa: Number(values.cgpa),
      class_name: values.class_name.trim(),
      start_date: values.start_date,
      description: values.description.trim() || null,
    };
    if (withAccount) {
      payload.email = values.email.trim();
      payload.password = values.password;
    }
    onSubmit(payload);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div className="grid gap-5 sm:grid-cols-2">
        {withAccount && (
          <>
            <Field
              id="email"
              label="Student email"
              type="email"
              autoComplete="off"
              required
              placeholder="student@example.com"
              value={values.email}
              onChange={handleChange}
              className="sm:col-span-2"
            />
            <Field
              id="password"
              label="Temporary password"
              type="text"
              autoComplete="new-password"
              required
              minLength={8}
              maxLength={128}
              placeholder="At least 8 characters"
              hint="Share this with the student so they can sign in."
              value={values.password}
              onChange={handleChange}
              className="sm:col-span-2"
            />
          </>
        )}
        <Field
          id="name"
          label="Full name"
          required
          minLength={2}
          maxLength={100}
          placeholder="Rahim Uddin"
          value={values.name}
          onChange={handleChange}
          className="sm:col-span-2"
        />
        <Field
          id="class_name"
          label="Class"
          required
          maxLength={50}
          placeholder="Class 10"
          value={values.class_name}
          onChange={handleChange}
        />
        <Field
          id="cgpa"
          label="CGPA (0 – 5)"
          type="number"
          step="0.01"
          min="0"
          max="5"
          required
          placeholder="3.75"
          value={values.cgpa}
          onChange={handleChange}
        />
        <Field
          id="start_date"
          label="School starting date"
          type="date"
          required
          value={values.start_date}
          onChange={handleChange}
          className="sm:col-span-2"
        />
        <Field
          id="description"
          label="About (optional)"
          as="textarea"
          rows={4}
          maxLength={1000}
          placeholder="A few words about the student, interests, achievements..."
          value={values.description}
          onChange={handleChange}
          className="sm:col-span-2"
        />
      </div>

      <div className="flex justify-end gap-3">
        {onCancel && (
          <Button variant="secondary" onClick={onCancel} disabled={saving}>
            Cancel
          </Button>
        )}
        <Button type="submit" loading={saving}>
          {submitLabel}
        </Button>
      </div>
    </form>
  );
}