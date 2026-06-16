---
title: AutoResearch AI
emoji: 🔬
colorFrom: yellow
colorTo: red
sdk: docker
app_port: 7860
pinned: false
---

# AutoResearch AI 🔬
### Autonomous Research & BRD Generation Agent

> Built with Google Gemini and Vertex AI

## 🚀 Live Demo
- **Frontend:** https://autoresearch-emi1zjhkd-shresthbhargavas-projects.vercel.app
- **Backend API:** https://shresth0-autoresearch-ai.hf.space
- **API Docs:** https://shresth0-autoresearch-ai.hf.space/docs

## 🧠 What It Does
Transforms fragmented startup inputs — notes, PDFs, screenshots — 
into a professional Business Requirements Document in under 60 seconds.

## ⚡ 4 AI Agents Working in Parallel
- **Research Agent** — Extracts insights from your inputs
- **Market Agent** — Competitor analysis & market sizing  
- **BRD Agent** — Writes the full professional document
- **Architect Agent** — Generates system design blueprint

## 🛠 Tech Stack
| Layer | Technology |
|-------|-----------|
| AI Model | Google Gemini 1.5 Pro |
| Cloud | Vertex AI · BigQuery · Cloud Storage |
| Orchestration | LangGraph · LangChain |
| Backend | FastAPI · Python |
| Frontend | Next.js 14 · TypeScript · Tailwind |
| Deployment | Hugging Face Spaces · Vercel |

## 🏗 Architecture
```
User Input (PDF/Image/Text)
↓
Cloud Storage
↓
Gemini AI Context Engine
↓
Research Agent ‖ Market Agent (parallel)
↓
BRD Agent
↓
Architect Agent
↓
Professional BRD + BigQuery Audit Log
```
## 🚀 Run Locally

### Backend
```bash
cd app
pip install -r requirements.txt
cp .env.example .env
# Add your GEMINI_API_KEY to .env
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend-next
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

## 📄 License
MIT
Save → then push:
bashgit add README.md
git commit -m "Add professional README"
git push origin main
