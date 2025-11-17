# YouTube: Video Transcoding

## The Transcoding Challenge

When someone uploads a 1080p video, we must create 7 different resolutions for adaptive streaming:
- 2160p (4K)
- 1440p (2K)
- 1080p (Full HD)
- 720p (HD)
- 480p (SD)
- 360p
- 240p

Each resolution needs multiple bitrates for adaptive quality. This creates 20+ output files per video.

## Why Transcode?

**Different devices**: Phone screens don't need 4K. Desktop monitors benefit from it.

**Variable bandwidth**: 2G networks can't stream 1080p. Fiber can handle 4K.

**Adaptive streaming**: Client switches quality based on current network speed.

## Transcoding Architecture

```
┌──────────────┐      ┌────────────────┐      ┌─────────────┐
│Upload Service│─────►│  Kafka Queue   │─────►│ Transcoding │
│              │      │  (Job Queue)   │      │   Workers   │
└──────────────┘      └────────────────┘      └──────┬──────┘
                                                      │
                                              ┌───────┴───────┐
                                              │               │
                                              ▼               ▼
                                        ┌──────────┐    ┌──────────┐
                                        │ Worker 1 │    │ Worker N │
                                        │ (FFmpeg) │    │ (FFmpeg) │
                                        └─────┬────┘    └─────┬────┘
                                              │               │
                                              └───────┬───────┘
                                                      ▼
                                              ┌─────────────┐
                                              │   GCS/S3    │
                                              │  (Output)   │
                                              └─────────────┘
```

## Transcoding Worker

```python
class TranscodingWorker:
    async def process_video(self, job):
        video_id = job['video_id']
        input_path = await self.download_from_gcs(job['gcs_key'])
        
        # Transcode to multiple resolutions in parallel
        tasks = [
            self.transcode_resolution(input_path, '240p', '500k'),
            self.transcode_resolution(input_path, '360p', '1M'),
            self.transcode_resolution(input_path, '480p', '1.5M'),
            self.transcode_resolution(input_path, '720p', '3M'),
            self.transcode_resolution(input_path, '1080p', '6M'),
            self.transcode_resolution(input_path, '1440p', '12M'),
            self.transcode_resolution(input_path, '2160p', '24M'),
        ]
        
        outputs = await asyncio.gather(*tasks)
        
        # Generate HLS manifest
        manifest = self.create_hls_manifest(outputs)
        
        # Upload all outputs to GCS
        await self.upload_outputs(video_id, outputs, manifest)
        
        # Mark as ready
        await db.execute("""
            UPDATE videos
            SET status = 'ready', processed_at = NOW()
            WHERE video_id = ?
        """, (video_id,))
        
    async def transcode_resolution(self, input, resolution, bitrate):
        output_path = f"/tmp/{resolution}_output.mp4"
        
        # FFmpeg command
        cmd = [
            'ffmpeg', '-i', input,
            '-vf', f'scale=-2:{resolution[:-1]}',  # e.g., scale=-2:1080
            '-b:v', bitrate,
            '-c:v', 'libx264',  # H.264 codec
            '-preset', 'fast',
            '-c:a', 'aac',
            '-b:a', '128k',
            output_path
        ]
        
        await run_command(cmd)
        return output_path
```

## GPU Acceleration

For faster transcoding:
```python
# Use NVENC (NVIDIA GPU encoder)
cmd = [
    'ffmpeg', '-i', input,
    '-c:v', 'h264_nvenc',  # GPU encoder
    '-preset', 'fast',
    '-b:v', bitrate,
    output
]
```

**Speed**: GPU encoding is 10x faster than CPU. 10-minute video transcodes in 1 minute instead of 10.

## Priority Queue

```python
# Kafka topic with priority
await kafka.send('video.transcoding.high_priority', job)  # Popular creators
await kafka.send('video.transcoding.normal', job)  # Regular users
await kafka.send('video.transcoding.low_priority', job)  # Re-encodes

# Workers consume high priority first
consumer = KafkaConsumer(['high_priority', 'normal', 'low_priority'])
```

## Adaptive Bitrate Streaming (HLS)

Generate manifest file:
```m3u8
#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=500000,RESOLUTION=426x240
240p/playlist.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=640x360
360p/playlist.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=3000000,RESOLUTION=1280x720
720p/playlist.m3u8
```

Client chooses quality based on bandwidth.

## Why This Design Works

**Parallel transcoding**: All resolutions process simultaneously (7x speedup).

**GPU acceleration**: 10x faster than CPU encoding.

**Priority queue**: Important videos process first.

**Async design**: Upload confirms immediately, transcoding happens in background.

**Scalable**: Add more workers to handle increased load.
