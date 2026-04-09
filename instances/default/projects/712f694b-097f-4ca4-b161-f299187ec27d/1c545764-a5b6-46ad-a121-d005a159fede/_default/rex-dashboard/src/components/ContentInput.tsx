"use client";

import { useState } from "react";
import type { InputType } from "@/lib/types";

const inputTypes: { value: InputType; label: string; description: string }[] = [
  { value: "topic", label: "Topic", description: "A subject or opinion to write about" },
  { value: "transcript", label: "Transcript", description: "Meeting notes or podcast transcript" },
  { value: "news", label: "News", description: "Industry news or trending topic" },
];

interface ContentInputProps {
  onSubmit: (content: string, type: InputType) => void;
  loading: boolean;
}

export default function ContentInput({ onSubmit, loading }: ContentInputProps) {
  const [content, setContent] = useState("");
  const [type, setType] = useState<InputType>("topic");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!content.trim()) return;
    onSubmit(content.trim(), type);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div className="flex gap-2">
        {inputTypes.map((t) => (
          <button
            key={t.value}
            type="button"
            onClick={() => setType(t.value)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              type === t.value
                ? "bg-accent text-slate-900"
                : "bg-surface text-muted hover:bg-surface-hover hover:text-foreground"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <p className="text-sm text-muted">
        {inputTypes.find((t) => t.value === type)?.description}
      </p>

      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder={
          type === "topic"
            ? "What do you want to write about?"
            : type === "transcript"
            ? "Paste your transcript here..."
            : "Paste the news article or link..."
        }
        rows={6}
        className="w-full bg-surface border border-border rounded-lg px-4 py-3 text-foreground placeholder:text-muted resize-y focus:border-accent focus:ring-0 transition-colors"
      />

      <button
        type="submit"
        disabled={loading || !content.trim()}
        className="px-6 py-2.5 bg-accent text-slate-900 font-medium rounded-lg hover:bg-cyan-300 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? "Generating hooks..." : "Generate hooks"}
      </button>
    </form>
  );
}
