"use client";

import { Lesson } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Check, Clock, Star, Play } from "lucide-react";
import Link from "next/link";

interface LessonCardProps {
  lesson: Lesson;
  isActive?: boolean;
}

export default function LessonCard({ lesson, isActive = false }: LessonCardProps) {
  return (
    <Link
      href={`/lesson/${lesson.id}`}
      className={cn(
        "block px-4 py-3 rounded-lg transition-all border",
        isActive
          ? "bg-primary/10 border-primary"
          : "hover:bg-muted border-transparent"
      )}
    >
      <div className="flex items-start gap-3">
        {/* Status Icon */}
        <div className="mt-0.5">
          {lesson.is_completed ? (
            <div className="h-5 w-5 rounded-full bg-green-500 flex items-center justify-center">
              <Check className="h-3 w-3 text-white" />
            </div>
          ) : (
            <div className="h-5 w-5 rounded-full border-2 border-muted-foreground/30" />
          )}
        </div>

        {/* Lesson Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h4 className={cn(
              "text-sm font-medium leading-tight",
              lesson.is_completed && "text-muted-foreground line-through"
            )}>
              {lesson.title}
            </h4>
            {lesson.is_bookmarked && (
              <Star className="h-4 w-4 text-yellow-500 fill-yellow-500 shrink-0" />
            )}
          </div>

          <p className="text-xs text-muted-foreground mt-1 truncate">
            {lesson.topic}
          </p>

          {/* Meta info */}
          <div className="flex items-center gap-3 mt-2">
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <Clock className="h-3 w-3" />
              <span>{lesson.estimated_minutes}m</span>
            </div>
            {lesson.video_url && (
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <Play className="h-3 w-3" />
                <span>Video</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}
