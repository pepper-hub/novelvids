"""NLP 处理相关的领域模型。

提供小说文本和章节解析结果的值对象。
"""

from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class NovelText:
    """表示原始小说文本的值对象。"""

    content: str

    @property
    def length(self) -> int:
        """获取内容长度。"""
        return len(self.content)

    def is_empty(self) -> bool:
        """检查内容是否为空。"""
        return not self.content.strip()

    @classmethod
    def from_string(cls, content: str) -> Self:
        """从字符串创建实例。"""
        if not content:
            raise ValueError("小说内容不能为空")
        return cls(content=content)


@dataclass(frozen=True)
class ParsedChapterResult:
    """表示识别出的章节的值对象。"""

    title: str
    content: str
    start_index: int
    end_index: int
    confidence: float = 1.0

    def __post_init__(self):
        """验证索引值。"""
        if self.start_index < 0:
            raise ValueError("起始索引不能为负数")
        if self.end_index <= self.start_index:
            raise ValueError("结束索引必须大于起始索引")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("置信度必须在 0.0 到 1.0 之间")
