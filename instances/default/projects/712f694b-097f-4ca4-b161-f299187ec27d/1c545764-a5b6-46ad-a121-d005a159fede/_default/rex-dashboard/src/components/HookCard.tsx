"use client";

import type { Hook } from "@/lib/types";

const styleLabels: Record<Hook["style"], string> = {
  curiosity_gap: "Curiosity Gap",
  bold_claim: "Bold Claim",
  specific_story: "Specific Story",
};

const styleColors: Record<Hook["style"], string> = {
  curiosity_gap: "border-accent",
  bold_claim: "border-warning",
  specific_story: "border-success",
};

interface HookCardProps {
  hook: Hook;
  selected: boolean;
  onSelect: (hook: Hook) => void;
}

export default function HookCard({ hook, selected, onSelect }: HookCardProps) {
  return (
    <button
      type="button"
      onClick={() => onSelect(hook)}
      className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
        selected
          ? `${styleColors[hook.style]} bg-accent-dim`
          : "border-border bg-surface hover:border-surface-hover hover:bg-surface-hover"
      }`}
    >
      <span
        className={`inline-block px-2 py-0.5 rounded text-xs font-medium mb-2 ${
          selected ? "bg-accent/20 text-accent" : "bg-surface-hover text-muted"
        }`}
      >
        {styleLabels[hook.style]}
      </span>
      <p className="text-foreground leading-relaxed">{hook.text}</p>
    </button>
  );
}
