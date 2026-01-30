<script setup lang="ts">
/**
 * StudioView - Video Composition Studio
 *
 * The final step in the chapter workflow where users:
 * 1. View storyboard shots in a left sidebar
 * 2. Generate video clips for each shot (multiple versions - gacha mechanic)
 * 3. Pick the best video version for each shot
 * 4. Arrange clips on a timeline via drag-and-drop
 * 5. Compose the final video
 */
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useToastStore } from '@/stores/toast'
import {
  getStudioProject,
  generateVideoClip,
  VIDEO_MODELS,
  EXPORT_RESOLUTIONS,
  EXPORT_FORMATS,
  EXPORT_FPS,
} from '@/api/studio'
import { getStoryboardPrompts } from '@/api/storyboard'
import type { StudioProject, StudioShot, VideoClip, TimelineClip, VideoModel, ExportSettings } from '@/types/studio'
import type { ShotPrompt } from '@/api/storyboard'

const { t, locale } = useI18n()
const route = useRoute()
const toastStore = useToastStore()

// Route params
const chapterId = computed(() => route.params.chapterId as string)

// ============== State ==============

// Loading states
const isLoading = ref(true)
const isGenerating = ref(false)
const error = ref<string | null>(null)

// Project data
const project = ref<StudioProject | null>(null)
const shotPrompts = ref<ShotPrompt[]>([])

// Selection state
const selectedShotSequence = ref<number | null>(null)
const selectedShot = computed<StudioShot | null>(() =>
  project.value?.shots.find(s => s.sequence === selectedShotSequence.value) ?? null
)
const selectedClip = computed<VideoClip | null>(() => {
  if (!selectedShot.value?.selectedClipId) return null
  return selectedShot.value.clips.find(c => c.id === selectedShot.value?.selectedClipId) ?? null
})

// Current shot's prompt
const currentShotPrompt = computed<ShotPrompt | null>(() => {
  if (!selectedShotSequence.value) return null
  return shotPrompts.value.find(p => p.sequence === selectedShotSequence.value) ?? null
})

// Generate settings
const generateSettings = ref<{ model: VideoModel; duration: number }>({
  model: 'veo',
  duration: 6,
})

// Playback state (UI only, no actual video playback)
const isPlaying = ref(false)
const currentTime = ref(0)

// Timeline state
const videoTrackClips = computed<TimelineClip[]>(() => {
  const track = project.value?.timeline.find(t => t.type === 'video')
  return track?.clips ?? []
})
const timelineTotalDuration = computed(() => {
  const clips = videoTrackClips.value
  if (clips.length === 0) return 0
  const lastClip = clips[clips.length - 1]
  return lastClip.startTime + lastClip.duration
})

// Drag state
const draggingFromGallery = ref<VideoClip | null>(null)
const draggingTimelineIndex = ref<number | null>(null)

// Export modal
const showExportModal = ref(false)
const exportSettings = ref<ExportSettings>({
  format: 'mp4',
  resolution: '1080p',
  fps: 24,
  includeAudio: true,
})

// ============== Data Loading ==============

async function loadData(): Promise<void> {
  if (!chapterId.value) return

  isLoading.value = true
  error.value = null

  try {
    project.value = await getStudioProject(chapterId.value)

    try {
      const promptsResponse = await getStoryboardPrompts(chapterId.value, 'veo')
      shotPrompts.value = promptsResponse.prompts
    } catch {
      // Prompts are optional, don't fail on error
      shotPrompts.value = []
    }

    // Auto-select first shot
    if (project.value.shots.length > 0 && !selectedShotSequence.value) {
      selectedShotSequence.value = project.value.shots[0].sequence
    }
  } catch (e: unknown) {
    const message = e instanceof Error ? e.message : 'Failed to load studio data'
    error.value = message
    toastStore.error(message)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadData()
})

watch(chapterId, () => {
  loadData()
})

// ============== Shot Selection ==============

function selectShot(sequence: number): void {
  selectedShotSequence.value = sequence
}

// ============== Video Generation ==============

async function handleGenerateVideo(): Promise<void> {
  if (!selectedShot.value || isGenerating.value) return

  isGenerating.value = true

  try {
    const prompt = currentShotPrompt.value?.prompt ?? selectedShot.value.description_cn
    const negativePrompt = currentShotPrompt.value?.negative_prompt ?? null

    const clip = await generateVideoClip(
      chapterId.value,
      {
        shotSequence: selectedShot.value.sequence,
        model: generateSettings.value.model,
        duration: generateSettings.value.duration,
      },
      prompt,
      negativePrompt
    )

    selectedShot.value.clips.push(clip)

    // Auto-select if it's the first clip
    if (!selectedShot.value.selectedClipId) {
      selectedShot.value.selectedClipId = clip.id
    }

    toastStore.success(t('studio.clipGenerated'))
  } catch {
    toastStore.error(t('studio.clipGenerateFailed'))
  } finally {
    isGenerating.value = false
  }
}

// ============== Clip Selection ==============

function selectClipForShot(clip: VideoClip): void {
  if (!selectedShot.value) return
  selectedShot.value.selectedClipId = clip.id
  toastStore.success(t('studio.clipSelected'))
}

function deleteClipHandler(clip: VideoClip): void {
  if (!selectedShot.value) return
  if (!confirm(t('studio.deleteConfirm'))) return

  const index = selectedShot.value.clips.findIndex(c => c.id === clip.id)
  if (index >= 0) {
    selectedShot.value.clips.splice(index, 1)

    if (selectedShot.value.selectedClipId === clip.id) {
      selectedShot.value.selectedClipId = selectedShot.value.clips[0]?.id ?? null
    }

    toastStore.success(t('studio.clipDeleted'))
  }
}

// ============== Drag and Drop ==============

function handleGalleryDragStart(event: DragEvent, clip: VideoClip): void {
  if (!event.dataTransfer) return
  event.dataTransfer.setData('source', 'gallery')
  event.dataTransfer.setData('clip-id', clip.id)
  event.dataTransfer.setData('shot-sequence', String(clip.shotSequence))
  event.dataTransfer.effectAllowed = 'copy'
  draggingFromGallery.value = clip
}

function handleGalleryDragEnd(): void {
  draggingFromGallery.value = null
}

function handleTimelineDragStart(event: DragEvent, index: number): void {
  if (!event.dataTransfer) return
  event.dataTransfer.setData('source', 'timeline')
  event.dataTransfer.setData('timeline-index', String(index))
  event.dataTransfer.effectAllowed = 'move'
  draggingTimelineIndex.value = index
}

function handleTimelineDragEnd(): void {
  draggingTimelineIndex.value = null
}

function handleTimelineDragOver(event: DragEvent): void {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'copy'
  }
}

function handleTimelineDrop(event: DragEvent): void {
  event.preventDefault()
  const data = event.dataTransfer
  if (!data || !project.value) return

  const source = data.getData('source')

  if (source === 'gallery') {
    const clipId = data.getData('clip-id')
    const shotSequence = parseInt(data.getData('shot-sequence'), 10)
    addClipToTimeline(clipId, shotSequence)
  } else if (source === 'timeline') {
    const fromIndex = parseInt(data.getData('timeline-index'), 10)
    const toIndex = videoTrackClips.value.length - 1
    if (fromIndex !== toIndex) {
      reorderTimelineClip(fromIndex, toIndex)
    }
  }

  draggingFromGallery.value = null
  draggingTimelineIndex.value = null
}

function addClipToTimeline(clipId: string, shotSequence: number): void {
  if (!project.value) return

  const shot = project.value.shots.find(s => s.sequence === shotSequence)
  const clip = shot?.clips.find(c => c.id === clipId)
  if (!clip) return

  const videoTrack = project.value.timeline.find(t => t.type === 'video')
  if (!videoTrack) return

  const lastClip = videoTrack.clips[videoTrack.clips.length - 1]
  const startTime = lastClip ? lastClip.startTime + lastClip.duration : 0

  videoTrack.clips.push({
    id: `timeline-${Date.now()}`,
    clipId: clip.id,
    shotSequence: clip.shotSequence,
    startTime,
    duration: clip.duration,
    thumbnailUrl: clip.thumbnailUrl,
  })

  toastStore.success(t('studio.savedToTimeline'))
}

function reorderTimelineClip(fromIndex: number, toIndex: number): void {
  if (!project.value) return

  const videoTrack = project.value.timeline.find(t => t.type === 'video')
  if (!videoTrack) return

  const [clip] = videoTrack.clips.splice(fromIndex, 1)
  videoTrack.clips.splice(toIndex, 0, clip)

  // Recalculate start times
  let time = 0
  for (const c of videoTrack.clips) {
    c.startTime = time
    time += c.duration
  }
}

function removeFromTimeline(index: number): void {
  if (!project.value) return

  const videoTrack = project.value.timeline.find(t => t.type === 'video')
  if (!videoTrack) return

  videoTrack.clips.splice(index, 1)

  let time = 0
  for (const c of videoTrack.clips) {
    c.startTime = time
    time += c.duration
  }
}

function clearTimeline(): void {
  if (!project.value) return
  const videoTrack = project.value.timeline.find(t => t.type === 'video')
  if (videoTrack) {
    videoTrack.clips = []
  }
}

function autoArrangeTimeline(): void {
  if (!project.value) return

  const videoTrack = project.value.timeline.find(t => t.type === 'video')
  if (!videoTrack) return

  videoTrack.clips = []

  let time = 0
  for (const shot of project.value.shots) {
    if (shot.selectedClipId) {
      const clip = shot.clips.find(c => c.id === shot.selectedClipId)
      if (clip) {
        videoTrack.clips.push({
          id: `timeline-${Date.now()}-${shot.sequence}`,
          clipId: clip.id,
          shotSequence: shot.sequence,
          startTime: time,
          duration: clip.duration,
          thumbnailUrl: clip.thumbnailUrl,
        })
        time += clip.duration
      }
    }
  }

  toastStore.success(t('studio.savedToTimeline'))
}

// ============== Playback (UI only) ==============

function togglePlay(): void {
  isPlaying.value = !isPlaying.value
}

let playbackInterval: number | null = null

watch(isPlaying, (playing) => {
  if (playing) {
    playbackInterval = window.setInterval(() => {
      if (currentTime.value < timelineTotalDuration.value) {
        currentTime.value += 0.1
      } else {
        isPlaying.value = false
        currentTime.value = 0
      }
    }, 100)
  } else if (playbackInterval) {
    window.clearInterval(playbackInterval)
    playbackInterval = null
  }
})

onUnmounted(() => {
  if (playbackInterval) {
    window.clearInterval(playbackInterval)
  }
})

// ============== Compose & Export ==============

function handleCompose(): void {
  const shotsWithoutClips = project.value?.shots.filter(s => !s.selectedClipId) ?? []
  if (shotsWithoutClips.length > 0) {
    toastStore.warning(t('studio.compose.missingClips', { count: shotsWithoutClips.length }))
    return
  }
  showExportModal.value = true
}

function handleExport(): void {
  toastStore.success(t('studio.compose.complete'))
  showExportModal.value = false
}

// ============== Helpers ==============

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  const ms = Math.floor((seconds % 1) * 10)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}.${ms}`
}

function copyPrompt(text: string): void {
  navigator.clipboard.writeText(text)
  toastStore.success(t('studio.promptCopied'))
}

function getModelLabel(value: VideoModel): string {
  const model = VIDEO_MODELS.find(m => m.value === value)
  return locale.value === 'zh-CN' ? (model?.labelZh ?? value) : (model?.label ?? value)
}
</script>

<template>
  <div class="studio-view h-full flex flex-col bg-gray-100 dark:bg-gray-900">
    <!-- Loading State -->
    <div v-if="isLoading" class="flex-1 flex items-center justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500" />
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <p class="text-red-500 mb-4">{{ error }}</p>
        <button class="btn-primary" @click="loadData">Retry</button>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else-if="project">
      <!-- Toolbar -->
      <div class="flex-none h-14 px-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <!-- Left: Playback controls -->
        <div class="flex items-center gap-4">
          <button
            class="w-10 h-10 rounded-full bg-primary-500 hover:bg-primary-600 text-white flex items-center justify-center transition-colors"
            @click="togglePlay"
          >
            <svg v-if="!isPlaying" class="w-5 h-5 ml-0.5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
            <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
            </svg>
          </button>
          <span class="text-sm font-mono text-gray-600 dark:text-gray-400">
            {{ formatTime(currentTime) }} / {{ formatTime(timelineTotalDuration) }}
          </span>
        </div>

        <!-- Right: Actions -->
        <div class="flex items-center gap-2">
          <button class="btn-secondary" @click="showExportModal = true">
            {{ t('studio.exportSettings') }}
          </button>
          <button class="btn-primary" @click="handleCompose">
            {{ t('studio.composeVideo') }}
          </button>
        </div>
      </div>

      <!-- Main Content Area -->
      <div class="flex-1 flex overflow-hidden">
        <!-- Left Panel - Shot List -->
        <div class="w-72 flex-none border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex flex-col">
          <div class="flex-none p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 class="font-semibold text-gray-900 dark:text-white">{{ t('studio.shotList') }}</h3>
          </div>

          <div class="flex-1 overflow-y-auto p-2">
            <div v-if="project.shots.length === 0" class="text-center py-8 text-gray-500">
              <p>{{ t('studio.noShots') }}</p>
              <p class="text-sm mt-2">{{ t('studio.noShotsHint') }}</p>
            </div>

            <div
              v-for="shot in project.shots"
              :key="shot.sequence"
              :class="[
                'p-3 rounded-lg cursor-pointer transition-all mb-2',
                selectedShotSequence === shot.sequence
                  ? 'bg-primary-100 dark:bg-primary-900/30 border-2 border-primary-500'
                  : 'bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 border-2 border-transparent',
              ]"
              @click="selectShot(shot.sequence)"
            >
              <div class="flex items-start gap-3">
                <span
                  :class="[
                    'w-7 h-7 rounded-full flex items-center justify-center text-xs font-medium flex-shrink-0',
                    shot.selectedClipId
                      ? 'bg-green-500 text-white'
                      : shot.clips.length > 0
                        ? 'bg-yellow-500 text-white'
                        : 'bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-300',
                  ]"
                >
                  {{ shot.selectedClipId ? '✓' : shot.sequence }}
                </span>
                <div class="flex-1 min-w-0">
                  <p class="font-medium text-gray-900 dark:text-white truncate">
                    {{ shot.name || t('studio.shotNumber', { number: shot.sequence }) }}
                  </p>
                  <p class="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">
                    {{ shot.description_cn }}
                  </p>
                  <p class="text-xs mt-1">
                    <span
                      :class="[
                        'px-1.5 py-0.5 rounded',
                        shot.clips.length > 0
                          ? 'bg-primary-100 dark:bg-primary-900/50 text-primary-700 dark:text-primary-300'
                          : 'bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-400',
                      ]"
                    >
                      {{ shot.clips.length > 0 ? t('studio.clipsCount', { count: shot.clips.length }) : t('studio.noClip') }}
                    </span>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Center Area - Preview + Gallery -->
        <div class="flex-1 flex flex-col overflow-hidden">
          <!-- Video Preview -->
          <div class="flex-none p-4">
            <div class="bg-black rounded-lg overflow-hidden aspect-video flex items-center justify-center">
              <div v-if="!selectedClip" class="text-gray-500">
                {{ t('studio.noPreview') }}
              </div>
              <div v-else class="text-white text-center">
                <p class="text-lg font-medium">{{ t('studio.shotNumber', { number: selectedClip.shotSequence }) }}</p>
                <p class="text-sm text-gray-400 mt-1">{{ getModelLabel(selectedClip.model) }} · {{ selectedClip.duration }}s</p>
              </div>
            </div>
          </div>

          <!-- Video Gallery -->
          <div class="flex-1 overflow-hidden flex flex-col border-t border-gray-200 dark:border-gray-700">
            <div class="flex-none px-4 py-2 bg-gray-50 dark:bg-gray-800 flex items-center justify-between">
              <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('studio.videoGallery') }}</h4>
              <span class="text-xs text-gray-500">{{ t('studio.dragToTimeline') }}</span>
            </div>
            <div class="flex-1 overflow-y-auto p-4">
              <div v-if="!selectedShot" class="text-center py-8 text-gray-500">
                {{ t('studio.noPreview') }}
              </div>
              <div v-else-if="selectedShot.clips.length === 0" class="text-center py-8 text-gray-500">
                <p>{{ t('studio.galleryEmpty') }}</p>
                <p class="text-sm mt-2">{{ t('studio.galleryHint') }}</p>
              </div>
              <div v-else class="grid grid-cols-3 gap-3">
                <div
                  v-for="clip in selectedShot.clips"
                  :key="clip.id"
                  :class="[
                    'relative aspect-video rounded-lg overflow-hidden cursor-move border-2 transition-all group',
                    selectedShot.selectedClipId === clip.id
                      ? 'border-primary-500 ring-2 ring-primary-500/30'
                      : 'border-gray-300 dark:border-gray-600 hover:border-gray-400',
                  ]"
                  draggable="true"
                  @dragstart="handleGalleryDragStart($event, clip)"
                  @dragend="handleGalleryDragEnd"
                >
                  <!-- Thumbnail Placeholder -->
                  <div class="absolute inset-0 bg-gray-800 flex items-center justify-center">
                    <div class="text-center text-gray-400">
                      <p class="text-xs">{{ getModelLabel(clip.model) }}</p>
                      <p class="text-lg font-bold">{{ clip.duration }}s</p>
                    </div>
                  </div>

                  <!-- Selected badge -->
                  <div v-if="selectedShot.selectedClipId === clip.id" class="absolute top-1 left-1">
                    <span class="px-1.5 py-0.5 bg-primary-500 text-white text-xs rounded font-medium">
                      {{ t('studio.selectedVideo') }}
                    </span>
                  </div>

                  <!-- Hover overlay -->
                  <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                    <button
                      class="px-2 py-1 bg-primary-500 hover:bg-primary-600 text-white text-xs rounded transition-colors"
                      @click.stop="selectClipForShot(clip)"
                    >
                      {{ t('studio.selectVideo') }}
                    </button>
                    <button
                      class="px-2 py-1 bg-red-500 hover:bg-red-600 text-white text-xs rounded transition-colors"
                      @click.stop="deleteClipHandler(clip)"
                    >
                      {{ t('studio.deleteVideo') }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Panel - Properties -->
        <div class="w-80 flex-none border-l border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex flex-col overflow-hidden">
          <div v-if="!selectedShot" class="flex-1 flex items-center justify-center text-gray-500">
            {{ t('studio.noPreview') }}
          </div>
          <template v-else>
            <!-- Shot Info -->
            <div class="flex-none p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 class="font-semibold text-gray-900 dark:text-white mb-3">{{ t('studio.shotInfo') }}</h3>
              <p class="font-medium text-gray-800 dark:text-gray-200">
                {{ selectedShot.name || t('studio.shotNumber', { number: selectedShot.sequence }) }}
              </p>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {{ selectedShot.description_cn }}
              </p>
            </div>

            <!-- Generate Settings -->
            <div class="flex-none p-4 border-b border-gray-200 dark:border-gray-700 space-y-4">
              <div>
                <label class="label">{{ t('studio.model') }}</label>
                <select v-model="generateSettings.model" class="input w-full">
                  <option v-for="m in VIDEO_MODELS" :key="m.value" :value="m.value">
                    {{ locale === 'zh-CN' ? m.labelZh : m.label }}
                  </option>
                </select>
              </div>

              <div>
                <label class="label">
                  {{ t('studio.duration') }}: {{ t('studio.durationSeconds', { seconds: generateSettings.duration }) }}
                </label>
                <input
                  v-model.number="generateSettings.duration"
                  type="range"
                  min="2"
                  max="10"
                  step="1"
                  class="w-full"
                />
              </div>

              <button
                class="btn-primary w-full"
                :disabled="isGenerating"
                @click="handleGenerateVideo"
              >
                <span v-if="isGenerating" class="flex items-center justify-center gap-2">
                  <span class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                  {{ t('studio.generating') }}
                </span>
                <span v-else>
                  {{ selectedShot.clips.length > 0 ? t('studio.generateMore') : t('studio.generate') }}
                </span>
              </button>
            </div>

            <!-- Prompt Preview -->
            <div class="flex-1 overflow-y-auto p-4">
              <h4 class="font-medium text-gray-900 dark:text-white mb-3">{{ t('studio.promptPreview') }}</h4>
              <div v-if="currentShotPrompt" class="space-y-3">
                <div>
                  <div class="flex items-center justify-between mb-1">
                    <span class="text-xs text-gray-500">{{ t('studio.prompt') }}</span>
                    <button
                      class="text-xs text-primary-500 hover:text-primary-600"
                      @click="copyPrompt(currentShotPrompt.prompt)"
                    >
                      {{ t('studio.copyPrompt') }}
                    </button>
                  </div>
                  <p class="text-xs text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 rounded p-2 max-h-32 overflow-y-auto">
                    {{ currentShotPrompt.prompt }}
                  </p>
                </div>

                <div v-if="currentShotPrompt.negative_prompt">
                  <div class="flex items-center justify-between mb-1">
                    <span class="text-xs text-gray-500">{{ t('studio.negativePrompt') }}</span>
                    <button
                      class="text-xs text-primary-500 hover:text-primary-600"
                      @click="copyPrompt(currentShotPrompt.negative_prompt)"
                    >
                      {{ t('studio.copyPrompt') }}
                    </button>
                  </div>
                  <p class="text-xs text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 rounded p-2 max-h-24 overflow-y-auto">
                    {{ currentShotPrompt.negative_prompt }}
                  </p>
                </div>
              </div>
              <div v-else class="text-sm text-gray-500">
                {{ t('studio.noPreview') }}
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- Timeline -->
      <div class="flex-none h-48 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex flex-col">
        <!-- Timeline Header -->
        <div class="flex-none h-10 px-4 flex items-center justify-between border-b border-gray-200 dark:border-gray-700">
          <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('studio.timeline') }}</h4>
          <div class="flex items-center gap-2">
            <button class="text-xs text-primary-500 hover:text-primary-600" @click="autoArrangeTimeline">
              {{ t('studio.autoArrange') }}
            </button>
            <button class="text-xs text-red-500 hover:text-red-600" @click="clearTimeline">
              {{ t('studio.clearTimeline') }}
            </button>
          </div>
        </div>

        <!-- Time Ruler -->
        <div class="flex-none h-6 flex items-center px-4 bg-gray-50 dark:bg-gray-700/50 border-b border-gray-200 dark:border-gray-700">
          <div class="w-20 flex-shrink-0" />
          <div class="flex-1 flex">
            <template v-for="i in Math.max(Math.ceil(timelineTotalDuration / 5) + 1, 6)" :key="i">
              <span class="text-xs text-gray-400 w-24">{{ formatTime((i - 1) * 5) }}</span>
            </template>
          </div>
        </div>

        <!-- Video Track -->
        <div
          class="flex-1 flex items-center px-4 gap-1 overflow-x-auto"
          @dragover="handleTimelineDragOver"
          @drop="handleTimelineDrop"
        >
          <div class="w-20 flex-shrink-0 text-xs text-gray-500 dark:text-gray-400">
            {{ t('studio.videoTrack') }}
          </div>
          <div class="flex-1 flex items-center gap-1 h-16">
            <div
              v-for="(clip, index) in videoTrackClips"
              :key="clip.id"
              :style="{ width: `${Math.max(clip.duration * 20, 60)}px` }"
              class="h-full rounded bg-primary-500/80 hover:bg-primary-600/80 flex-shrink-0 cursor-move relative group transition-colors"
              draggable="true"
              @dragstart="handleTimelineDragStart($event, index)"
              @dragend="handleTimelineDragEnd"
            >
              <div class="absolute inset-0 flex items-center justify-center text-white text-xs font-medium">
                {{ t('studio.shotNumber', { number: clip.shotSequence }) }}
              </div>
              <div class="absolute bottom-1 right-1 text-xs text-white/80">
                {{ clip.duration }}s
              </div>
              <button
                class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 hover:bg-red-600 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-xs"
                @click.stop="removeFromTimeline(index)"
              >
                ×
              </button>
            </div>

            <div
              v-if="draggingFromGallery || videoTrackClips.length === 0"
              class="h-full min-w-32 border-2 border-dashed border-primary-400 dark:border-primary-600 rounded flex items-center justify-center text-primary-500 text-xs"
            >
              {{ t('studio.timelineEmpty') }}
            </div>
          </div>
        </div>

        <!-- Audio Track (placeholder) -->
        <div class="flex-none h-12 flex items-center px-4 border-t border-gray-200 dark:border-gray-700">
          <div class="w-20 flex-shrink-0 text-xs text-gray-500 dark:text-gray-400">
            {{ t('studio.audioTrack') }}
          </div>
          <div class="flex-1 h-8 bg-gray-100 dark:bg-gray-700 rounded opacity-50" />
        </div>
      </div>
    </template>

    <!-- Export Modal -->
    <Teleport to="body">
      <div
        v-if="showExportModal"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
        @click.self="showExportModal = false"
      >
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-md p-6">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            {{ t('studio.export.title') }}
          </h3>

          <div class="space-y-4">
            <div>
              <label class="label">{{ t('studio.export.format') }}</label>
              <select v-model="exportSettings.format" class="input w-full">
                <option v-for="f in EXPORT_FORMATS" :key="f.value" :value="f.value">
                  {{ locale === 'zh-CN' ? f.labelZh : f.label }}
                </option>
              </select>
            </div>

            <div>
              <label class="label">{{ t('studio.export.resolution') }}</label>
              <select v-model="exportSettings.resolution" class="input w-full">
                <option v-for="r in EXPORT_RESOLUTIONS" :key="r.value" :value="r.value">
                  {{ locale === 'zh-CN' ? r.labelZh : r.label }}
                </option>
              </select>
            </div>

            <div>
              <label class="label">{{ t('studio.export.fps') }}</label>
              <select v-model="exportSettings.fps" class="input w-full">
                <option v-for="f in EXPORT_FPS" :key="f.value" :value="f.value">
                  {{ locale === 'zh-CN' ? f.labelZh : f.label }}
                </option>
              </select>
            </div>

            <div class="flex items-center gap-2">
              <input
                id="include-audio"
                v-model="exportSettings.includeAudio"
                type="checkbox"
                class="rounded border-gray-300 text-primary-500 focus:ring-primary-500"
              />
              <label for="include-audio" class="text-sm text-gray-700 dark:text-gray-300">
                {{ t('studio.export.includeAudio') }}
              </label>
            </div>
          </div>

          <div class="flex justify-end gap-3 mt-6">
            <button class="btn-secondary" @click="showExportModal = false">
              {{ t('studio.export.cancel') }}
            </button>
            <button class="btn-primary" @click="handleExport">
              {{ t('studio.export.export') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.studio-view {
  height: 100%;
}
</style>
