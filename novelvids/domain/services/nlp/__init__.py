"""NLP 服务模块。

提供小说章节识别相关的服务和策略。
"""

from novelvids.domain.services.nlp.service import ChapterRecognitionService
from novelvids.domain.services.nlp.strategies import (
    ChapterRecognitionStrategy,
    MLChapterRecognitionStrategy,
    RegexChapterRecognitionStrategy,
)

__all__ = [
    "ChapterRecognitionService",
    "ChapterRecognitionStrategy",
    "RegexChapterRecognitionStrategy",
    "MLChapterRecognitionStrategy",
]
