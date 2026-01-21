"""角色相关的 API 端点。"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from novelvids.api.dependencies import (
    get_character_repository,
    get_current_user_id,
    get_novel_repository,
)
from novelvids.application.dto import (
    CharacterCreateDTO,
    CharacterResponseDTO,
    CharacterUpdateDTO,
)
from novelvids.infrastructure.database.repositories import (
    TortoiseCharacterRepository,
    TortoiseNovelRepository,
)

router = APIRouter(prefix="/novels/{novel_id}/characters", tags=["角色"])


async def verify_novel_access(
    novel_id: UUID,
    user_id: UUID,
    novel_repo: TortoiseNovelRepository,
) -> None:
    """验证用户是否有权限访问该小说。"""
    novel = await novel_repo.get_by_id(novel_id)
    if novel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="小说不存在")
    if novel.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="拒绝访问")


@router.get("", response_model=list[CharacterResponseDTO])
async def list_characters(
    novel_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    novel_repo: Annotated[TortoiseNovelRepository, Depends(get_novel_repository)],
    character_repo: Annotated[TortoiseCharacterRepository, Depends(get_character_repository)],
):
    """列出小说的所有角色。"""
    await verify_novel_access(novel_id, user_id, novel_repo)
    characters = await character_repo.get_by_novel_id(novel_id)
    return [CharacterResponseDTO.model_validate(c) for c in characters]


@router.post("", response_model=CharacterResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_character(
    novel_id: UUID,
    data: CharacterCreateDTO,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    novel_repo: Annotated[TortoiseNovelRepository, Depends(get_novel_repository)],
    character_repo: Annotated[TortoiseCharacterRepository, Depends(get_character_repository)],
):
    """为小说创建新角色。"""
    await verify_novel_access(novel_id, user_id, novel_repo)

    # 检查角色名是否已存在
    existing = await character_repo.get_by_name(novel_id, data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该名称的角色已存在",
        )

    character = await character_repo.create(novel_id=novel_id, **data.model_dump())
    return CharacterResponseDTO.model_validate(character)


@router.get("/{character_id}", response_model=CharacterResponseDTO)
async def get_character(
    novel_id: UUID,
    character_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    novel_repo: Annotated[TortoiseNovelRepository, Depends(get_novel_repository)],
    character_repo: Annotated[TortoiseCharacterRepository, Depends(get_character_repository)],
):
    """获取特定角色。"""
    await verify_novel_access(novel_id, user_id, novel_repo)
    character = await character_repo.get_by_id(character_id)
    if character is None or character.novel_id != novel_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    return CharacterResponseDTO.model_validate(character)


@router.put("/{character_id}", response_model=CharacterResponseDTO)
async def update_character(
    novel_id: UUID,
    character_id: UUID,
    data: CharacterUpdateDTO,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    novel_repo: Annotated[TortoiseNovelRepository, Depends(get_novel_repository)],
    character_repo: Annotated[TortoiseCharacterRepository, Depends(get_character_repository)],
):
    """更新角色。"""
    await verify_novel_access(novel_id, user_id, novel_repo)
    character = await character_repo.get_by_id(character_id)
    if character is None or character.novel_id != novel_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")

    update_data = data.model_dump(exclude_unset=True)
    updated = await character_repo.update(character_id, update_data)
    return CharacterResponseDTO.model_validate(updated)


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(
    novel_id: UUID,
    character_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    novel_repo: Annotated[TortoiseNovelRepository, Depends(get_novel_repository)],
    character_repo: Annotated[TortoiseCharacterRepository, Depends(get_character_repository)],
):
    """删除角色。"""
    await verify_novel_access(novel_id, user_id, novel_repo)
    character = await character_repo.get_by_id(character_id)
    if character is None or character.novel_id != novel_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    await character_repo.delete(character_id)
