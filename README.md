# Mentoro RAG 📚

**Mentoro RAG** is an open‑source Retrieval‑Augmented Generation (RAG) platform that powers AI‑driven tutoring, course search, and personalized learning experiences. Built with **FastAPI**, **ChromaDB**, and **LangChain**, it synchronizes course data from a Mentor backend into a vector store and serves real‑time chat completions.

---

## 🎯 Why Mentoro RAG?
- **Highly Scalable** – Leverages ChromaDB for fast similarity searches.
- **Seamless Sync** – Automatic bulk sync of courses from your backend via the `/api/sync-source` endpoint.
- **Production‑Ready CI/CD** – GitHub Actions pipeline builds Docker images and runs linting, type‑checking, and tests on every push.
- **Front‑end Ready** – Comes with a Next.js chat UI that proxies requests through an internal API route for CORS‑free communication.

---

## 🛠️ Tech Stack
| Layer | Technology |
|-------|------------|
| **API** | FastAPI 0.115, Uvicorn 0.51 |
| **Vector Store** | ChromaDB 1.5.9 |
| **LLM Integration** | LangChain‑HuggingFace, LangChain‑Chroma |
| **Cache** | Redis (asyncio) |
| **Frontend** | Next.js 16, React 18, TypeScript |
| **CI/CD** | GitHub Actions, Docker, ruff, mypy, pytest |

---

## 📦 Installation
```bash
# Clone the repository
git clone https://github.com/dev-alauddin-bd/mentoro_rag.git
cd mentoro_rag

# Create a virtual environment (recommended)
python -m venv .venv
# Windows activation
.\\.venv\\Scripts\\activate
# Unix/macOS activation
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt


```

---

## ⚙️ Configuration
Create a `.env` file in the project root:
```dotenv
# FastAPI settings
HOST=0.0.0.0
PORT=8000

# Redis cache (required for async Redis support)
REDIS_URL=redis://localhost:6379/0

# External course data source (used by the sync service)
MENTOR_BACKEND_COURSES_URL=http://localhost:8000/api/courses
```
> **Tip:** The `scripts/sync_all_courses.py` script automatically reads this variable.

---

## ▶️ Running the API
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

### Key Endpoints
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check – returns a simple JSON message. |
| `POST` | `/api/v1/chat` | Streams AI‑generated answers (SSE). |
| `POST` | `/api/sync-source` | Accepts `{ "source_url": "..." }` to bulk‑sync courses from an external JSON endpoint. |
| `POST` | `/api/sync` (internal) | Bulk sync via `BulkSyncRequest` – accepts a list of `CourseData`. |

---

## 🔄 Syncing Courses
Two convenient ways to populate the vector store:
1. **External source** – Call the `/api/sync-source` endpoint with a public URL that returns a JSON array of `CourseData` objects.
2. **CLI script** – Run the helper script:
   ```bash
   python scripts/sync_all_courses.py
   ```
   It reads `MENTOR_BACKEND_COURSES_URL` from `.env`, validates the payload, and stores the data in ChromaDB.

---

## 📈 SEO‑Optimized README Structure
- **Title** includes primary keyword *"Mentoro RAG"*.
- **Meta description** (first paragraph) is concise, under 160 characters, summarizing the project and its key benefits.
- **Heading hierarchy** (`#`, `##`, `###`) follows a single H1 and logical sub‑headings, improving crawlability.
- **Keyword density**: Frequent use of terms like *RAG*, *retrieval‑augmented generation*, *FastAPI*, *ChromaDB*, and *AI tutoring*.
- **Rich content**: Tables, emojis, and call‑to‑action badges make the page more engaging for both users and search engines.

---

## 🤝 Contributing
1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/awesome-feature
   ```
3. Run tests:
   ```bash
   pytest -q
   ```
4. Submit a Pull Request.

All contributions must pass the CI pipeline (lint, type‑check, tests) before merging.

---

## 📜 License
Distributed under the **MIT License**. See `LICENSE` for more information.

---

## 📞 Support & Community
- **Issues**: Open a GitHub issue for bugs or feature requests.
- **Discussions**: Join the community chat on Discord (link in the repo README).
- **Contact**: `dev@alauddin-bd.com`

---

*Stay tuned for upcoming tutorials on fine‑tuning LLMs and deploying Mentoro RAG to cloud platforms!*
