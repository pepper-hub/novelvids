"""图像、音频和视频生成相关的 API 端点。"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from novelvids.api.dependencies import get_current_user_id
from novelvids.application.dto import GenerateAudioDTO, GenerateImageDTO, ProcessNovelDTO
from novelvids.application.tasks.novel_processing import process_novel_task
from novelvids.infrastructure.comfyui import ComfyUIClient, ComfyUIWorkflowBuilder
from novelvids.infrastructure.database.models import TaskStatus
from novelvids.infrastructure.storage import LocalStorage

router = APIRouter(prefix="/generate", tags=["Generation"])


@router.post("/image")
async def generate_image(
    data: GenerateImageDTO,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    """使用 ComfyUI 生成图像。"""
    client = ComfyUIClient()
    storage = LocalStorage()

    try:
        # 构建工作流
        workflow = ComfyUIWorkflowBuilder.build_txt2img_workflow(
            prompt=data.prompt,
            negative_prompt=data.negative_prompt,
            width=data.width,
            height=data.height,
            seed=data.seed,
        )

        # 生成图像
        images = await client.generate_image(workflow)
        if not images:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="生成图像失败",
            )

        # 保存图像
        image_path = await storage.save_image(images[0])
        image_url = storage.get_url(image_path)

        return {
            "image_url": image_url,
            "width": data.width,
            "height": data.height,
        }
    finally:
        await client.close()


@router.post("/process-novel")
async def process_novel(
    data: ProcessNovelDTO,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    background_tasks: BackgroundTasks,
):
    """开始处理小说以生成视频。"""
    background_tasks.add_task(process_novel_task, data.novel_id, user_id)

    return {
        "task_id": str(data.novel_id),
        "status": TaskStatus.QUEUED.value,
        "message": "小说处理任务已加入队列",
    }


@router.get("/status/{task_id}")
async def get_generation_status(
    task_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    """获取生成任务的状态。"""
    # TODO: 从任务队列中查询实际的任务状态
    return {
        "task_id": str(task_id),
        "status": TaskStatus.PENDING.value,
        "progress": 0,
        "message": "任务等待处理中",
    }
