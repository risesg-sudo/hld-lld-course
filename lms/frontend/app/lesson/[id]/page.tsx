"use client";

import { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { getLesson, getLessonContent, toggleComplete, toggleBookmark, updateTimeSpent } from "@/lib/api";
import { Lesson } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import VideoPlayer from "@/components/VideoPlayer";
import LessonContent from "@/components/LessonContent";
import NotesEditor from "@/components/NotesEditor";
import {
  ChevronLeft,
  ChevronRight,
  Star,
  Clock,
  CheckCircle2,
  Circle,
} from "lucide-react";
import { formatTime } from "@/lib/utils";

export default function LessonPage() {
  const params = useParams();
  const router = useRouter();
  const lessonId = parseInt(params.id as string);

  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(true);
  const [timeSpent, setTimeSpent] = useState(0);
  const [isCompleted, setIsCompleted] = useState(false);
  const [isBookmarked, setIsBookmarked] = useState(false);

  const timerRef = useRef<NodeJS.Timeout>();
  const timeAccumulatorRef = useRef(0);

  useEffect(() => {
    loadLesson();

    return () => {
      // Save time on unmount
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (timeAccumulatorRef.current > 0) {
        saveTimeSpent();
      }
    };
  }, [lessonId]);

  useEffect(() => {
    // Start timer
    timerRef.current = setInterval(() => {
      setTimeSpent((prev) => prev + 1);
      timeAccumulatorRef.current += 1;

      // Save every 30 seconds
      if (timeAccumulatorRef.current >= 30) {
        saveTimeSpent();
      }
    }, 1000);

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [lessonId]);

  async function loadLesson() {
    try {
      setLoading(true);
      const lessonData = await getLesson(lessonId);
      setLesson(lessonData);
      setIsCompleted(lessonData.is_completed);
      setIsBookmarked(lessonData.is_bookmarked);
      setTimeSpent(lessonData.time_spent_seconds);

      // Load content if available
      if (lessonData.content_file) {
        const contentData = await getLessonContent(lessonData.content_file);
        setContent(contentData);
      }
    } catch (error) {
      console.error("Failed to load lesson:", error);
    } finally {
      setLoading(false);
    }
  }

  async function saveTimeSpent() {
    if (timeAccumulatorRef.current > 0) {
      try {
        await updateTimeSpent(lessonId, timeAccumulatorRef.current);
        timeAccumulatorRef.current = 0;
      } catch (error) {
        console.error("Failed to save time:", error);
      }
    }
  }

  async function handleToggleComplete() {
    try {
      const result = await toggleComplete(lessonId);
      setIsCompleted(result.is_completed);
    } catch (error) {
      console.error("Failed to toggle completion:", error);
    }
  }

  async function handleToggleBookmark() {
    try {
      const result = await toggleBookmark(lessonId);
      setIsBookmarked(result.is_bookmarked);
    } catch (error) {
      console.error("Failed to toggle bookmark:", error);
    }
  }

  function navigateToLesson(direction: "prev" | "next") {
    const newId = direction === "prev" ? lessonId - 1 : lessonId + 1;
    if (newId > 0) {
      router.push(`/lesson/${newId}`);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h1 className="text-2xl font-bold">Lesson not found</h1>
        <Button onClick={() => router.push("/")} className="mt-4">
          Go to Dashboard
        </Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6 max-w-5xl">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
          <Badge variant="outline">
            {lesson.week_type} Week {lesson.week_num}
          </Badge>
          <span>•</span>
          <span>{lesson.topic}</span>
        </div>

        <h1 className="text-3xl font-bold mb-4">{lesson.title}</h1>

        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Clock className="h-4 w-4" />
              <span>{formatTime(timeSpent)} spent</span>
            </div>
            <div className="text-sm text-muted-foreground">
              Est: {lesson.estimated_minutes} minutes
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Bookmark Toggle */}
            <Button
              variant={isBookmarked ? "default" : "outline"}
              size="sm"
              onClick={handleToggleBookmark}
            >
              <Star
                className={`h-4 w-4 mr-2 ${
                  isBookmarked ? "fill-current" : ""
                }`}
              />
              {isBookmarked ? "Bookmarked" : "Bookmark"}
            </Button>

            {/* Complete Toggle */}
            <div className="flex items-center gap-2">
              <Switch
                checked={isCompleted}
                onCheckedChange={handleToggleComplete}
                id="complete-switch"
              />
              <label
                htmlFor="complete-switch"
                className="text-sm font-medium cursor-pointer flex items-center gap-2"
              >
                {isCompleted ? (
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                ) : (
                  <Circle className="h-4 w-4" />
                )}
                Mark Complete
              </label>
            </div>
          </div>
        </div>
      </div>

      <Separator className="mb-6" />

      {/* Video */}
      {lesson.video_url && (
        <div className="mb-8">
          <VideoPlayer url={lesson.video_url} />
        </div>
      )}

      {/* Lesson Content */}
      {content && (
        <Card className="mb-8">
          <CardContent className="pt-6">
            <LessonContent content={content} />
          </CardContent>
        </Card>
      )}

      {/* Notes Editor */}
      <div className="mb-8">
        <NotesEditor lessonId={lessonId} />
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between pt-6 border-t">
        <Button
          variant="outline"
          onClick={() => navigateToLesson("prev")}
          disabled={lessonId <= 1}
        >
          <ChevronLeft className="h-4 w-4 mr-2" />
          Previous Lesson
        </Button>

        <Button onClick={() => router.push("/")}>Back to Dashboard</Button>

        <Button
          variant="outline"
          onClick={() => navigateToLesson("next")}
        >
          Next Lesson
          <ChevronRight className="h-4 w-4 ml-2" />
        </Button>
      </div>
    </div>
  );
}
