# NovelVids - AI 小说视频生成器

基于第三方视频生成 API，将小说自动转换为风格一致的视频内容。

## 核心特性

### 🎯 解决的问题

| 问题 | 解决方案 |
|------|----------|
| AI 上下文长度限制 | 使用**续写机制**分段处理长文本 |
| Token 消耗过高 | 使用 **FileID** 上传文本，避免重复传输 |
| AI 不理解小说内容 | 结构化提取角色、场景、情节 |
| 人物/场景不一致 | 使用**三视图参考图**保持风格统一 |

### 📦 主要功能

- **角色提取**: 从小说中自动识别角色，生成三视图参考图
- **分镜生成**: 智能拆分章节为视频分镜
- **视频生成**: 调用 Vidu/豆包 API 生成风格一致的视频片段
- **工作室编辑**: 可视化编辑分镜、调整参数

## 快速开始

> ⚠️ **注意**: 项目仍在开发中，Docker 部署暂不可用

### 环境要求

- Python 3.12+
- Node.js 18+

### 安装

```bash
# 克隆项目
git clone https://github.com/Anning01/novelvids.git
cd novelvids

# 后端
uv venv && source .venv/bin/activate
uv pip install -e .
cp .env.example .env  # 配置 API 密钥

# 前端
cd frontend && npm install

# 初始化数据库
aerich upgrade
```

### 启动

```bash
# 后端
uvicorn novelvids.main:app --reload

# 前端 (新终端)
cd frontend && npm run dev
```

访问 http://localhost:3000

## 开发进度

### ✅ 已完成
- [x] 小说上传与章节提取
- [x] 角色/场景 AI 提取
- [x] 参考图生成（三视图）
- [x] 分镜自动生成
- [x] 视频 API 集成 (Vidu/豆包)
- [x] 工作室基础编辑

### 🚧 进行中
- [ ] 视频生成效果优化
- [ ] 分镜超细节控制
- [ ] 多片段自动合成
- [ ] 音频/配音集成

## 参与贡献

项目处于早期开发阶段，欢迎有想法的开发者提交 PR！

重点需要帮助的方向：
- 视频生成质量提升
- 分镜参数精细控制
- 风格一致性优化

## 许可证

MIT License

---

[English](./README_EN.md)
