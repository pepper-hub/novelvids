# NovelVids - AI 小说视频生成器

将小说自动转换为引人入胜的视频内容的 AI 驱动平台。

## 功能特性

- 📚 **小说处理**: 上传并处理小说文本，自动提取章节和角色
- 🎨 **AI 图像生成**: 使用 ComfyUI 为场景生成一致的角色图像
- 🎙️ **语音合成**: 使用多种 TTS 提供商为角色生成独特的语音
- 🎬 **视频创作**: 自动将场景、图像和音频组合成视频
- 🔄 **工作流管理**: 可自定义的 ComfyUI 工作流用于图像生成
- 💰 **使用追踪**: 监控 API 使用情况和成本

## 技术栈

### 后端
- **FastAPI**: 现代、快速的 Web 框架
- **Tortoise ORM**: 异步 ORM
- **PostgreSQL**: 主数据库
- **Celery**: 分布式任务队列
- **Redis**: 缓存和消息代理

### 前端
- **Vue 3**: 渐进式 JavaScript 框架
- **TypeScript**: 类型安全
- **Pinia**: 状态管理
- **Vue Router**: 路由
- **Tailwind CSS**: 实用优先的 CSS 框架
- **Vue I18n**: 国际化支持（中英文）

### AI 集成
- **ComfyUI**: 图像生成工作流
- **Edge TTS / Azure / OpenAI**: 语音合成
- **Fish Speech**: 自定义语音克隆

## 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- ComfyUI（用于图像生成）

### 安装

1. 克隆仓库
```bash
git clone https://github.com/yourusername/novelvids.git
cd novelvids
```

2. 设置后端
```bash
# 使用 uv 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .

# 复制环境变量示例文件
cp .env.example .env
# 编辑 .env 并填写你的配置
```

3. 设置前端
```bash
cd frontend
npm install
```

4. 初始化数据库
```bash
# 运行迁移
aerich upgrade
```

5. 启动服务

```bash
# 启动后端（开发模式）
uvicorn novelvids.main:app --reload

# 在新终端中启动前端
cd frontend
npm run dev

# 在另一个终端中启动 Celery worker
celery -A novelvids.infrastructure.celery.app worker --loglevel=info
```

### 使用 Docker

```bash
# 使用 docker-compose 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 项目结构

```
novelvids/
├── src/novelvids/          # 后端源代码
│   ├── api/                # API 端点
│   ├── application/        # 应用服务和 DTO
│   ├── core/               # 核心配置和安全
│   ├── domain/             # 领域模型和接口
│   └── infrastructure/     # 基础设施实现
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── api/           # API 客户端
│   │   ├── components/    # Vue 组件
│   │   ├── i18n/          # 国际化配置
│   │   ├── stores/        # Pinia 状态管理
│   │   ├── views/         # 页面组件
│   │   └── router/        # 路由配置
│   └── public/            # 静态资源
├── migrations/            # 数据库迁移
├── tests/                 # 测试
└── scripts/               # 实用脚本
```

## 配置

主要配置选项在 `.env` 文件中：

```env
# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/novelvids

# Redis
REDIS_URL=redis://localhost:6379/0

# ComfyUI
COMFYUI_API_URL=http://localhost:8188

# JWT 密钥
SECRET_KEY=your-secret-key-here

# TTS 提供商
EDGE_TTS_ENABLED=true
AZURE_TTS_KEY=your-azure-key
OPENAI_API_KEY=your-openai-key
```

## 开发

### 运行测试

```bash
# 后端测试
pytest

# 前端测试
cd frontend
npm run test
```

### 代码格式化

```bash
# 后端
ruff format .

# 前端
cd frontend
npm run format
```

### 类型检查

```bash
# 后端
mypy src/

# 前端
cd frontend
npm run type-check
```

## API 文档

启动后端服务后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 国际化

前端支持中英文双语：
- 在页面右上角点击语言切换器
- 用户选择的语言会自动保存到 localStorage
- 所有主要页面和组件都已翻译

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 许可证

MIT License - 详见 LICENSE 文件

## 致谢

- ComfyUI 用于强大的图像生成工作流
- FastAPI 用于出色的 Web 框架
- Vue.js 团队用于优秀的前端框架
