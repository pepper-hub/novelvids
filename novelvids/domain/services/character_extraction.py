"""角色提取服务。

使用 LLM 从小说章节中提取角色信息，并通过图算法进行实体归一化。
"""

import json
from abc import ABC, abstractmethod
from collections import defaultdict

import networkx as nx

from novelvids.domain.models.character_asset import (
    AliasRelation,
    ChapterExtractionResult,
    CharacterAsset,
    ExtractedEntity,
    VisualState,
)

# ==================== 提取 Prompt ====================

EXTRACTION_PROMPT = """你是一个小说设定整理专家。请分析给定的小说片段，提取人物、物品及其视觉描述。
最重要的是，你需要根据上下文逻辑，判断人物的【别名/化名/马甲】关系。

请返回严格的 JSON 格式，结构如下：
{
    "entities": [
        {
            "name": "实体名称(原名)",
            "type": "Person/Object",
            "visual_desc": "视觉外观描述(形容词、衣着、面貌)",
            "action_context": "当前的动作或状态"
        }
    ],
    "relationships": [
        {
            "source": "名字A",
            "target": "名字B",
            "relation": "is_alias_of",
            "reason": "判断他们是同一人的原文依据"
        }
    ]
}

注意：
1. 如果文中明确提到"张三化名为李四"，必须生成一条 relation: {"source": "李四", "target": "张三", "relation": "is_alias_of"}。
2. 视觉描述尽可能摘录原文中的形容词。
"""

STATE_EXTRACTION_PROMPT = """你是一个小说视觉化助手。
已知角色数据库摘要：{known_characters}

请分析当前章节文本，提取主要角色的视觉信息。返回 JSON 格式：
{{
    "characters": [
        {{
            "name": "标准名(如张凡)",
            "alias_used": "文中称呼(如崇祯)",
            "is_new_or_changed": true/false (是否有新的永久性生理特征，或者这是新角色),
            "permanent_traits": "如果是新角色或发生了生理巨变(毁容/长大)，请用英文描写其固有长相。否则留空",
            "current_state": "当前的衣着、动作、物品、表情 (English)"
        }}
    ]
}}
注意：permanent_traits 是指如果不化妆不换衣服也存在的特征（脸型、身材、疤痕）。
"""


class LLMClient(ABC):
    """LLM 客户端抽象基类。"""

    @abstractmethod
    async def extract_entities(self, text: str) -> dict:
        """从文本中提取实体和关系。"""
        pass

    @abstractmethod
    async def extract_character_states(self, text: str, known_characters: list[str]) -> dict:
        """提取角色状态信息。"""
        pass


class OpenAICompatibleClient(LLMClient):
    """兼容 OpenAI API 的 LLM 客户端。"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        model_name: str = "gpt-4o-mini",
    ):
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name

    async def extract_entities(self, text: str) -> dict:
        """从文本中提取实体和关系。"""
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": EXTRACTION_PROMPT},
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)

    async def extract_character_states(self, text: str, known_characters: list[str]) -> dict:
        """提取角色状态信息。"""
        system_prompt = STATE_EXTRACTION_PROMPT.format(known_characters=str(known_characters))
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)


class CharacterExtractionService:
    """角色提取服务。

    实现增量式状态机模式：
    1. 从章节文本中提取实体和关系
    2. 使用图算法进行实体归一化（连通分量）
    3. 更新角色资产库
    """

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def extract_from_chapter(
        self,
        chapter_content: str,
        chapter_number: int,
        existing_assets: dict[str, CharacterAsset],
    ) -> ChapterExtractionResult:
        """
        从章节中提取角色信息并更新资产库。

        参数：
            chapter_content: 章节文本
            chapter_number: 章节编号
            existing_assets: 现有角色资产 {canonical_name: CharacterAsset}

        返回：
            ChapterExtractionResult 包含提取结果和最终 prompts
        """
        # 1. 调用 LLM 提取实体和关系
        raw_data = await self.llm_client.extract_entities(chapter_content)

        entities = [
            ExtractedEntity(
                name=e["name"],
                entity_type=e.get("type", "Person"),
                visual_desc=e.get("visual_desc", ""),
                action_context=e.get("action_context", ""),
            )
            for e in raw_data.get("entities", [])
        ]

        alias_relations = [
            AliasRelation(
                alias=r["source"],
                canonical_name=r["target"],
                reason=r.get("reason", ""),
                chapter_discovered=chapter_number,
            )
            for r in raw_data.get("relationships", [])
            if r.get("relation") == "is_alias_of"
        ]

        # 2. 调用 LLM 提取状态信息
        known_names = list(existing_assets.keys())
        state_data = await self.llm_client.extract_character_states(chapter_content, known_names)

        # 3. 使用图算法归一化实体
        resolved_assets = self._resolve_entities(
            entities, alias_relations, existing_assets, chapter_number, state_data
        )

        # 4. 生成最终 prompts
        character_prompts = {}
        for name, asset in resolved_assets.items():
            latest_state = asset.get_latest_visual_state()
            current_state = latest_state.current_state if latest_state else None
            character_prompts[name] = asset.generate_prompt(current_state)

        return ChapterExtractionResult(
            chapter_number=chapter_number,
            entities=entities,
            alias_relations=alias_relations,
            character_prompts=character_prompts,
        )

    def _resolve_entities(
        self,
        entities: list[ExtractedEntity],
        alias_relations: list[AliasRelation],
        existing_assets: dict[str, CharacterAsset],
        chapter_number: int,
        state_data: dict,
    ) -> dict[str, CharacterAsset]:
        """
        使用图算法进行实体归一化。

        核心算法：连通分量 (Connected Components)
        如果 A-B 相连，B-C 相连，那么 {A, B, C} 就是同一个人的不同马甲
        """
        G = nx.Graph()
        name_to_descs: dict[str, list[str]] = defaultdict(list)

        # 1. 添加节点
        for entity in entities:
            name = entity.name
            if entity.visual_desc:
                name_to_descs[name].append(entity.visual_desc)
            if not G.has_node(name):
                G.add_node(name, type=entity.entity_type)

        # 添加现有资产中的名字
        for name, asset in existing_assets.items():
            if not G.has_node(name):
                G.add_node(name, type=asset.character_type)
            for alias in asset.aliases:
                if not G.has_node(alias):
                    G.add_node(alias, type=asset.character_type)
                G.add_edge(name, alias)

        # 2. 添加边（别名关系）
        for rel in alias_relations:
            G.add_edge(rel.alias, rel.canonical_name)

        # 3. 处理状态数据中的角色
        state_chars = state_data.get("characters", [])
        state_by_name: dict[str, dict] = {}
        for char_data in state_chars:
            name = char_data.get("name", "")
            alias = char_data.get("alias_used", "")
            if name:
                state_by_name[name] = char_data
                if not G.has_node(name):
                    G.add_node(name, type="Person")
                if alias and alias != name:
                    if not G.has_node(alias):
                        G.add_node(alias, type="Person")
                    G.add_edge(name, alias)

        # 4. 连通分量归一化
        resolved_assets: dict[str, CharacterAsset] = {}

        for component in nx.connected_components(G):
            names_in_group = list(component)

            # 选择主 ID：优先使用现有资产中的名字，否则选最短的
            primary_id = None
            for name in names_in_group:
                if name in existing_assets:
                    primary_id = name
                    break
            if primary_id is None:
                primary_id = min(names_in_group, key=len)

            # 获取或创建资产
            if primary_id in existing_assets:
                asset = existing_assets[primary_id]
            else:
                node_type = G.nodes.get(primary_id, {}).get("type", "Person")
                asset = CharacterAsset(canonical_name=primary_id, character_type=node_type)

            # 添加所有别名
            for name in names_in_group:
                asset.add_alias(name)

            # 更新永久属性和视觉状态
            for name in names_in_group:
                if name in state_by_name:
                    char_state = state_by_name[name]

                    # 更新永久属性
                    if char_state.get("is_new_or_changed"):
                        new_traits = char_state.get("permanent_traits", "")
                        if new_traits:
                            asset.update_base_traits(new_traits, chapter_number)

                    # 添加视觉状态
                    current_state = char_state.get("current_state", "")
                    if current_state:
                        visual_state = VisualState(
                            chapter_number=chapter_number,
                            alias_used=char_state.get("alias_used", name),
                            current_state=current_state,
                        )
                        asset.add_visual_state(visual_state)

            resolved_assets[primary_id] = asset

        return resolved_assets
