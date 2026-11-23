import { useEffect, useRef, useState } from "react";
import api from "../api/client";
import { getErrorMessage } from "../utils/errors";
import Logo from "./Logo";

export default function ChatBot() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const listRef = useRef(null);

  // শুরুর শুভেচ্ছা ও সাজেশনের প্রশ্ন আনা
  useEffect(() => {
    let ignore = false;
    api
      .get("/bot/topics")
      .then(({ data }) => {
        if (ignore) return;
        setMessages([{ role: "bot", text: data.greeting }]);
        setSuggestions(data.suggestions);
      })
      .catch(() => {
        if (!ignore) {
          setMessages([{ role: "bot", text: "Hi! Ask me a question about your profile." }]);
        }
      });
    return () => {
      ignore = true;
    };
  }, []);

  // নতুন বার্তা এলে নিচে স্ক্রল
  useEffect(() => {
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, sending, open]);

  async function send(text) {
    const question = text.trim();
    if (!question || sending) return;

    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setInput("");
    setSending(true);
    try {
      const { data } = await api.post("/bot/ask", { question });
      setMessages((prev) => [...prev, { role: "bot", text: data.answer }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "bot", text: getErrorMessage(err) }]);
    } finally {
      setSending(false);
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    send(input);
  }

  return (
    <>
      {open && (
        <div className="fixed bottom-24 right-4 z-40 flex h-[32rem] max-h-[calc(100vh-8rem)] w-[calc(100vw-2rem)] max-w-sm flex-col overflow-hidden rounded-2xl bg-white shadow-xl ring-1 ring-slate-200 sm:right-6">
          <div className="flex items-center justify-between bg-indigo-600 px-4 py-3 text-white">
            <div className="flex items-center gap-3">
              <span className="flex h-9 w-9 items-center justify-center rounded-full bg-white/15">
                <Logo className="h-5 w-5" />
              </span>
              <div>
                <p className="text-sm font-semibold leading-tight">SchoolHub Assistant</p>
                <p className="flex items-center gap-1.5 text-xs text-indigo-100">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  Online
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setOpen(false)}
              aria-label="Close chat"
              className="rounded-lg p-1.5 text-indigo-100 hover:bg-white/10"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="h-5 w-5">
                <path d="M18 6 6 18" />
                <path d="m6 6 12 12" />
              </svg>
            </button>
          </div>

          <div ref={listRef} className="flex-1 space-y-3 overflow-y-auto bg-slate-50 p-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`max-w-[85%] whitespace-pre-line rounded-2xl px-3.5 py-2.5 text-sm ${
                  message.role === "user"
                    ? "ml-auto rounded-br-md bg-indigo-600 text-white"
                    : "rounded-bl-md bg-white text-slate-800 ring-1 ring-slate-200"
                }`}
              >
                {message.text}
              </div>
            ))}
            {sending && (
              <div className="w-fit animate-pulse rounded-2xl rounded-bl-md bg-white px-3.5 py-2.5 text-sm text-slate-500 ring-1 ring-slate-200">
                Typing…
              </div>
            )}
          </div>

          {suggestions.length > 0 && (
            <div className="flex gap-2 overflow-x-auto border-t border-slate-200 bg-white px-3 py-2">
              {suggestions.map((question) => (
                <button
                  key={question}
                  type="button"
                  disabled={sending}
                  onClick={() => send(question)}
                  className="shrink-0 rounded-full bg-indigo-50 px-3 py-1.5 text-xs font-medium text-indigo-700 ring-1 ring-indigo-200 hover:bg-indigo-100 disabled:opacity-60"
                >
                  {question}
                </button>
              ))}
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex gap-2 border-t border-slate-200 bg-white p-3">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              maxLength={300}
              placeholder="Type your question..."
              className="min-w-0 flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 focus:outline-none"
            />
            <button
              type="submit"
              disabled={sending || !input.trim()}
              aria-label="Send"
              className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5">
                <path d="m22 2-7 20-4-9-9-4Z" />
                <path d="M22 2 11 13" />
              </svg>
            </button>
          </form>
        </div>
      )}

      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-label={open ? "Close assistant" : "Open assistant"}
        className="fixed bottom-4 right-4 z-40 flex h-14 w-14 items-center justify-center rounded-full bg-indigo-600 text-white shadow-lg transition hover:bg-indigo-700 sm:right-6"
      >
        {open ? (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="h-6 w-6">
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        ) : (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6">
            <path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z" />
          </svg>
        )}
      </button>
    </>
  );
}