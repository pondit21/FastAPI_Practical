import { useRef, useState } from "react";
import { getErrorMessage } from "../utils/errors";
import Button from "./Button";

const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"];
const MAX_BYTES = 5 * 1024 * 1024;

export default function PhotoUploader({ hasPhoto, onUpload, onRemove }) {
  const inputRef = useRef(null);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState("");

  async function run(action) {
    setWorking(true);
    setError("");
    try {
      await action();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setWorking(false);
    }
  }

  function handleFile(e) {
    const file = e.target.files?.[0];
    e.target.value = ""; // একই ফাইল আবার বাছাই করা যাবে
    if (!file) return;

    if (!ALLOWED_TYPES.includes(file.type)) {
      setError("Please choose a JPG, PNG or WebP image.");
      return;
    }
    if (file.size > MAX_BYTES) {
      setError("Image must be 5 MB or smaller.");
      return;
    }
    run(() => onUpload(file));
  }

  return (
    <div>
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={handleFile}
      />
      <div className="flex flex-wrap gap-2">
        <Button
          variant="secondary"
          size="sm"
          loading={working}
          onClick={() => inputRef.current?.click()}
        >
          Change photo
        </Button>
        {hasPhoto && (
          <Button variant="secondary" size="sm" disabled={working} onClick={() => run(onRemove)}>
            Remove
          </Button>
        )}
      </div>
      {error && <p className="mt-2 text-xs text-red-600">{error}</p>}
      <p className="mt-2 text-xs text-slate-500">JPG, PNG or WebP, up to 5 MB.</p>
    </div>
  );
}