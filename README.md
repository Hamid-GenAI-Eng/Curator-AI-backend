# 🧠 Curator AI — Note Assistant App (Backend)

Welcome to the backend engine of **Curator AI**, a premium, AI-driven canvas that converts handwritten notes and images into beautifully structured digital notes, summarizes batch documents, and compiles ready-to-export PDF summaries.

This backend is built on **FastAPI** with high-performance asynchronous MongoDB interaction, JWT security, and state-of-the-art LLM pipelines.

---

## 🚀 Key Features

*   **Secure Authentication**: Standard JWT-based signups, logins, and route guard integration.
*   **Groq Multimodal OCR**: Direct image/note uploads processed with Groq's high-speed Vision model (`meta-llama/llama-4-scout-17b-16e-instruct`) for perfect content extraction.
*   **Intelligent Note Refinement**: Automated cleanup, formatting, and structural synthesis of handwritten notes using `llama-3.3-70b-versatile`.
*   **Synthesis & Batch Engine**: Group multiple raw note fragments, refine their flow, and generate cohesive markdown summaries.
*   **Dynamic PDF Generator**: Compiled batch notes exported directly to premium PDF archives using high-fidelity styling.
*   **Production CORS Policy**: Multi-origin CORS guard configured with regex sub-domain recognition to perfectly authorize Vercel deployments.

---

## 🛠️ Technology Stack

*   **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous python web framework)
*   **Database**: [MongoDB Atlas](https://www.mongodb.com/) (Asynchronous interaction using Motor)
*   **AI Orchestration**: [Groq API](https://groq.com/) for high-velocity LLM/Vision inferencing
*   **Security & Tokenization**: JWT (JSON Web Tokens) via `python-jose` and `passlib`
*   **PDF Generation**: `FPDF2`
*   **Hosting Compatibility**: Fully optimized for serverless deployments on [Vercel](https://vercel.com/)

---

## ⚙️ Configuration & Environment Setup

Create a `.env` file in the root directory using the following parameters:

```env
# App Config
APP_NAME="AI Note Assistant"
DEBUG=True
SECRET_KEY="your-production-safe-jwt-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Configuration (MongoDB Atlas)
MONGODB_URL="mongodb+srv://<user>:<password>@cluster.mongodb.net/?appName=curator"
MONGODB_DB_NAME="curator_ai_db"

# AI Model Configuration (Groq & OpenRouter)
GROQ_API_KEY="gsk_..."
LLM_MODEL_NAME="llama-3.3-70b-versatile"
LLM_BASE_URL="https://api.groq.com/openai/v1"

# Vision Configuration (Groq Multimodal OCR)
VISION_MODEL_ID="meta-llama/llama-4-scout-17b-16e-instruct"

# SMTP Relay Config (Brevo)
SMTP_HOST="smtp-relay.brevo.com"
SMTP_PORT=587
SMTP_USER="your-relay-username"
SMTP_PASSWORD="your-relay-password"
EMAILS_FROM_EMAIL="noreply@curator.app"
EMAILS_FROM_NAME="Curator AI"
```

---

## 🏃 Local Development

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/Hamid-GenAI-Eng/Curator-AI-backend.git
    cd Curator-AI-backend
    ```

2.  **Create Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run Development Server**:
    ```bash
    uvicorn app.main:app --reload
    ```
    *   API Welcome Endpoint: `http://localhost:8000/`
    *   Interactive Swagger Documentation: `http://localhost:8000/docs`

---

## 🔌 API Endpoints Summary

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| **POST** | `/auth/signup` | Registers a new user. | No |
| **POST** | `/auth/login` | Log in and return a JWT access token. | No |
| **POST** | `/notes/upload` | Process image upload, run OCR, and refine content. | Yes |
| **POST** | `/notes/batches` | Create a new batch document from note IDs. | Yes |
| **GET** | `/notes/batches` | Retrieve all synthesized batch notes. | Yes |
| **GET** | `/notes/batches/{id}/download` | Compile batch synthesis into a PDF. | Yes |

---

## 🛡️ CORS Production Policy
Our server is configured to dynamically accept CORS preflights and headers for localhost development endpoints and wildcard Vercel subdomains:
*   `http://localhost:5173` & `http://localhost:3000`
*   `https://curator-ai-*.vercel.app`

---

Developed and maintained with ❤️ by [Hamid-GenAI-Eng](https://github.com/Hamid-GenAI-Eng).
