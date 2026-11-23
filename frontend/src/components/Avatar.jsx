import { useEffect, useRef, useState } from "react";
import api from "../api/client";

function initials(name = "") {
  const result = name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join("");
  return result || "?";
}

export default function Avatar({
  url,
  hasPhoto,
  version = 0,
  name = "",
  className = "h-10 w-10 text-sm",
}) {
  const [src, setSrc] = useState(null);
  const urlRef = useRef(null);

  useEffect(() => {
    if (!hasPhoto) return;
    let ignore = false;

    api
      .get(url, { responseType: "blob" })
      .then((res) => {
        if (ignore) return;
        const objectUrl = URL.createObjectURL(res.data);
        if (urlRef.current) URL.revokeObjectURL(urlRef.current);
        urlRef.current = objectUrl;
        setSrc(objectUrl);
      })
      .catch(() => {});

    return () => {
      ignore = true;
    };
  }, [url, hasPhoto, version]);

  // কম্পোনেন্ট বন্ধ হলে মেমরি পরিষ্কার
  useEffect(() => {
    return () => {
      if (urlRef.current) URL.revokeObjectURL(urlRef.current);
    };
  }, []);

  if (hasPhoto && src) {
    return <img src={src} alt={name} className={`rounded-full object-cover ${className}`} />;
  }

  return (
    <span
      className={`inline-flex shrink-0 items-center justify-center rounded-full bg-indigo-100 font-semibold text-indigo-700 ${className}`}
    >
      {initials(name)}
    </span>
  );
}