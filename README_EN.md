# NovelVids - AI Novel Video Generator

Generate style-consistent videos from novels using third-party video generation APIs.

## Core Features

### 🎯 Problems Solved

| Problem | Solution |
|---------|----------|
| AI context length limits | **Continuation mechanism** for processing long texts |
| High token consumption | **FileID upload** to avoid repeated transmission |
| AI doesn't understand content | Structured extraction of characters, scenes, plots |
| Inconsistent characters/scenes | **Three-view reference images** for style consistency |

### 📦 Main Features

- **Character Extraction**: Auto-identify characters from novels, generate three-view references
- **Storyboard Generation**: Intelligently split chapters into video shots
- **Video Generation**: Call Vidu/Doubao APIs for style-consistent video clips
- **Studio Editor**: Visual editing of shots and parameters

## Quick Start

> ⚠️ **Note**: Project is under development, Docker deployment not available yet

### Requirements

- Python 3.12+
- Node.js 18+

### Installation

```bash
# Clone
git clone https://github.com/Anning01/novelvids.git
cd novelvids

# Backend
uv venv && source .venv/bin/activate
uv pip install -e .
cp .env.example .env  # Configure API keys

# Frontend
cd frontend && npm install

```

### Run

```bash
# Backend
uvicorn novelvids.main:app --reload

# Frontend (new terminal)
cd frontend && npm run dev
```

Visit http://localhost:3000

## Development Progress

### ✅ Completed
- [x] Novel upload & chapter extraction
- [x] Character/scene AI extraction
- [x] Reference image generation (three-view)
- [x] Auto storyboard generation
- [x] Video API integration (Vidu/Doubao)
- [x] Basic studio editing

### 🚧 In Progress
- [ ] Video generation quality optimization
- [ ] Fine-grained shot control
- [ ] Multi-clip auto composition
- [ ] Audio/voiceover integration

## Contributing

Project is in early development. PRs welcome!

Areas needing help:
- Video generation quality
- Fine-grained shot parameter control
- Style consistency optimization

## License

MIT License

---

[中文](./README.md)
