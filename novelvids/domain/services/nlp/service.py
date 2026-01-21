"""章节识别领域服务。

使用策略模式实现章节识别功能。
"""

from novelvids.domain.models.nlp import NovelText, ParsedChapterResult
from novelvids.domain.services.nlp.strategies import ChapterRecognitionStrategy


class ChapterRecognitionService:
    """章节识别服务，负责协调章节识别流程。"""

    def __init__(self, strategy: ChapterRecognitionStrategy):
        """
        使用指定策略初始化服务。

        参数：
            strategy: 要使用的章节识别策略
        """
        self._strategy = strategy

    def process_novel(self, content: str) -> list[ParsedChapterResult]:
        """
        处理小说内容以提取章节。

        参数：
            content: 小说的原始文本内容

        返回：
            解析出的章节结果列表

        异常：
            ValueError: 当内容为空时抛出
        """
        novel_text = NovelText.from_string(content)
        return self._strategy.recognize(novel_text)
