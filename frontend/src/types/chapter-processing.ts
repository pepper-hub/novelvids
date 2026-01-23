/**
 * 章节处理相关类型定义
 * 支持角色提取、资产管理、分镜处理等功能
 */

// ==================== 视觉状态 ====================

export interface VisualState {
  chapterNumber: number
  aliasUsed: string
  currentState: string // 英文 prompt 描述
}

// ==================== 别名关系 ====================

export interface AliasRelation {
  alias: string
  canonicalName: string
  reason: string
  chapterDiscovered: number
}

// ==================== 提取的实体 ====================

export interface ExtractedEntity {
  name: string
  entityType: 'Person' | 'Object'
  visualDesc: string
  actionContext: string
}

// ==================== 角色资产 ====================

export interface CharacterAsset {
  canonicalName: string
  characterType: 'Person' | 'Object'
  baseTraits: string // 固有属性（英文）
  aliases: string[]
  visualStates: VisualState[]
  lastUpdatedChapter: number
}

// ==================== 章节提取结果 ====================

export interface ChapterExtractionResult {
  chapterNumber: number
  entities: ExtractedEntity[]
  aliasRelations: AliasRelation[]
  characterPrompts: Record<string, string>
}

// ==================== 角色 Prompts ====================

export interface CharacterPrompts {
  novelId: string
  chapterNumber: number | null
  prompts: Record<string, string>
}

// ==================== API 请求类型 ====================

export interface ProcessChapterRequest {
  chapter_id: string
}

export interface ProcessChaptersBatchRequest {
  novel_id: string
  start_chapter: number
  end_chapter?: number | null
}

// ==================== 处理状态 ====================

export type ProcessingStatus = 'idle' | 'processing' | 'completed' | 'failed'

export interface ProcessingProgress {
  status: ProcessingStatus
  currentChapter: number
  totalChapters: number
  message: string
}

// ==================== 工作流步骤（用于未来扩展） ====================

export type WorkflowStep = 'extraction' | 'storyboard' | 'generation'

export interface WorkflowState {
  currentStep: WorkflowStep
  completedSteps: WorkflowStep[]
  canProceed: boolean
}
