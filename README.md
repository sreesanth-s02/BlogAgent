# 📝 BlogAgent — AI-Powered Blogger Automation Platform

BlogAgent is a full-stack AI blogging automation platform that helps users generate original blog content, detect plagiarism at sentence level, rewrite risky content, attach images, and publish directly to **Google Blogger** — all from a familiar **document-style editor UI**.

> 🎯 **Core Goal:** Automate high-quality Blogger publishing while bypassing browser-based OAuth limitations through a secure backend-driven workflow.

---

## 🚀 Key Features

### ✍️ AI Content Generation
- Structured blog generation (Introduction, Subsections, Conclusion)
- SEO-friendly, human-like writing
- Strict JSON output contract for reliability

### 🔍 Sentence-Level Plagiarism Detection
- Per-sentence similarity scoring
- Visual highlighting for risky sentences
- Overall blog similarity score
- Safe / Rewrite-Required classification

### ✏️ Intelligent Rewrite System
- Rewrite **only selected sentences**
- User-guided rewrite instructions
- Re-checks similarity after rewrite
- Automatically clears highlights when safe

### 🖼️ Image Pipeline
- AI-generated image keywords
- Image search (Unsplash proxy)
- User-selected image placement (top / bottom)
- Image URL validation before publish

### 📤 Blogger Publishing
- Secure Google OAuth integration
- Token stored **per user**
- Automatic token refresh
- Publish content + image in one click
- Prevents duplicate publishing

### 🔗 Secure Blog Sharing
- Read-only share links using JWT
- Token expiry enforced
- Rewrite & publish disabled in shared view
- “Read-only” visual badge

### 📁 Blog Lifecycle Management
- Pin / Archive / Delete blogs
- Rename drafts (blocked for published blogs)
- Export as Markdown or HTML
- Sidebar with ChatGPT-style UX

---

## 🧱 Tech Stack

### Backend
- FastAPI (Python)
- SQLite (local persistence)
- JWT Authentication
- Rate Limiting (IP-based)
- Groq LLM (LLaMA 3.1)
- Google Blogger API

### Frontend
- Vanilla HTML / CSS / JavaScript
- Document-style editor UX
- Sentence-level interactions
- Dark mode
- Toast notifications & loading states

---

## 🔐 Security & Best Practices

- JWT-protected APIs  
- Rate limiting on all public endpoints  
- Input validation & length limits  
- No secrets committed to Git  
- Environment-based configuration  
- Read-only sharing via scoped JWTs  
- OWASP-aligned backend design  

> 🔒 Secrets are never exposed client-side.

---

## 📂 Project Structure

blog-agent/
│
├── app/
│   ├── api/
│   │   ├── v1/                # Core API routes
│   │   ├── oauth.py            # Blogger OAuth
│   │   ├── login.py            # JWT login
│   │   └── rate_limit.py
│   │
│   ├── blogger/                # Blogger publishing logic
│   ├── core/                   # Auth, JWT, config
│   ├── database/               # SQLite setup
│   ├── llm/                    # Prompts + Groq client
│   ├── plagiarism/             # Sentence-level checker
│   ├── services/               # Image search
│   └── ui/                     # Frontend (HTML/CSS/JS)
│
├── data/                        # Local runtime data (ignored in git)
├── requirements.txt
├── run.py
└── README.md

---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repository
```bash
git clone https://github.com/sreesanth-s02/BlogAgent.git
cd BlogAgent

---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repository
```bash
git clone https://github.com/sreesanth-s02/BlogAgent.git
cd BlogAgent
2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
3️⃣ Install Dependencies
pip install -r requirements.txt
Run locally after setting the environment variables:
python run.py
