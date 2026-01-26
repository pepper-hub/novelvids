"""使用 Tortoise ORM 的数据库模型。"""

from enum import StrEnum

from tortoise import fields
from tortoise.models import Model


class TaskStatus(StrEnum):
    """任务执行状态。"""

    PENDING = "pending"  # 待处理
    QUEUED = "queued"  # 已入队
    RUNNING = "running"  # 运行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 已取消


class WorkflowStatus(StrEnum):
    """小说工作流状态 - 状态机。

    工作流顺序：
    draft -> chapters_extracted -> characters_extracted -> storyboard_ready -> generating -> completed

    状态转换规则：
    - draft: 初始状态，小说刚上传
    - chapters_extracted: 章节已提取（需要 total_chapters > 0）
    - characters_extracted: 角色已提取（需要有 characters）
    - storyboard_ready: 分镜已就绪（需要有 scenes）
    - generating: 正在生成视频
    - completed: 全部完成
    """

    DRAFT = "draft"  # 草稿 - 刚上传
    CHAPTERS_EXTRACTED = "chapters_extracted"  # 已分章
    CHARACTERS_EXTRACTED = "characters_extracted"  # 已提取角色
    STORYBOARD_READY = "storyboard_ready"  # 分镜就绪
    GENERATING = "generating"  # 生成中
    COMPLETED = "completed"  # 已完成

    @classmethod
    def get_order(cls) -> list["WorkflowStatus"]:
        """获取工作流顺序。"""
        return [
            cls.DRAFT,
            cls.CHAPTERS_EXTRACTED,
            cls.CHARACTERS_EXTRACTED,
            cls.STORYBOARD_READY,
            cls.GENERATING,
            cls.COMPLETED,
        ]

    def can_transition_to(self, target: "WorkflowStatus") -> bool:
        """检查是否可以转换到目标状态。"""
        order = self.get_order()
        current_idx = order.index(self)
        target_idx = order.index(target)
        # 只能向前进一步，或者保持原状态
        return target_idx == current_idx or target_idx == current_idx + 1

    def get_next(self) -> "WorkflowStatus | None":
        """获取下一个状态。"""
        order = self.get_order()
        current_idx = order.index(self)
        if current_idx < len(order) - 1:
            return order[current_idx + 1]
        return None


class ChapterWorkflowStatus(StrEnum):
    """章节工作流状态 - 每章独立的处理状态。

    工作流顺序：
    pending -> characters_extracted -> storyboard_ready -> generating -> completed

    每章独立处理，完成后才能进行下一步。
    """

    PENDING = "pending"  # 待处理
    CHARACTERS_EXTRACTED = "characters_extracted"  # 已提取角色
    STORYBOARD_READY = "storyboard_ready"  # 分镜就绪
    GENERATING = "generating"  # 生成中
    COMPLETED = "completed"  # 已完成

    @classmethod
    def get_order(cls) -> list["ChapterWorkflowStatus"]:
        """获取工作流顺序。"""
        return [
            cls.PENDING,
            cls.CHARACTERS_EXTRACTED,
            cls.STORYBOARD_READY,
            cls.GENERATING,
            cls.COMPLETED,
        ]

    def can_transition_to(self, target: "ChapterWorkflowStatus") -> bool:
        """检查是否可以转换到目标状态。"""
        order = self.get_order()
        current_idx = order.index(self)
        target_idx = order.index(target)
        return target_idx == current_idx or target_idx == current_idx + 1

    def get_next(self) -> "ChapterWorkflowStatus | None":
        """获取下一个状态。"""
        order = self.get_order()
        current_idx = order.index(self)
        if current_idx < len(order) - 1:
            return order[current_idx + 1]
        return None


class Gender(StrEnum):
    """角色性别。"""

    MALE = "male"  # 男
    FEMALE = "female"  # 女
    OTHER = "other"  # 其他


class VoiceProvider(StrEnum):
    """语音合成服务提供商。"""

    EDGE_TTS = "edge_tts"
    AZURE = "azure"
    OPENAI = "openai"
    FISH_SPEECH = "fish_speech"
    CUSTOM = "custom"


class BaseModel(Model):
    """包含通用字段的基础模型。"""

    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True


class UserModel(BaseModel):
    """用户数据库模型。"""

    username = fields.CharField(max_length=50, unique=True, index=True)
    email = fields.CharField(max_length=255, unique=True, index=True)
    hashed_password = fields.CharField(max_length=255)
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)
    balance = fields.DecimalField(max_digits=12, decimal_places=4, default=0)
    metadata = fields.JSONField(default=dict)

    novels: fields.ReverseRelation["NovelModel"]
    usage_records: fields.ReverseRelation["UsageRecordModel"]

    class Meta:
        table = "users"


class NovelModel(BaseModel):
    """小说数据库模型。"""

    title = fields.CharField(max_length=255, index=True)
    content = fields.TextField()
    author = fields.CharField(max_length=255, null=True)
    user: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(
        "models.UserModel",
        related_name="novels",
        on_delete=fields.CASCADE,
    )
    status = fields.CharEnumField(TaskStatus, default=TaskStatus.PENDING, index=True)
    workflow_status = fields.CharEnumField(WorkflowStatus, default=WorkflowStatus.DRAFT, index=True)
    total_chapters = fields.IntField(default=0)
    processed_chapters = fields.IntField(default=0)
    metadata = fields.JSONField(default=dict)

    chapters: fields.ReverseRelation["ChapterModel"]
    characters: fields.ReverseRelation["CharacterModel"]
    videos: fields.ReverseRelation["VideoModel"]

    class Meta:
        table = "novels"

    def can_extract_chapters(self) -> bool:
        """检查是否可以提取章节。"""
        return self.workflow_status == WorkflowStatus.DRAFT and bool(self.content)

    def can_extract_characters(self) -> bool:
        """检查是否可以提取角色。"""
        return self.workflow_status == WorkflowStatus.CHAPTERS_EXTRACTED and self.total_chapters > 0

    def can_create_storyboard(self) -> bool:
        """检查是否可以创建分镜。"""
        return self.workflow_status == WorkflowStatus.CHARACTERS_EXTRACTED

    def can_generate_video(self) -> bool:
        """检查是否可以生成视频。"""
        return self.workflow_status == WorkflowStatus.STORYBOARD_READY

    async def advance_workflow(self, target_status: WorkflowStatus) -> bool:
        """尝试推进工作流状态。

        Args:
            target_status: 目标状态

        Returns:
            是否成功推进
        """
        if self.workflow_status.can_transition_to(target_status):
            self.workflow_status = target_status
            await self.save(update_fields=["workflow_status", "updated_at"])
            return True
        return False


class ChapterModel(BaseModel):
    """章节数据库模型。"""

    novel: fields.ForeignKeyRelation[NovelModel] = fields.ForeignKeyField(
        "models.NovelModel",
        related_name="chapters",
        on_delete=fields.CASCADE,
    )
    number = fields.IntField(index=True)
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    status = fields.CharEnumField(TaskStatus, default=TaskStatus.PENDING, index=True)
    workflow_status = fields.CharEnumField(
        ChapterWorkflowStatus, default=ChapterWorkflowStatus.PENDING, index=True
    )
    scene_count = fields.IntField(default=0)
    metadata = fields.JSONField(default=dict)

    scenes: fields.ReverseRelation["SceneModel"]

    class Meta:
        table = "chapters"
        unique_together = (("novel", "number"),)

    def can_extract_characters(self) -> bool:
        """检查是否可以提取角色。"""
        return self.workflow_status == ChapterWorkflowStatus.PENDING

    def can_create_storyboard(self) -> bool:
        """检查是否可以创建分镜。"""
        return self.workflow_status == ChapterWorkflowStatus.CHARACTERS_EXTRACTED

    def can_generate_video(self) -> bool:
        """检查是否可以生成视频。"""
        return self.workflow_status == ChapterWorkflowStatus.STORYBOARD_READY


class CharacterModel(BaseModel):
    """角色数据库模型，用于维护角色一致性。"""

    name = fields.CharField(max_length=100, index=True)
    novel: fields.ForeignKeyRelation[NovelModel] = fields.ForeignKeyField(
        "models.NovelModel",
        related_name="characters",
        on_delete=fields.CASCADE,
    )
    description = fields.TextField(null=True)
    gender = fields.CharEnumField(Gender, default=Gender.OTHER)
    age_range = fields.CharField(max_length=50, null=True)
    appearance = fields.TextField(null=True)  # 用于存储 base_traits
    personality = fields.TextField(null=True)
    voice_id = fields.CharField(max_length=255, null=True)
    voice_provider = fields.CharEnumField(VoiceProvider, default=VoiceProvider.EDGE_TTS)
    reference_images = fields.JSONField(default=list)
    embedding = fields.JSONField(null=True)
    # 新增：别名列表，用于快速查询
    aliases = fields.JSONField(default=list)
    # 新增：视觉状态历史，存储各章节的视觉状态
    visual_states = fields.JSONField(default=list)
    # 新增：最后更新的章节编号
    last_updated_chapter = fields.IntField(default=0)
    metadata = fields.JSONField(default=dict)

    scenes: fields.ReverseRelation["SceneModel"]

    class Meta:
        table = "characters"
        unique_together = (("novel", "name"),)


class SceneModel(BaseModel):
    """场景数据库模型，表示单个分镜/镜头。"""

    chapter: fields.ForeignKeyRelation[ChapterModel] = fields.ForeignKeyField(
        "models.ChapterModel",
        related_name="scenes",
        on_delete=fields.CASCADE,
    )
    sequence = fields.IntField(index=True)
    description = fields.TextField()
    dialogue = fields.TextField(null=True)
    speaker: fields.ForeignKeyRelation[CharacterModel] | None = fields.ForeignKeyField(
        "models.CharacterModel",
        related_name="scenes",
        on_delete=fields.SET_NULL,
        null=True,
    )
    prompt = fields.TextField(null=True)
    negative_prompt = fields.TextField(null=True)
    image_url = fields.CharField(max_length=500, null=True)
    audio_url = fields.CharField(max_length=500, null=True)
    duration = fields.FloatField(default=0.0)
    status = fields.CharEnumField(TaskStatus, default=TaskStatus.PENDING, index=True)
    metadata = fields.JSONField(default=dict)

    class Meta:
        table = "scenes"
        unique_together = (("chapter", "sequence"),)


class VideoModel(BaseModel):
    """视频数据库模型。"""

    novel: fields.ForeignKeyRelation[NovelModel] = fields.ForeignKeyField(
        "models.NovelModel",
        related_name="videos",
        on_delete=fields.CASCADE,
    )
    chapter: fields.ForeignKeyRelation[ChapterModel] | None = fields.ForeignKeyField(
        "models.ChapterModel",
        related_name="videos",
        on_delete=fields.SET_NULL,
        null=True,
    )
    title = fields.CharField(max_length=255)
    url = fields.CharField(max_length=500, null=True)
    duration = fields.FloatField(default=0.0)
    resolution = fields.CharField(max_length=20, default="1920x1080")
    fps = fields.IntField(default=24)
    status = fields.CharEnumField(TaskStatus, default=TaskStatus.PENDING, index=True)
    metadata = fields.JSONField(default=dict)

    class Meta:
        table = "videos"


class UsageRecordModel(BaseModel):
    """使用记录模型，用于计费。"""

    user: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(
        "models.UserModel",
        related_name="usage_records",
        on_delete=fields.CASCADE,
    )
    resource_type = fields.CharField(max_length=50, index=True)
    quantity = fields.FloatField()
    unit_cost = fields.DecimalField(max_digits=10, decimal_places=6)
    total_cost = fields.DecimalField(max_digits=12, decimal_places=4)
    description = fields.CharField(max_length=255, null=True)
    metadata = fields.JSONField(default=dict)

    class Meta:
        table = "usage_records"


class ComfyUIWorkflowModel(BaseModel):
    """ComfyUI 工作流配置模型。"""

    name = fields.CharField(max_length=100, unique=True, index=True)
    description = fields.TextField(null=True)
    workflow_json = fields.JSONField()
    category = fields.CharField(max_length=50, default="general", index=True)
    is_default = fields.BooleanField(default=False)
    metadata = fields.JSONField(default=dict)

    class Meta:
        table = "comfyui_workflows"
