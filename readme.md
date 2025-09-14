<p align="center">
  <img src="https://placehold.co/900x300/2E7D32/FFFFFF?text=AgroAI+%F0%9F%8C%B1&font=raleway" alt="AgroAI Banner" width="900" />
</p>

# 🌱 AgroAI — Smart Farming Assistant

> An intelligent, voice-enabled agricultural assistant built to provide Indian farmers with instant, accurate, and actionable advice.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue.svg" alt="Python" />
  <img src="https://img.shields.io/badge/Framework-Streamlit-red.svg" alt="Streamlit" />
  <img src="https://img.shields.io/badge/AI%2FML-LangChain%20%7C%20Azure%20OpenAI-green.svg" alt="AI Stack" />
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License" />
</p>

---

## Table of Contents

* [About](#about)
* [Key Features](#key-features)
* [Tech Stack](#tech-stack)
* [System Architecture](#system-architecture)
* [Project Structure](#project-structure)
* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Configuration](#configuration)
* [Usage](#usage)
* [Data Format](#data-format)
* [Security & .gitignore](#security--gitignore)
* [Contributing](#contributing)
* [License](#license)
* [Acknowledgements](#acknowledgements)

---

## About

AgroAI is a voice-first chatbot that helps farmers by answering agriculture-related questions using a Retrieval-Augmented Generation (RAG) pipeline. Responses are grounded in a curated knowledge base (`data.json`) and enhanced with short-term conversational memory.

## Key Features

* 🗣️ **Voice-first interaction**: Speak naturally — uses GROQ Whisper for speech-to-text.
* 🔊 **Audio responses**: Answers are returned as text and synthesized audio.
* 🧠 **RAG-powered accuracy**: Answers are generated from a FAISS-backed knowledge base to reduce hallucinations.
* 💬 **Conversational memory**: Keeps recent interactions (configurable) to handle follow-ups.
* 📈 **Analytics dashboard**: Lightweight Streamlit UI showing session stats and usage.
* 🎨 **Responsive UI**: Easy-to-use Streamlit interface for low-literacy and mobile users.

## Tech Stack

* **Frontend:** Streamlit
* **Core Logic:** Python
* **RAG & Orchestration:** LangChain
* **LLM & Embeddings:** Azure OpenAI
* **Speech-to-Text:** GROQ (Whisper-large-v3)
* **Vector DB:** FAISS
* **Audio Processing:** sounddevice, SciPy

## System Architecture (Brief)

1. **User Input (Text/Voice)** → 2. **STT (Whisper)** → 3. **Embeddings** → 4. **FAISS Similarity Search** → 5. **Context Augmentation (recent convo + retrieved docs)** → 6. **Azure OpenAI Generation** → 7. **Text-to-Speech** → 8. **UI Output**

## Project Structure

```
agro-ai-assistant/
│
├── .gitignore
├── app.py                # Main Streamlit application UI
├── farm_bot.py           # Core logic, RAG pipeline, and assistant class
├── vector_db_creation.py # Script to create the FAISS vector database
├── data.json             # Knowledge base with agricultural Q&A
├── faiss_index/          # Directory storing the FAISS vector index
│   └── ...
├── requirements.txt      # Python dependencies
└── README.md             # You are here!
```

---

## Prerequisites

* Python 3.9+
* Git
* A virtual environment manager (venv recommended)
* Azure OpenAI account + deployment (for chat & embeddings)
* GROQ API key (Whisper) for speech-to-text

## Installation

```bash
# Clone the repo
git clone https://github.com/your-username/agro-ai-assistant.git
cd agro-ai-assistant

# Create & activate virtual environment (macOS / Linux)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root (this file is ignored by Git). Add the following keys:

```env
# Azure OpenAI (chat & embeddings)
AZURE_OPENAI_API_KEY="your_azure_openai_api_key"
AZURE_OPENAI_ENDPOINT="your_azure_openai_endpoint"
CHAT_DEPLOYMENT="your_chat_deployment_name"
AZURE_OPENAI_EMBEDDING_DEPLOYMENT="your_embedding_deployment_name"

# Optional / Vector DB keys (if separate)
AZURE_OPENAI_API_KEY_VB="your_vector_db_azure_api_key"
AZURE_ENDPOINT_VB="your_vector_db_azure_endpoint"

# GROQ (Whisper STT)
GROQ_API_KEY="your_groq_api_key"
```

> ⚠️ Never commit `.env` to the repository. The `.env` file is listed in `.gitignore` by default.

## Usage

### 1. Create the FAISS Vector Database

This step loads `data.json`, creates embeddings, and saves the index to `faiss_index/`.

```bash
python vector_db_creation.py
```

### 2. Run the Streamlit App

```bash
streamlit run app.py
```

Open the URL printed by Streamlit (usually `http://localhost:8501`).

## Data Format (`data.json`)

Each entry must follow this structure:

```json
{
  "id": 22,
  "question": "What is the recommended method to store turmeric in humid regions like Kerala?",
  "answer": "Dry turmeric to below ~12% moisture, sort and clean rhizomes, store in moisture-proof containers in a cool, ventilated area. Use desiccants or raised racks and fumigate with approved agents if pest pressure exists to prevent fungal attack.",
  "region": "Kerala",
  "topic": "Post-harvest / Turmeric"
}
```

Add new Q\&A pairs and re-run `vector_db_creation.py` to update the FAISS index.

## Security & `.gitignore`

If you accidentally added `.env` or `.venv` to Git before updating `.gitignore`, remove them from the index (keeps local files intact):

```bash
# remove from git tracking but keep local files
git rm -r --cached .venv .env

# re-add and commit
git add -A
git commit -m "Remove .venv and .env from tracking and update .gitignore"
```

If you *already pushed* sensitive keys to a remote (GitHub), rotate those keys immediately (Azure & GROQ) and consider using the `git filter-repo` or BFG Repo-Cleaner to scrub history.

## Contributing

Contributions are welcome!

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/AmazingFeature`
3. Commit your changes: `git commit -m 'Add some AmazingFeature'`
4. Push to the branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

Please include tests or example data when possible.

## License

This project is released under the **MIT License**. See [LICENSE](LICENSE) for details.

## Acknowledgements

* Built with ❤️ for the farming community.
* Uses LangChain, Azure OpenAI, GROQ, FAISS, and Streamlit.

---

### Contact / Support

If you have questions or need help, open an issue or reach out at: `adrs3342@gmail.com` (replace with your preferred contact).

<p align="center">Made with ❤️ — <strong>AgroAI</strong></p>
