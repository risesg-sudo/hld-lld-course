"use client";

import { useEffect, useState } from "react";
import { getCourseStructure } from "@/lib/api";
import { Lesson } from "@/lib/types";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import LessonCard from "@/components/LessonCard";
import ProgressBar from "@/components/ProgressBar";
import { Search, ChevronDown, BookOpen } from "lucide-react";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

type FilterType = "all" | "completed" | "incomplete" | "bookmarked";

interface WeekData {
  week_num: number;
  week_type: 'LLD' | 'HLD';
  lessons: Lesson[];
}

export default function Sidebar() {
  const [weeks, setWeeks] = useState<WeekData[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [filter, setFilter] = useState<FilterType>("all");
  const [openWeeks, setOpenWeeks] = useState<Set<string>>(new Set());
  const pathname = usePathname();

  useEffect(() => {
    loadCourseStructure();
  }, []);

  async function loadCourseStructure() {
    try {
      const structure = await getCourseStructure();
      const weeksArray: WeekData[] = Object.values(structure.weeks);

      // Sort weeks by type and number
      weeksArray.sort((a, b) => {
        if (a.week_type === b.week_type) {
          return a.week_num - b.week_num;
        }
        return a.week_type === 'LLD' ? -1 : 1;
      });

      setWeeks(weeksArray);

      // Open all weeks by default
      const allWeekKeys = weeksArray.map(w => `${w.week_type}-${w.week_num}`);
      setOpenWeeks(new Set(allWeekKeys));
    } catch (error) {
      console.error("Failed to load course structure:", error);
    }
  }

  const toggleWeek = (weekKey: string) => {
    setOpenWeeks(prev => {
      const newSet = new Set(prev);
      if (newSet.has(weekKey)) {
        newSet.delete(weekKey);
      } else {
        newSet.add(weekKey);
      }
      return newSet;
    });
  };

  const filterLessons = (lessons: Lesson[]): Lesson[] => {
    return lessons.filter(lesson => {
      // Apply search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const matchesSearch =
          lesson.title.toLowerCase().includes(query) ||
          lesson.topic.toLowerCase().includes(query);
        if (!matchesSearch) return false;
      }

      // Apply status filter
      if (filter === "completed") return lesson.is_completed;
      if (filter === "incomplete") return !lesson.is_completed;
      if (filter === "bookmarked") return lesson.is_bookmarked;

      return true;
    });
  };

  const getCurrentLessonId = (): number | null => {
    const match = pathname?.match(/\/lesson\/(\d+)/);
    return match ? parseInt(match[1]) : null;
  };

  const currentLessonId = getCurrentLessonId();

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 space-y-4">
        <div className="flex items-center gap-2">
          <BookOpen className="h-5 w-5 text-primary" />
          <h2 className="font-semibold text-lg">Course Content</h2>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search lessons..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-2">
          {(["all", "completed", "incomplete", "bookmarked"] as FilterType[]).map((f) => (
            <Badge
              key={f}
              variant={filter === f ? "default" : "outline"}
              className="cursor-pointer capitalize"
              onClick={() => setFilter(f)}
            >
              {f}
            </Badge>
          ))}
        </div>
      </div>

      <Separator />

      {/* Weeks List */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-2 space-y-1">
          {weeks.map((week) => {
            const weekKey = `${week.week_type}-${week.week_num}`;
            const isOpen = openWeeks.has(weekKey);
            const filteredLessons = filterLessons(week.lessons);

            if (filteredLessons.length === 0 && (searchQuery || filter !== "all")) {
              return null;
            }

            const completedCount = week.lessons.filter(l => l.is_completed).length;
            const totalCount = week.lessons.length;
            const progress = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;
            const estimatedTime = week.lessons.reduce((acc, l) => acc + l.estimated_minutes, 0);

            return (
              <Collapsible
                key={weekKey}
                open={isOpen}
                onOpenChange={() => toggleWeek(weekKey)}
              >
                <CollapsibleTrigger className="w-full">
                  <div className="px-3 py-2 hover:bg-muted rounded-lg transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <ChevronDown
                          className={cn(
                            "h-4 w-4 transition-transform",
                            !isOpen && "-rotate-90"
                          )}
                        />
                        <span className="font-medium text-sm">
                          {week.week_type} Week {week.week_num}
                        </span>
                      </div>
                      <Badge variant="secondary" className="text-xs">
                        {completedCount}/{totalCount}
                      </Badge>
                    </div>

                    <div className="mt-2 ml-6 space-y-1">
                      <ProgressBar value={progress} />
                      <p className="text-xs text-muted-foreground">
                        {Math.floor(estimatedTime / 60)}h {estimatedTime % 60}m
                      </p>
                    </div>
                  </div>
                </CollapsibleTrigger>

                <CollapsibleContent>
                  <div className="ml-6 mt-1 space-y-1">
                    {filteredLessons.map((lesson) => (
                      <LessonCard
                        key={lesson.id}
                        lesson={lesson}
                        isActive={lesson.id === currentLessonId}
                      />
                    ))}
                  </div>
                </CollapsibleContent>
              </Collapsible>
            );
          })}
        </div>
      </div>
    </div>
  );
}
