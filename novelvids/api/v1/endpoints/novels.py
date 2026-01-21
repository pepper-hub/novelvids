"""小说相关的 API 端点。"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from novelvids.api.dependencies import (
    get_current_user_id,
    get_novel_repository,
)
from novelvids.application.dto import (
    NovelCreateDTO,
    NovelDetailDTO,
    NovelResponseDTO,
    NovelUpdateDTO,
    PaginatedResponseDTO,
)
from novelvids.infrastructure.database.repositories import TortoiseNovelRepository

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="小说不存在")
    if novel.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="拒绝访问")
    return NovelDetailDTO.model_validate(novel)


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="小说不存在")
    if novel.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="拒绝访问")

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="小说不存在")
    if novel.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="拒绝访问")

    await novel_repo.delete(novel_id)
