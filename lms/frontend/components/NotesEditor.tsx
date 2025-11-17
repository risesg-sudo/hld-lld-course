"use client";

import { useState, useEffect, useRef } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getNotes, saveNotes } from "@/lib/api";
import { Save, Check } from "lucide-react";

interface NotesEditorProps {
  lessonId: number;
}

export default function NotesEditor({ lessonId }: NotesEditorProps) {
  const [content, setContent] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const saveTimeoutRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    loadNotes();
  }, [lessonId]);

  async function loadNotes() {
    try {
      const note = await getNotes(lessonId);
      if (note) {
        setContent(note.content);
        setLastSaved(new Date(note.updated_at));
      } else {
        setContent("");
        setLastSaved(null);
      }
    } catch (error) {
      console.error("Failed to load notes:", error);
    }
  }

  const handleContentChange = (value: string) => {
    setContent(value);

    // Clear existing timeout
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    // Auto-save after 2 seconds of inactivity
    saveTimeoutRef.current = setTimeout(() => {
      saveNotesNow(value);
    }, 2000);
  };

  const saveNotesNow = async (noteContent: string) => {
    if (!noteContent.trim()) return;

    setIsSaving(true);
    try {
      await saveNotes(lessonId, noteContent);
      setLastSaved(new Date());
    } catch (error) {
      console.error("Failed to save notes:", error);
    } finally {
      setIsSaving(false);
    }
  };

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, []);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">My Notes</CardTitle>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            {isSaving ? (
              <>
                <Save className="h-4 w-4 animate-pulse" />
                <span>Saving...</span>
              </>
            ) : lastSaved ? (
              <>
                <Check className="h-4 w-4 text-green-500" />
                <span>Saved {lastSaved.toLocaleTimeString()}</span>
              </>
            ) : null}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Textarea
          placeholder="Take notes here... (Auto-saves after 2 seconds)"
          value={content}
          onChange={(e) => handleContentChange(e.target.value)}
          className="min-h-[200px] font-mono text-sm resize-none"
        />
      </CardContent>
    </Card>
  );
}
