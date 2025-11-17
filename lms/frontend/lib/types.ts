export interface Lesson {
  id: number;
  week_num: number;
  week_type: 'LLD' | 'HLD';
  topic: string;
  title: string;
  estimated_minutes: number;
  video_url?: string;
  content_file?: string;
  is_completed: boolean;
  is_bookmarked: boolean;
  time_spent_seconds: number;
  order_in_week: number;
}

export interface WeekProgress {
  week_type: 'LLD' | 'HLD';
  week_num: number;
  total_lessons: number;
  completed_lessons: number;
  completion_percentage: number;
  total_estimated_minutes: number;
  time_spent_seconds: number;
}

export interface Progress {
  overall: {
    total_lessons: number;
    completed_lessons: number;
    completion_percentage: number;
    total_estimated_minutes: number;
    time_spent_seconds: number;
  };
  by_week: WeekProgress[];
  streak: {
    current_days: number;
    best_days: number;
  };
}

export interface Note {
  id: number;
  lesson_id: number;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface CourseStructure {
  weeks: {
    [key: string]: {
      week_num: number;
      week_type: 'LLD' | 'HLD';
      lessons: Lesson[];
    };
  };
}

export interface ActivityDay {
  date: string;
  count: number;
  level: 0 | 1 | 2 | 3 | 4; // 0 = no activity, 4 = max activity
}
