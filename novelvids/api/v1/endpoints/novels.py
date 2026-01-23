"""小说相关的 API 端点。"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from novelvids.api.dependencies import (
    get_current_user_id,
    get_chapter_repository,
    get_novel_repository,
)
from novelvids.application.dto import (
    NovelCreateDTO,
    NovelDetailDTO,
    NovelResponseDTO,
    NovelUpdateDTO,
    PaginatedResponseDTO,
)
from novelvids.domain.services.nlp.service import ChapterRecognitionService
from novelvids.domain.services.nlp.strategies import RegexChapterRecognitionStrategy
from novelvids.infrastructure.database.models import TaskStatus, WorkflowStatus
from novelvids.infrastructure.database.repositories import (
    TortoiseChapterRepository,
    TortoiseNovelRepository,
)
from novelvids.api.exceptions import (
    BadRequestException,
    NotFoundException,
    PermissionDeniedException,
    ConflictException,
)

router = APIRouter(prefix="/novels", tags=["小说"])


@router.get("", response_model=PaginatedResponseDTO)
async def list_novels(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    novel_repo: Annotated[TortoiseNovelRepository, Depends(get_novel_repository)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """列出当前用户的所有小说。"""
    skip = (page - 1) * page_size
    novels = await novel_repo.get_all(skip=skip, limit=page_size, filters={"user_id": user_id})
    total = await novel_repo.count(filters={"user_id": user_id})
    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponseDTO(
        items=[NovelResponseDTO.model_validate(n) for n in novels],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("", response_model=NovelResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_novel(
    data: NovelCreateDTO,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    novel_repo: Annotated[TortoiseNovelRepository, Depends(get_novel_repository)],
):
    """创建新小说。"""
    novel = await novel_repo.create(
        title=data.title,
        content=data.content,
        author=data.author,
        user_id=user_id,
    )
    return NovelResponseDTO.model_validate(novel)


@router.get("/{novel_id}", response_model=NovelDetailDTO)
async def get_novel(
    novel_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    novel_repo: Annotated[TortoiseNovelRepository, Depends(get_novel_repository)],
):
    """根据 ID 获取特定小说。"""
    novel = await novel_repo.get_by_id(novel_id)
    if novel is None:
        raise NotFoundException(code="NOVEL_NOT_FOUND", message="Novel not found")
    if novel.user_id != user_id:
        raise PermissionDeniedException(code="PERMISSION_DENIED", message="Access denied")

    # 构建包含工作流状态的响应
    data = {
        "id": novel.id,
        "title": novel.title,
        "author": novel.author,
        "status": novel.status,
        "workflow_status": novel.workflow_status,
        "total_chapters": novel.total_chapters,
        "processed_chapters": novel.processed_chapters,
        "created_at": novel.created_at,
        "updated_at": novel.updated_at,
        "content": novel.content,
        "metadata": novel.metadata,
        "can_extract_chapters": novel.can_extract_chapters(),
        "can_extract_characters": novel.can_extract_characters(),
        "can_create_storyboard": novel.can_create_storyboard(),
        "can_generate_video": novel.can_generate_video(),
    }
    return NovelDetailDTO(**data)


@router.put("/{novel_id}", response_model=NovelResponseDTO)
async def update_novel(
    novel_id: UUID,
    data: NovelUpdateDTO,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    novel_repo: Annotated[TortoiseNovelRepository, Depends(get_novel_repository)],
):
    """更新小说。"""
    novel = await novel_repo.get_by_id(novel_id)
    if novel is None:
        raise NotFoundException(code="NOVEL_NOT_FOUND", message="Novel not found")
    if novel.user_id != user_id:
        raise PermissionDeniedException(code="PERMISSION_DENIED", message="Access denied")

    update_data = data.model_dump(exclude_unset=True)
    updated = await novel_repo.update(novel_id, update_data)
    return NovelResponseDTO.model_validate(updated)


@router.delete("/{novel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_novel(
    novel_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    novel_repo: Annotated[TortoiseNovelRepository, Depends(get_novel_repository)],
):
    """删除小说。"""
    novel = await novel_repo.get_by_id(novel_id)
    if novel is None:
        raise NotFoundException(code="NOVEL_NOT_FOUND", message="Novel not found")
    if novel.user_id != user_id:
        raise PermissionDeniedException(code="PERMISSION_DENIED", message="Access denied")

    await novel_repo.delete(novel_id)


@router.post("/{novel_id}/extract-chapters", response_model=NovelResponseDTO)
async def extract_chapters(
    novel_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    novel_repo: Annotated[TortoiseNovelRepository, Depends(get_novel_repository)],
    chapter_repo: Annotated[TortoiseChapterRepository, Depends(get_chapter_repository)],
):
    """提取小说章节。"""
    novel = await novel_repo.get_by_id(novel_id)
    if novel is None:
        raise NotFoundException(code="NOVEL_NOT_FOUND", message="Novel not found")
    if novel.user_id != user_id:
        raise PermissionDeniedException(code="PERMISSION_DENIED", message="Access denied")

    if novel.status == TaskStatus.RUNNING:
        raise ConflictException(code="NOVEL_PROCESSING", message="Novel is already being processed")

    # 检查工作流状态
    if not novel.can_extract_chapters():
        raise BadRequestException(
            code="WORKFLOW_STATE_ERROR",
            message=f"Cannot extract chapters in current workflow state: {novel.workflow_status}"
        )

    # 更新状态为运行中
    novel.status = TaskStatus.RUNNING
    await novel.save()

    try:
        # 使用 NLP 服务识别章节
        service = ChapterRecognitionService(RegexChapterRecognitionStrategy())
        parsed_chapters = service.process_novel(novel.content)

        # 如果没有识别到章节，默认整个小说作为一个章节
        if not parsed_chapters:
            parsed_chapters = [
                type("ParsedChapterResult", (), {
                    "title": "第一章",
                    "content": novel.content,
                    "start_index": 0,
                    "end_index": len(novel.content),
                    "confidence": 1.0
                })()
            ]

        # 创建章节记录
        for idx, chapter_result in enumerate(parsed_chapters):
            await chapter_repo.create(
                novel_id=novel.id,
                number=idx + 1,
                title=chapter_result.title,
                content=chapter_result.content,
            )

        # 更新小说的总章节数和状态
        await novel.update_from_dict({
            "total_chapters": len(parsed_chapters),
            "status": TaskStatus.COMPLETED,
            "workflow_status": WorkflowStatus.CHAPTERS_EXTRACTED,
        })
        await novel.save()

    except Exception as e:
        novel.status = TaskStatus.FAILED
        await novel.save()
        raise e

    return NovelResponseDTO.model_validate(novel)
