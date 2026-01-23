"""角色资产管理服务。

负责角色资产的持久化、缓存和状态管理。
"""

from uuid import UUID

from novelvids.domain.models.character_asset import (
    ChapterExtractionResult,
    CharacterAsset,
    VisualState,
)
from novelvids.domain.services.character_extraction import (
    CharacterExtractionService,
    LLMClient,
)
from novelvids.infrastructure.database.models import ChapterModel, CharacterModel


class CharacterAssetManager:
    """角色资产管理器。

    负责：
    1. 从数据库加载/保存角色资产
    2. 协调角色提取服务
    3. 生成最终的图像生成 prompts
    """

    def __init__(self, extraction_service: CharacterExtractionService):
        self.extraction_service = extraction_service

    async def load_assets_from_db(self, novel_id: UUID) -> dict[str, CharacterAsset]:
        """从数据库加载小说的所有角色资产。"""
        characters = await CharacterModel.filter(novel_id=novel_id)
        assets: dict[str, CharacterAsset] = {}

        for char in characters:
            # 优先从新字段读取，兼容旧数据
            visual_states_data = char.visual_states or []
            aliases_data = char.aliases or []

            # 如果新字段为空，尝试从 metadata 读取
            if not visual_states_data:
                metadata = char.metadata or {}
                asset_data = metadata.get("asset_data", {})
                if asset_data:
                    visual_states_data = asset_data.get("visual_states", [])
                    aliases_data = asset_data.get("aliases", [])

            asset = CharacterAsset(
                canonical_name=char.name,
                character_type="Person",
                base_traits=char.appearance or "",
                aliases=aliases_data,
                visual_states=[VisualState.from_dict(s) for s in visual_states_data],
                last_updated_chapter=char.last_updated_chapter,
            )

            assets[char.name] = asset

        return assets

    async def save_assets_to_db(self, novel_id: UUID, assets: dict[str, CharacterAsset]) -> None:
        """将角色资产保存到数据库。"""
        for name, asset in assets.items():
            char = await CharacterModel.get_or_none(novel_id=novel_id, name=name)

            visual_states_data = [s.to_dict() for s in asset.visual_states]

            if char is None:
                # 创建新角色
                await CharacterModel.create(
                    novel_id=novel_id,
                    name=name,
                    description=f"自动提取的角色: {name}",
                    appearance=asset.base_traits,
                    aliases=asset.aliases,
                    visual_states=visual_states_data,
                    last_updated_chapter=asset.last_updated_chapter,
                    metadata={"asset_data": asset.to_dict()},
                )
            else:
                # 更新现有角色
                char.appearance = asset.base_traits
                char.aliases = asset.aliases
                char.visual_states = visual_states_data
                char.last_updated_chapter = asset.last_updated_chapter
                char.metadata = {**char.metadata, "asset_data": asset.to_dict()}
                await char.save()

    async def process_chapter(
        self, chapter: ChapterModel, novel_id: UUID
    ) -> ChapterExtractionResult:
        """
        处理单个章节，提取角色并更新资产库。

        参数：
            chapter: 章节模型
            novel_id: 小说 ID

        返回：
            ChapterExtractionResult 包含提取结果
        """
        # 1. 加载现有资产
        existing_assets = await self.load_assets_from_db(novel_id)

        # 2. 提取角色
        result = await self.extraction_service.extract_from_chapter(
            chapter_content=chapter.content,
            chapter_number=chapter.number,
            existing_assets=existing_assets,
        )

        # 3. 合并并保存资产
        # 从提取结果重建更新后的资产
        updated_assets = await self._merge_extraction_result(
            existing_assets, result, chapter.number
        )
        await self.save_assets_to_db(novel_id, updated_assets)

        # 4. 更新章节状态
        chapter.metadata = {
            **chapter.metadata,
            "extraction_result": result.to_dict(),
            "processed": True,
        }
        await chapter.save()

        return result

    async def _merge_extraction_result(
        self,
        existing_assets: dict[str, CharacterAsset],
        result: ChapterExtractionResult,
        chapter_number: int,
    ) -> dict[str, CharacterAsset]:
        """合并提取结果到现有资产。"""
        # 使用提取服务的归一化逻辑重新处理
        # 这里简化处理：直接从 prompts 反推需要更新的资产
        updated = dict(existing_assets)

        for name, _prompt in result.character_prompts.items():
            if name not in updated:
                # 新角色
                updated[name] = CharacterAsset(
                    canonical_name=name,
                    character_type="Person",
                    last_updated_chapter=chapter_number,
                )

        return updated

    def generate_prompt_for_character(
        self,
        asset: CharacterAsset,
        chapter_state: str | None = None,
    ) -> str:
        """为角色生成图像生成 prompt。"""
        return asset.generate_prompt(chapter_state)


class ChapterProcessingService:
    """章节处理服务。

    协调整个章节处理流程。
    """

    def __init__(self, llm_client: LLMClient):
        extraction_service = CharacterExtractionService(llm_client)
        self.asset_manager = CharacterAssetManager(extraction_service)

    async def process_single_chapter(self, chapter_id: UUID) -> ChapterExtractionResult | None:
        """处理单个章节。"""
        chapter = await ChapterModel.get_or_none(id=chapter_id).prefetch_related("novel")
        if chapter is None:
            return None

        return await self.asset_manager.process_chapter(chapter, chapter.novel_id)

    async def process_chapters_batch(
        self,
        novel_id: UUID,
        start_chapter: int = 1,
        end_chapter: int | None = None,
    ) -> list[ChapterExtractionResult]:
        """批量处理章节（按顺序）。"""
        query = ChapterModel.filter(novel_id=novel_id, number__gte=start_chapter)
        if end_chapter is not None:
            query = query.filter(number__lte=end_chapter)

        chapters = await query.order_by("number")
        results = []

        for chapter in chapters:
            result = await self.asset_manager.process_chapter(chapter, novel_id)
            results.append(result)

        return results

    async def get_character_prompts(
        self, novel_id: UUID, chapter_number: int | None = None
    ) -> dict[str, str]:
        """
        获取角色的图像生成 prompts。

        如果指定章节号，返回该章节的状态；否则返回最新状态。
        """
        assets = await self.asset_manager.load_assets_from_db(novel_id)
        prompts = {}

        for name, asset in assets.items():
            if chapter_number is not None:
                # 查找指定章节的状态
                state = next(
                    (s for s in asset.visual_states if s.chapter_number == chapter_number),
                    None,
                )
                chapter_state = state.current_state if state else None
            else:
                # 使用最新状态
                latest = asset.get_latest_visual_state()
                chapter_state = latest.current_state if latest else None

            prompts[name] = asset.generate_prompt(chapter_state)

        return prompts
