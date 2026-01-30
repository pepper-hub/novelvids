/**
 * Studio API Client
 *
 * Mock API functions for the video composition studio.
 * These will be replaced with real backend calls once the API is implemented.
 */

import type {
  VideoClip,
  StudioShot,
  StudioProject,
  GenerateVideoRequest,
  ComposeVideoRequest,
  TimelineTrack,
  VideoModel,
} from '@/types/studio'
import type { StoryboardResponse } from './storyboard'
import { getStoryboard } from './storyboard'

// ============== Mock Data Generators ==============

let clipIdCounter = 1

function generateMockClip(
  shotSequence: number,
  model: VideoModel,
  duration: number,
  prompt: string,
  negativePrompt: string | null
): VideoClip {
  const id = `clip-${clipIdCounter++}-${Date.now()}`
  return {
    id,
    shotSequence,
    model,
    status: 'completed',
    progress: 100,
    videoUrl: null, // Mock - no actual video
    thumbnailUrl: null, // Mock - no actual thumbnail
    duration,
    createdAt: new Date().toISOString(),
    prompt,
    negativePrompt,
    error: null,
  }
}

// ============== API Functions ==============

/**
 * Get studio project data for a chapter.
 * Loads storyboard and converts to studio format.
 */
export async function getStudioProject(chapterId: string): Promise<StudioProject> {
  const storyboard: StoryboardResponse = await getStoryboard(chapterId)

  const shots: StudioShot[] = storyboard.shots.map(shot => ({
    ...shot,
    clips: [],
    selectedClipId: null,
  }))

  return {
    chapterId,
    shots,
    timeline: [
      { id: 'video-track', type: 'video', clips: [] },
      { id: 'audio-track', type: 'audio', clips: [] },
    ],
    totalDuration: storyboard.total_duration,
  }
}

/**
 * Generate a new video clip for a shot (MOCK).
 * In real implementation, this would start a task and return task ID.
 */
export async function generateVideoClip(
  _chapterId: string,
  request: GenerateVideoRequest,
  prompt: string,
  negativePrompt: string | null
): Promise<VideoClip> {
  // Simulate API delay (500ms - 1.5s)
  const delay = 500 + Math.random() * 1000
  await new Promise(resolve => setTimeout(resolve, delay))

  return generateMockClip(
    request.shotSequence,
    request.model,
    request.duration,
    prompt,
    negativePrompt
  )
}

/**
 * Get all clips for a shot.
 */
export async function getShotClips(
  _chapterId: string,
  _shotSequence: number
): Promise<VideoClip[]> {
  // Mock - returns empty array, clips are managed locally
  return []
}

/**
 * Select a clip for a shot.
 */
export async function selectClipForShot(
  _chapterId: string,
  _shotSequence: number,
  _clipId: string
): Promise<void> {
  // Mock - no-op, state managed locally
  await new Promise(resolve => setTimeout(resolve, 100))
}

/**
 * Delete a clip.
 */
export async function deleteClip(
  _chapterId: string,
  _clipId: string
): Promise<void> {
  await new Promise(resolve => setTimeout(resolve, 100))
}

/**
 * Update timeline arrangement.
 */
export async function updateTimeline(
  _chapterId: string,
  _timeline: TimelineTrack[]
): Promise<void> {
  await new Promise(resolve => setTimeout(resolve, 100))
}

/**
 * Compose final video (MOCK).
 * In real implementation, this would start a composition task.
 */
export async function composeVideo(
  _chapterId: string,
  _request: ComposeVideoRequest
): Promise<{ taskId: string }> {
  await new Promise(resolve => setTimeout(resolve, 500))
  return { taskId: `compose-task-${Date.now()}` }
}

/**
 * Get video generation task status (MOCK).
 */
export async function getVideoTaskStatus(_taskId: string): Promise<{
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  videoUrl: string | null
  error: string | null
}> {
  return {
    status: 'completed',
    progress: 100,
    videoUrl: null,
    error: null,
  }
}

// ============== Constants ==============

export const VIDEO_MODELS = [
  { value: 'veo' as const, label: 'Veo 3.1', labelZh: 'Veo 3.1', description: 'Native audio, multi-reference', descriptionZh: '原生音频，多参考图' },
  { value: 'vidu' as const, label: 'Vidu Q2', labelZh: 'Vidu Q2', description: 'Fine expressions, smooth motion', descriptionZh: '细腻表情，平滑运动' },
  { value: 'kling' as const, label: 'Kling 2.5', labelZh: 'Kling 2.5', description: 'Cinematic action videos', descriptionZh: '电影感动作视频' },
  { value: 'sora' as const, label: 'Sora 2', labelZh: 'Sora 2', description: 'Physics-aware, complex scenes', descriptionZh: '物理感知，复杂场景' },
] as const

export const EXPORT_RESOLUTIONS = [
  { value: '720p' as const, label: '720p (HD)', labelZh: '720p (高清)' },
  { value: '1080p' as const, label: '1080p (Full HD)', labelZh: '1080p (全高清)' },
  { value: '4k' as const, label: '4K (Ultra HD)', labelZh: '4K (超高清)' },
] as const

export const EXPORT_FORMATS = [
  { value: 'mp4' as const, label: 'MP4 (H.264)', labelZh: 'MP4 (H.264)' },
  { value: 'webm' as const, label: 'WebM (VP9)', labelZh: 'WebM (VP9)' },
] as const

export const EXPORT_FPS = [
  { value: 24 as const, label: '24 fps (Film)', labelZh: '24 帧 (电影)' },
  { value: 30 as const, label: '30 fps (Standard)', labelZh: '30 帧 (标准)' },
  { value: 60 as const, label: '60 fps (Smooth)', labelZh: '60 帧 (流畅)' },
] as const
