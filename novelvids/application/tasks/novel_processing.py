"""小说处理后台任务模块。"""

from uuid import UUID

from fastapi import concurrency
from loguru import logger

from novelvids.domain.services.nlp import (
    ChapterRecognitionService,
    MLChapterRecognitionStrategy,
)
from novelvids.infrastructure.database.models import TaskStatus
from novelvids.infrastructure.database.repositories import (
    TortoiseChapterRepository,
    TortoiseNovelRepository,
)


async def process_novel_task(novel_id: UUID, user_id: UUID) -> None:
    """
    处理小说的后台任务。

    处理步骤：
    1. 获取小说内容
    2. 使用 NLP 识别章节（CPU 密集型操作，在线程池中运行）
    3. 保存章节到数据库
    4. 更新小说状态
    """
    logger.info(f"开始处理小说 {novel_id}")

    novel_repo = TortoiseNovelRepository()
    chapter_repo = TortoiseChapterRepository()

    novel = await novel_repo.get_by_id(novel_id)
    if not novel:
        logger.error(f"小说 {novel_id} 不存在")
        return

    # 初始化 NLP 服务（使用 ML 策略）
    # 注意：ML 策略加载模型，首次运行可能较慢
    try:
        strategy = MLChapterRecognitionStrategy()
        service = ChapterRecognitionService(strategy)
    except Exception as e:
        logger.error(f"初始化 NLP 服务失败: {e}")
        await novel_repo.update(novel_id, {"status": TaskStatus.FAILED})
        return

    # 更新状态为运行中
    await novel_repo.update(novel_id, {"status": TaskStatus.RUNNING})

    try:
        # 在线程池中运行 CPU 密集型的 NLP 任务
        logger.info(f"正在对小说 {novel_id} 进行 NLP 识别")
        chapters = await concurrency.run_in_threadpool(
            service.process_novel, novel.content
        )
        logger.info(f"小说 {novel_id} 识别出 {len(chapters)} 个章节")

        # 保存章节到数据库
        for i, chapter_data in enumerate(chapters):
            await chapter_repo.create(
                novel_id=novel_id,
                title=chapter_data.title,
                content=chapter_data.content,
                number=i + 1,
                status=TaskStatus.PENDING,  # 章节初始状态（等待场景生成）
                scene_count=0
            )

        # 更新小说状态为已完成
        await novel_repo.update(
            novel_id,
            {
                "status": TaskStatus.COMPLETED,
                "total_chapters": len(chapters),
                "processed_chapters": 0
            }
        )
        logger.info(f"小说 {novel_id} 处理成功")

    except Exception as e:
        logger.exception(f"处理小说 {novel_id} 时出错: {e}")
        await novel_repo.update(novel_id, {"status": TaskStatus.FAILED})
