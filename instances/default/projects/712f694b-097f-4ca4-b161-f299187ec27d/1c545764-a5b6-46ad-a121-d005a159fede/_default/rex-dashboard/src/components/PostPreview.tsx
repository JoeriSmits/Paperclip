"use client";

import { useState } from "react";

interface PostPreviewProps {
  content: string;
  onEdit: (content: string) => void;
  onSchedule: () => void;
  onBack: () => void;
  scheduling: boolean;
}

export default function PostPreview({
  content,
  onEdit,
  onSchedule,
  onBack,
  scheduling,
}: PostPreviewProps) {
  const [editing, setEditing] = useState(false);
  const [editContent, setEditContent] = useState(content);

  function handleSave() {
    onEdit(editContent);
    setEditing(false);
  }

  const displayContent = editing ? editContent : content;
  const charCount = displayContent.length;
  const charWarning = charCount > 3000;

  return (
    <div className="space-y-4">
      {/* LinkedIn-style preview */}
      <div className="bg-surface border border-border rounded-lg overflow-hidden">
        {/* Header */}
        <div className="flex items-center gap-3 p-4 pb-2">
          <div className="w-10 h-10 rounded-full bg-accent/20 flex items-center justify-center text-accent font-bold text-sm">
            J
          </div>
          <div>
            <p className="text-sm font-semibold text-foreground">Joeri Smits</p>
            <p className="text-xs text-muted">Just now</p>
          </div>
        </div>

        {/* Body */}
        <div className="px-4 pb-4">
          {editing ? (
            <textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              rows={12}
              className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-foreground resize-y focus:border-accent focus:ring-0"
            />
          ) : (
            <div className="text-sm text-foreground whitespace-pre-wrap leading-relaxed">
              {content}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-4 py-3 border-t border-border">
          <span className={`text-xs ${charWarning ? "text-warning" : "text-muted"}`}>
            {charCount.toLocaleString()} / 3,000 chars
          </span>
          <div className="flex items-center gap-2 text-xs text-muted">
            <span>Like</span>
            <span>Comment</span>
            <span>Repost</span>
            <span>Send</span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onBack}
          className="px-4 py-2 text-sm text-muted hover:text-foreground transition-colors"
        >
          Back to hooks
        </button>

        {editing ? (
          <button
            type="button"
            onClick={handleSave}
            className="px-4 py-2 text-sm bg-surface border border-border rounded-lg hover:bg-surface-hover transition-colors"
          >
            Save edits
          </button>
        ) : (
          <button
            type="button"
            onClick={() => setEditing(true)}
            className="px-4 py-2 text-sm bg-surface border border-border rounded-lg hover:bg-surface-hover transition-colors"
          >
            Edit
          </button>
        )}

        <button
          type="button"
          onClick={onSchedule}
          disabled={scheduling || editing}
          className="ml-auto px-6 py-2.5 bg-accent text-slate-900 font-medium rounded-lg hover:bg-cyan-300 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          {scheduling ? "Scheduling..." : "Push to Buffer"}
        </button>
      </div>
    </div>
  );
}
