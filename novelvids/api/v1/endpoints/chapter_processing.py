"""章节处理相关的 API 端点。

提供章节角色提取、资产管理等功能。
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, status

from novelvids.api.dependencies import (
    get_chapter_repository,
    get_current_user_id,
    get_novel_repository,
)
from novelvids.api.exceptions import (
    BadRequestException,
    NotFoundException,
    PermissionDeniedException,
)
from novelvids.application.dto import (
    AliasRelationDTO,
    ChapterExtractionResultDTO,
    CharacterAssetDTO,
    CharacterPromptsDTO,
    ExtractedEntityDTO,
    ProcessChapterDTO,
    ProcessChaptersBatchDTO,
    VisualStateDTO,
)
from novelvids.application.services.chapter_processing import ChapterProcessingService
from novelvids.core.config import settings
from novelvids.domain.services.character_extraction import OpenAICompatibleClient
from novelvids.infrastructure.database.models import TaskStatus, WorkflowStatus
from novelvids.infrastructure.database.repositories import (
    TortoiseChapterRepository,
    TortoiseNovelRepository,
)

router = APIRouter(prefix="/chapter-processing", tags=["章节处理"])


def get_chapter_processing_service() -> ChapterProcessingService:
    """获取章节处理服务实例。"""
    llm_client = OpenAICompatibleClient(
        api_key=settings.llm.api_key,
        base_url=settings.llm.base_url,
        model_name=settings.llm.model_name,
    )
    return ChapterProcessingService(llm_client)


@router.post("/process", response_model=ChapterExtractionResultDTO)
async def process_chapter(
    data: ProcessChapterDTO,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    chapter_repo: Annotated[TortoiseChapterRepository, Depends(get_chapter_repository)],
    novel_repo: Annotated[TortoiseNovelRepository, Depends(get_novel_repository)],
):
    """
    处理单个章节，提取角色并更新资产库。

    这个接口会：
    1. 调用 LLM 从章节文本中提取实体和别名关系
    2. 使用图算法进行实体归一化
    3. 提取角色的视觉状态（衣着、动作等）
    4. 更新数据库中的角色资产
    5. 返回提取结果和生成的 prompts
    """
    # 验证章节存在且用户有权限
    chapter = await chapter_repo.get_by_id(data.chapter_id)
    if chapter is None:
        raise NotFoundException(code="CHAPTER_NOT_FOUND", message="章节不存在")

    novel = await novel_repo.get_by_id(chapter.novel_id)
    if novel is None or novel.user_id != user_id:
        raise PermissionDeniedException(code="PERMISSION_DENIED", message="拒绝访问")

    # 检查 LLM 配置
    if not settings.llm.api_key:
        raise BadRequestException(
            code="LLM_NOT_CONFIGURED",
            message="LLM API 未配置，请设置 LLM_API_KEY 环境变量",
        )

    # 处理章节
    service = get_chapter_processing_service()
    result = await service.process_single_chapter(data.chapter_id)

    if result is None:
        raise NotFoundException(code="CHAPTER_NOT_FOUND", message="章节不存在")

    # 更新章节状态
    await chapter_repo.update(data.chapter_id, {"status": TaskStatus.COMPLETED})

    return ChapterExtractionResultDTO(
        chapter_number=result.chapter_number,
        entities=[
            ExtractedEntityDTO(
                name=e.name,
                entity_type=e.entity_type,
                visual_desc=e.visual_desc,
                action_context=e.action_context,
            )
            for e in result.entities
        ],
        alias_relations=[
            AliasRelationDTO(
                alias=r.alias,
                canonical_name=r.canonical_name,
                reason=r.reason,
                chapter_discovered=r.chapter_discovered,
            )
            for r in result.alias_relations
        ],
        character_prompts=result.character_prompts,
    )


@router.post("/process-batch", response_model=list[ChapterExtractionResultDTO])
async def process_chapters_batch(
    data: ProcessChaptersBatchDTO,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    novel_repo: Annotated[TortoiseNovelRepository, Depends(get_novel_repository)],
):
    """
    批量处理章节（按顺序）。

    增量式处理：每处理完一章，角色资产库会更新，
    后续章节会基于已知角色进行提取和归一化。
    """
    # 验证小说存在且用户有权限
    novel = await novel_repo.get_by_id(data.novel_id)
    if novel is None:
        raise NotFoundException(code="NOVEL_NOT_FOUND", message="小说不存在")
    if novel.user_id != user_id:
        raise PermissionDeniedException(code="PERMISSION_DENIED", message="拒绝访问")

    # 检查工作流状态 - 必须已分章才能提取角色
    if not novel.can_extract_characters():
        raise BadRequestException(
            code="WORKFLOW_STATE_ERROR",
            message=f"请先处理小说以提取章节。当前状态：{novel.workflow_status}",
        )

    # 检查 LLM 配置
    if not settings.llm.api_key:
        raise BadRequestException(
            code="LLM_NOT_CONFIGURED",
            message="LLM API 未配置，请设置 LLM_API_KEY 环境变量",
        )

    # 处理章节
    service = get_chapter_processing_service()
    results = await service.process_chapters_batch(
        novel_id=data.novel_id,
        start_chapter=data.start_chapter,
        end_chapter=data.end_chapter,
    )

    # 更新工作流状态为已提取角色
    if results:
        await novel_repo.update(
            data.novel_id,
            {"workflow_status": WorkflowStatus.CHARACTERS_EXTRACTED},
        )

    return [
        ChapterExtractionResultDTO(
            chapter_number=r.chapter_number,
            entities=[
                ExtractedEntityDTO(
                    name=e.name,
                    entity_type=e.entity_type,
                    visual_desc=e.visual_desc,
                    action_context=e.action_context,
                )
                for e in r.entities
            ],
            alias_relations=[
                AliasRelationDTO(
                    alias=rel.alias,
                    canonical_name=rel.canonical_name,
                    reason=rel.reason,
                    chapter_discovered=rel.chapter_discovered,
                )
                for rel in r.alias_relations
            ],
            character_prompts=r.character_prompts,
        )
        for r in results
    ]


@router.post("/process-batch-async", status_code=status.HTTP_202_ACCEPTED)
async def process_chapters_batch_async(
    data: ProcessChaptersBatchDTO,
    background_tasks: BackgroundTasks,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    novel_repo: Annotated[TortoiseNovelRepository, Depends(get_novel_repository)],
):
    """
    异步批量处理章节。

    立即返回，在后台处理。适用于大量章节的处理。
    """
    # 验证小说存在且用户有权限
    novel = await novel_repo.get_by_id(data.novel_id)
    if novel is None:
        raise NotFoundException(code="NOVEL_NOT_FOUND", message="小说不存在")
    if novel.user_id != user_id:
        raise PermissionDeniedException(code="PERMISSION_DENIED", message="拒绝访问")

    # 检查工作流状态 - 必须已分章才能提取角色
    if not novel.can_extract_characters():
        raise BadRequestException(
            code="WORKFLOW_STATE_ERROR",
            message=f"请先处理小说以提取章节。当前状态：{novel.workflow_status}",
        )

    # 检查 LLM 配置
    if not settings.llm.api_key:
        raise BadRequestException(
            code="LLM_NOT_CONFIGURED",
            message="LLM API 未配置，请设置 LLM_API_KEY 环境变量",
        )

    # 更新小说状态为处理中
    await novel_repo.update(data.novel_id, {"status": TaskStatus.RUNNING})

    # 添加后台任务
    async def process_in_background():
        service = get_chapter_processing_service()
        try:
            results = await service.process_chapters_batch(
                novel_id=data.novel_id,
                start_chapter=data.start_chapter,
                end_chapter=data.end_chapter,
            )
            # 更新状态
            update_data = {"status": TaskStatus.COMPLETED}
            if results:
                update_data["workflow_status"] = WorkflowStatus.CHARACTERS_EXTRACTED
            await novel_repo.update(data.novel_id, update_data)
        except Exception:
            await novel_repo.update(data.novel_id, {"status": TaskStatus.FAILED})

    background_tasks.add_task(process_in_background)

    return {
        "message": "处理任务已提交",
        "novel_id": str(data.novel_id),
        "start_chapter": data.start_chapter,
        "end_chapter": data.end_chapter,
    }


@router.get("/prompts/{novel_id}", response_model=CharacterPromptsDTO)
async def get_character_prompts(
    novel_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    novel_repo: Annotated[TortoiseNovelRepository, Depends(get_novel_repository)],
    chapter_number: int | None = None,
):
    """
    获取角色的图像生成 prompts。

    返回格式：Base Traits + Chapter State
    例如：(Base: Young man, pale face) + wearing imperial dragon robe, sitting on throne
    """
    # 验证小说存在且用户有权限
    novel = await novel_repo.get_by_id(novel_id)
    if novel is None:
        raise NotFoundException(code="NOVEL_NOT_FOUND", message="小说不存在")
    if novel.user_id != user_id:
        raise PermissionDeniedException(code="PERMISSION_DENIED", message="拒绝访问")

    service = get_chapter_processing_service()
    prompts = await service.get_character_prompts(novel_id, chapter_number)

    return CharacterPromptsDTO(
        novel_id=novel_id,
        chapter_number=chapter_number,
        prompts=prompts,
    )


@router.get("/assets/{novel_id}", response_model=list[CharacterAssetDTO])
async def get_character_assets(
    novel_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    novel_repo: Annotated[TortoiseNovelRepository, Depends(get_novel_repository)],
):
    """
    获取小说的所有角色资产。

    包含角色的固有属性、别名列表和各章节的视觉状态历史。
    """
    # 验证小说存在且用户有权限
    novel = await novel_repo.get_by_id(novel_id)
    if novel is None:
        raise NotFoundException(code="NOVEL_NOT_FOUND", message="小说不存在")
    if novel.user_id != user_id:
        raise PermissionDeniedException(code="PERMISSION_DENIED", message="拒绝访问")

    service = get_chapter_processing_service()
    assets = await service.asset_manager.load_assets_from_db(novel_id)

    return [
        CharacterAssetDTO(
            canonical_name=asset.canonical_name,
            character_type=asset.character_type,
            base_traits=asset.base_traits,
            aliases=asset.aliases,
            visual_states=[
                VisualStateDTO(
                    chapter_number=s.chapter_number,
                    alias_used=s.alias_used,
                    current_state=s.current_state,
                )
                for s in asset.visual_states
            ],
            last_updated_chapter=asset.last_updated_chapter,
        )
        for asset in assets.values()
    ]
