"use client";

import { useState, useCallback } from "react";
import ContentInput from "@/components/ContentInput";
import HookCard from "@/components/HookCard";
import PostPreview from "@/components/PostPreview";
import PostHistory from "@/components/PostHistory";
import type { Hook, Post, DashboardStep, InputType } from "@/lib/types";

export default function Dashboard() {
  const [step, setStep] = useState<DashboardStep>("input");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [inputContent, setInputContent] = useState("");
  const [inputType, setInputType] = useState<InputType>("topic");

  const [hooks, setHooks] = useState<Hook[]>([]);
  const [selectedHook, setSelectedHook] = useState<Hook | null>(null);

  const [postContent, setPostContent] = useState("");
  const [posts, setPosts] = useState<Post[]>([]);

  const generateHooks = useCallback(async (content: string, type: InputType) => {
    setLoading(true);
    setError(null);
    setInputContent(content);
    setInputType(type);

    try {
      const res = await fetch("/api/hooks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content, type }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to generate hooks");
      setHooks(data.hooks);
      setSelectedHook(null);
      setStep("hooks");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }, []);

  const generatePost = useCallback(async () => {
    if (!selectedHook) return;
    setLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/post", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          hook: selectedHook.text,
          content: inputContent,
          type: inputType,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to generate post");
      setPostContent(data.post);
      setStep("preview");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }, [selectedHook, inputContent, inputType]);

  const schedulePost = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/buffer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: postContent }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to schedule post");

      const newPost: Post = {
        id: `post-${Date.now()}`,
        hook: selectedHook?.text || "",
        body: postContent,
        status: "scheduled",
        createdAt: new Date().toISOString(),
        bufferPostId: data?.data?.createPost?.post?.id,
      };
      setPosts((prev) => [newPost, ...prev]);
      setStep("scheduled");
    } catch (err) {
      const newPost: Post = {
        id: `post-${Date.now()}`,
        hook: selectedHook?.text || "",
        body: postContent,
        status: "draft",
        createdAt: new Date().toISOString(),
      };
      setPosts((prev) => [newPost, ...prev]);
      setError(
        `Saved as draft. Buffer error: ${err instanceof Error ? err.message : "Unknown error"}`
      );
      setStep("scheduled");
    } finally {
      setLoading(false);
    }
  }, [postContent, selectedHook]);

  function reset() {
    setStep("input");
    setHooks([]);
    setSelectedHook(null);
    setPostContent("");
    setError(null);
  }

  return (
    <div className="flex-1 flex flex-col">
      <header className="border-b border-border px-6 py-4">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-accent/20 flex items-center justify-center text-accent font-bold text-sm">
              R
            </div>
            <div>
              <h1 className="text-base font-semibold text-foreground">Rex</h1>
              <p className="text-xs text-muted">LinkedIn Content Dashboard</p>
            </div>
          </div>
          {step !== "input" && (
            <button
              onClick={reset}
              className="text-sm text-muted hover:text-foreground transition-colors"
            >
              New post
            </button>
          )}
        </div>
      </header>

      <main className="flex-1 px-6 py-8">
        <div className="max-w-3xl mx-auto space-y-8">
          {error && (
            <div className="px-4 py-3 bg-red-500/10 border border-red-500/20 rounded-lg text-sm text-red-400">
              {error}
            </div>
          )}

          {step === "input" && (
            <section>
              <h2 className="text-lg font-semibold text-foreground mb-1">
                What do you want to post about?
              </h2>
              <p className="text-sm text-muted mb-6">
                Enter a topic, paste a transcript, or share some news. Rex will craft hooks for you.
              </p>
              <ContentInput onSubmit={generateHooks} loading={loading} />
            </section>
          )}

          {step === "hooks" && (
            <section>
              <h2 className="text-lg font-semibold text-foreground mb-1">
                Pick a hook
              </h2>
              <p className="text-sm text-muted mb-6">
                Select the opening that hits hardest. Rex will build the full post around it.
              </p>
              <div className="space-y-3">
                {hooks.map((hook) => (
                  <HookCard
                    key={hook.id}
                    hook={hook}
                    selected={selectedHook?.id === hook.id}
                    onSelect={setSelectedHook}
                  />
                ))}
              </div>
              <div className="flex items-center gap-3 mt-6">
                <button
                  onClick={() => setStep("input")}
                  className="px-4 py-2 text-sm text-muted hover:text-foreground transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={generatePost}
                  disabled={!selectedHook || loading}
                  className="px-6 py-2.5 bg-accent text-slate-900 font-medium rounded-lg hover:bg-cyan-300 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? "Writing post..." : "Write full post"}
                </button>
              </div>
            </section>
          )}

          {step === "preview" && (
            <section>
              <h2 className="text-lg font-semibold text-foreground mb-1">
                Preview your post
              </h2>
              <p className="text-sm text-muted mb-6">
                Review, edit if needed, then push to Buffer.
              </p>
              <PostPreview
                content={postContent}
                onEdit={setPostContent}
                onSchedule={schedulePost}
                onBack={() => setStep("hooks")}
                scheduling={loading}
              />
            </section>
          )}

          {step === "scheduled" && (
            <section className="text-center py-12">
              <div className="w-16 h-16 rounded-full bg-success/20 flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-lg font-semibold text-foreground mb-1">
                {posts[0]?.status === "scheduled" ? "Scheduled!" : "Saved as draft"}
              </h2>
              <p className="text-sm text-muted mb-6">
                {posts[0]?.status === "scheduled"
                  ? "Your post is queued in Buffer."
                  : "Buffer wasn't available, but your post is saved."}
              </p>
              <button
                onClick={reset}
                className="px-6 py-2.5 bg-accent text-slate-900 font-medium rounded-lg hover:bg-cyan-300 transition-colors"
              >
                Create another post
              </button>
            </section>
          )}

          {posts.length > 0 && (
            <section>
              <h2 className="text-sm font-semibold text-muted uppercase tracking-wider mb-3">
                Recent posts
              </h2>
              <PostHistory posts={posts} />
            </section>
          )}
        </div>
      </main>
    </div>
  );
}
