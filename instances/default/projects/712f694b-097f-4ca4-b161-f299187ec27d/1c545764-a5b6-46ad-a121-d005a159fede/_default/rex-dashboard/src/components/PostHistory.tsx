"use client";

import type { Post } from "@/lib/types";

const statusColors: Record<Post["status"], string> = {
  draft: "text-muted",
  scheduled: "text-accent",
  published: "text-success",
};

const statusDots: Record<Post["status"], string> = {
  draft: "bg-muted",
  scheduled: "bg-accent",
  published: "bg-success",
};

interface PostHistoryProps {
  posts: Post[];
}

export default function PostHistory({ posts }: PostHistoryProps) {
  if (posts.length === 0) {
    return (
      <p className="text-sm text-muted py-8 text-center">
        No posts yet. Create your first one above.
      </p>
    );
  }

  return (
    <div className="space-y-2">
      {posts.map((post) => (
        <div
          key={post.id}
          className="flex items-start gap-3 p-3 bg-surface border border-border rounded-lg"
        >
          <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${statusDots[post.status]}`} />
          <div className="min-w-0 flex-1">
            <p className="text-sm text-foreground truncate">{post.hook}</p>
            <div className="flex items-center gap-3 mt-1">
              <span className={`text-xs capitalize ${statusColors[post.status]}`}>
                {post.status}
              </span>
              <span className="text-xs text-muted">
                {new Date(post.createdAt).toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
