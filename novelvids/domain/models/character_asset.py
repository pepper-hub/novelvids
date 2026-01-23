"""角色资产领域模型。

支持增量式角色提取、别名管理和视觉状态跟踪。
"""

from dataclasses import dataclass, field
from typing import Self


@dataclass
class VisualState:
    """角色在特定章节的视觉状态。"""

    chapter_number: int
    alias_used: str  # 文中使用的称呼
    current_state: str  # 当前衣着、动作、物品、表情 (英文 prompt)

    def to_dict(self) -> dict:
        return {
            "chapter_number": self.chapter_number,
            "alias_used": self.alias_used,
            "current_state": self.current_state,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            chapter_number=data["chapter_number"],
            alias_used=data["alias_used"],
            current_state=data["current_state"],
        )


@dataclass
class AliasRelation:
    """别名关系，表示两个名字指向同一角色。"""

    alias: str  # 别名/化名/马甲
    canonical_name: str  # 标准名/原名
    reason: str  # 判断依据
    chapter_discovered: int  # 发现该关系的章节

    def to_dict(self) -> dict:
        return {
            "alias": self.alias,
            "canonical_name": self.canonical_name,
            "reason": self.reason,
            "chapter_discovered": self.chapter_discovered,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            alias=data["alias"],
            canonical_name=data["canonical_name"],
            reason=data["reason"],
            chapter_discovered=data["chapter_discovered"],
        )


@dataclass
class CharacterAsset:
    """角色资产，包含固有属性和视觉状态历史。"""

    canonical_name: str  # 标准名称
    character_type: str = "Person"  # Person/Object
    base_traits: str = ""  # 固有属性：脸型、身材、疤痕等永久特征 (英文)
    aliases: list[str] = field(default_factory=list)  # 所有已知别名
    visual_states: list[VisualState] = field(default_factory=list)  # 各章节视觉状态
    last_updated_chapter: int = 0

    def add_alias(self, alias: str) -> None:
        """添加别名。"""
        if alias and alias not in self.aliases and alias != self.canonical_name:
            self.aliases.append(alias)

    def update_base_traits(self, new_traits: str, chapter: int) -> bool:
        """更新固有属性，仅当发生永久变化时。返回是否发生更新。"""
        if new_traits and new_traits != self.base_traits:
            self.base_traits = new_traits
            self.last_updated_chapter = chapter
            return True
        return False

    def add_visual_state(self, state: VisualState) -> None:
        """添加章节视觉状态。"""
        # 移除同一章节的旧状态
        self.visual_states = [
            s for s in self.visual_states if s.chapter_number != state.chapter_number
        ]
        self.visual_states.append(state)
        self.visual_states.sort(key=lambda s: s.chapter_number)

    def get_latest_visual_state(self) -> VisualState | None:
        """获取最新的视觉状态。"""
        return self.visual_states[-1] if self.visual_states else None

    def generate_prompt(self, chapter_state: str | None = None) -> str:
        """
        生成最终的图像生成 prompt。

        合成：Base Traits + Chapter State
        """
        parts = []

        if self.base_traits:
            parts.append(f"(Base: {self.base_traits})")
        else:
            parts.append("(Base: Unknown Appearance)")

        if chapter_state:
            parts.append(chapter_state)

        return ", ".join(parts)

    def to_dict(self) -> dict:
        return {
            "canonical_name": self.canonical_name,
            "character_type": self.character_type,
            "base_traits": self.base_traits,
            "aliases": self.aliases,
            "visual_states": [s.to_dict() for s in self.visual_states],
            "last_updated_chapter": self.last_updated_chapter,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            canonical_name=data["canonical_name"],
            character_type=data.get("character_type", "Person"),
            base_traits=data.get("base_traits", ""),
            aliases=data.get("aliases", []),
            visual_states=[VisualState.from_dict(s) for s in data.get("visual_states", [])],
            last_updated_chapter=data.get("last_updated_chapter", 0),
        )


@dataclass
class ExtractedEntity:
    """从文本中提取的实体。"""

    name: str
    entity_type: str  # Person/Object
    visual_desc: str  # 视觉外观描述
    action_context: str  # 当前动作或状态

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.entity_type,
            "visual_desc": self.visual_desc,
            "action_context": self.action_context,
        }


@dataclass
class ChapterExtractionResult:
    """单章提取结果。"""

    chapter_number: int
    entities: list[ExtractedEntity]
    alias_relations: list[AliasRelation]
    character_prompts: dict[str, str]  # 角色名 -> 最终 prompt

    def to_dict(self) -> dict:
        return {
            "chapter_number": self.chapter_number,
            "entities": [e.to_dict() for e in self.entities],
            "alias_relations": [r.to_dict() for r in self.alias_relations],
            "character_prompts": self.character_prompts,
        }
