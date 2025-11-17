import type { Lesson, Progress, Note, CourseStructure } from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

async function fetchAPI(endpoint: string, options?: RequestInit) {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }

  return response.json();
}

export async function getCourseStructure(): Promise<CourseStructure> {
  return fetchAPI('/api/course-structure');
}

export async function getLessons(): Promise<Lesson[]> {
  return fetchAPI('/api/lessons');
}

export async function getLesson(id: number): Promise<Lesson> {
  return fetchAPI(`/api/lessons/${id}`);
}

export async function getProgress(): Promise<Progress> {
  return fetchAPI('/api/progress');
}

export async function toggleComplete(id: number): Promise<{ success: boolean; is_completed: boolean }> {
  return fetchAPI(`/api/lessons/${id}/toggle-complete`, {
    method: 'POST',
  });
}

export async function updateTimeSpent(id: number, seconds: number): Promise<{ success: boolean }> {
  return fetchAPI(`/api/lessons/${id}/time-spent`, {
    method: 'POST',
    body: JSON.stringify({ seconds }),
  });
}

export async function toggleBookmark(id: number): Promise<{ success: boolean; is_bookmarked: boolean }> {
  return fetchAPI(`/api/lessons/${id}/toggle-bookmark`, {
    method: 'POST',
  });
}

export async function getNotes(lessonId: number): Promise<Note | null> {
  try {
    return await fetchAPI(`/api/lessons/${lessonId}/notes`);
  } catch (error) {
    return null;
  }
}

export async function saveNotes(lessonId: number, content: string): Promise<Note> {
  return fetchAPI(`/api/lessons/${lessonId}/notes`, {
    method: 'POST',
    body: JSON.stringify({ content }),
  });
}

export async function getLessonContent(contentFile: string): Promise<string> {
  const response = await fetch(`${API_URL}/api/content/${contentFile}`);
  if (!response.ok) {
    throw new Error(`Failed to load content: ${response.statusText}`);
  }
  return response.text();
}
