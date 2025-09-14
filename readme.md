<div align="center"><img src="https://www.google.com/search?q=https://placehold.co/600x300/2E7D32/FFFFFF%3Ftext%3DAgroAI%26font%3Draleway" alt="AgroAI Banner"><h1 align="center">🌱 AgroAI: Smart Farming Assistant</h1><p align="center">An intelligent, voice-enabled agricultural assistant designed to provide Indian farmers with instant, accurate, and actionable advice.</p><!-- Badges --><p align="center"><img src="https://www.google.com/search?q=https://img.shields.io/badge/Python-3.9%252B-blue.svg" alt="Python Version"><img src="https://www.google.com/search?q=https://img.shields.io/badge/Framework-Streamlit-red.svg" alt="Streamlit"><img src="https://www.google.com/search?q=https://img.shields.io/badge/AI/ML-LangChain%2520%257C%2520OpenAI-green.svg" alt="AI/ML Stack"><img src="https://www.google.com/search?q=https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"></p></div>AgroAI is a sophisticated voice-first chatbot built to bridge the information gap for farmers. Leveraging a powerful Retrieval-Augmented Generation (RAG) architecture, it provides answers grounded in a specialized agricultural knowledge base, ensuring the advice is both relevant and reliable.✨ Key Features🗣️ Voice-First Interaction: Ask questions naturally in your own voice. AgroAI uses GROQ's Whisper model for fast and accurate speech-to-text.🔊 Audio Responses: Get clear, spoken answers, making information highly accessible.🧠 RAG-Powered Accuracy: Answers are generated based on a curated knowledge base (data.json), preventing hallucinations and providing reliable, context-specific advice.💬 Conversational Memory: The assistant remembers the last five interactions to understand follow-up questions and provide coherent, contextual conversations.📈 Real-time Analytics: A clean dashboard on the UI displays session statistics.🎨 Modern UI: A responsive and intuitive user interface built with Streamlit, designed for ease of use.🛠️ Technology StackFrontend: StreamlitCore Logic: PythonAI/ML Framework: LangChainLLM & Embeddings: Azure OpenAISpeech-to-Text: GROQ API (Whisper-large-v3)Vector Database: FAISS (Facebook AI Similarity Search)Audio Processing: Sounddevice, SciPy🏗️ System ArchitectureThe application follows a Retrieval-Augmented Generation (RAG) pipeline to ensure grounded and accurate responses.User Input (Text/Voice): The user asks a question through the Streamlit UI, either by typing or speaking. Voice input is transcribed to text.Vector Similarity Search: The user's question is converted into a vector embedding. This embedding is used to query the FAISS vector database to find the most relevant question-answer pairs from the data.json knowledge base.Context Augmentation: The retrieved documents (context) are passed to the language model along with the user's original question and the recent conversation history.Response Generation: The Azure OpenAI model generates a comprehensive and context-aware answer.Text-to-Speech: The generated text is converted into an audio response.UI Output: The final text and audio answer are displayed in the Streamlit interface.📁 Project Structureagro-ai-assistant/
│
├── 📄 .gitignore
├── 📄 app.py                # Main Streamlit application UI
├── 📄 farm_bot.py           # Core logic, RAG pipeline, and assistant class
├── 📄 vector_db_creation.py # Script to create the FAISS vector database
├── 📄 data.json             # Knowledge base with agricultural Q&A
├── 📦 faiss_index/          # Directory storing the FAISS vector index
│   └── ...
├── 📄 requirements.txt      # Python dependencies
└── 📄 README.md             # You are here!
🚀 Getting StartedFollow these steps to set up and run the project locally.1. PrerequisitesPython 3.9 or higherGitA virtual environment manager (e.g., venv)2. InstallationClone the Repositorygit clone [https://github.com/your-username/agro-ai-assistant.git](https://github.com/your-username/agro-ai-assistant.git)
cd agro-ai-assistant
Create and Activate a Virtual Environment# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
Install Dependenciespip install -r requirements.txt
Set Up Environment VariablesCreate a file named .env in the root directory of the project and add the following keys. This file is listed in .gitignore and will not be committed to GitHub.# Azure OpenAI API Keys for Chat & Embeddings
AZURE_OPENAI_API_KEY="your_azure_openai_api_key"
AZURE_OPENAI_ENDPOINT="your_azure_openai_endpoint"
CHAT_DEPLOYMENT="your_chat_deployment_name" # e.g., gpt-4o-mini

# Keys for the Vector Database endpoint
AZURE_OPENAI_API_KEY_VB="your_vector_db_azure_api_key"
AZURE_ENDPOINT_VB="your_vector_db_azure_endpoint"
AZURE_OPENAI_EMBEDDING_DEPLOYMENT="your_embedding_deployment_name" # e.g., text-embedding-ada-002

# GROQ API Key for Speech-to-Text
GROQ_API_KEY="your_groq_api_key"
3. UsageCreate the Vector DatabaseBefore running the main application, you need to create the vector store from your knowledge base. Run the following command in your terminal:python vector_db_creation.py
This will process data.json, generate embeddings, and save the FAISS index in the faiss_index directory.Launch the ApplicationOnce the vector database is created, start the Streamlit application:streamlit run app.py
The application should now be open and running in your web browser!📊 Data Source (data.json)The knowledge base for the RAG pipeline is powered by data.json. The quality of the assistant's answers depends heavily on the quality of this data. Each entry in the JSON file must follow this structure:{
  "id": 22,
  "question": "What is the recommended method to store turmeric in humid regions like Kerala?",
  "answer": "Dry turmeric to below ~12% moisture, sort and clean rhizomes, store in moisture-proof containers in a cool, ventilated area. Use desiccants or raised racks and fumigate with approved agents if pest pressure exists to prevent fungal attack.",
  "region": "Kerala",
  "topic": "Post-harvest / Turmeric"
}
You can expand the knowledge base by adding more question-answer pairs in the same format and re-running vector_db_creation.py.🤝 ContributingContributions are welcome! If you have suggestions for improvements, please feel free to open an issue or submit a pull request.Fork the ProjectCreate your Feature Branch (git checkout -b feature/AmazingFeature)Commit your Changes (git commit -m 'Add some AmazingFeature')Push to the Branch (git push origin feature/AmazingFeature)Open a Pull Request📄 LicenseThis project is distributed under the MIT License. See LICENSE for more information.<div align="center">Made with ❤️ for the farming community.</div>