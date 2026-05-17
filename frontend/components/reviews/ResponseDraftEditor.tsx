"use client";

import { useState } from "react";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";

interface ResponseDraftEditorProps {
  initialDraft: string;
  reviewId: string;
  onSave: (reviewId: string, editedResponse: string) => void;
  onCancel: () => void;
}

export default function ResponseDraftEditor({
  initialDraft, reviewId, onSave, onCancel,
}: ResponseDraftEditorProps) {
  const [draft, setDraft] = useState(initialDraft);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    await onSave(reviewId, draft);
    setSaving(false);
  };

  const charCount = draft.length;
  const isLong = charCount > 500;

  return (
    <Card>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-semibold text-foreground dark:text-white mb-2">
            Edit Response Draft
          </label>
          <textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            rows={8}
            className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm text-foreground dark:text-white resize-none focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-transparent transition-all"
            placeholder="Write your response..."
          />
          <div className="flex items-center justify-between mt-1">
            <p className={`text-xs ${isLong ? "text-amber-500" : "text-muted"}`}>
              {charCount} characters {isLong && "— consider shortening"}
            </p>
            <p className="text-xs text-muted">
              Must end with: Managed by Co Host Ceylon
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button onClick={handleSave} loading={saving} disabled={!draft.trim()}>
            Save Draft
          </Button>
          <Button variant="ghost" onClick={onCancel}>
            Cancel
          </Button>
        </div>
      </div>
    </Card>
  );
}
