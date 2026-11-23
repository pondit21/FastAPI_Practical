export function getErrorMessage(error) {
  if (error?.code === "ERR_NETWORK") {
    return "Cannot reach the server. Please check that the backend is running.";
  }

  const detail = error?.response?.data?.detail;

  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const field = item.loc?.[item.loc.length - 1];
        return field ? `${field}: ${item.msg}` : item.msg;
      })
      .join(". ");
  }

  return "Something went wrong. Please try again.";
}