export type InputType = "topic" | "transcript" | "news";

export interface Hook {
  id: string;
  style: "curiosity_gap" | "bold_claim" | "specific_story";
  text: string;
}

export interface Post {
  id: string;
  hook: string;
  body: string;
  status: "draft" | "scheduled" | "published";
  createdAt: string;
  scheduledAt?: string;
  bufferPostId?: string;
}

export type DashboardStep = "input" | "hooks" | "preview" | "scheduled";
