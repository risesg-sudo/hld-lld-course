"use client";

import { getYouTubeEmbedUrl } from "@/lib/utils";

interface VideoPlayerProps {
  url: string;
}

export default function VideoPlayer({ url }: VideoPlayerProps) {
  const embedUrl = getYouTubeEmbedUrl(url);

  return (
    <div className="aspect-video w-full rounded-lg overflow-hidden bg-black">
      <iframe
        src={embedUrl}
        title="Video Player"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
        className="w-full h-full"
      />
    </div>
  );
}
