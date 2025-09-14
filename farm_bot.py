# farm_bot.py
# Core agricultural assistant module with RAG functionality and conversational memory

import os
import base64
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
# LangChain imports
from langchain.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI

# Azure OpenAI client for audio
from openai import AzureOpenAI

# Load environment variables
load_dotenv()
class AgricultureAssistant:
    def __init__(self, vector_db_path: str = "faiss_index"):
        """
        Initialize the Agriclutural Assistant

        Args: 
        vector_db_path: path to the saved vector database
        """
        self.vector_db_path = vector_db_path
        self.vector_store = None
        self.session_memory = []
        self.conversation_history = [] # For conversational context

        # initialize all components
        self.setup_azure_clients()
        self.load_vector_store()

    def setup_azure_clients(self):
        """Setup Azure OpenAI clients and models"""
        try:
            # Audio client for speech-to-text and text-to-speech
            self.audio_client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version="2024-12-01-preview",
                azure_endpoint=os.getenv("ENDPOINT_URL")
            )
            # Embeddings for vector search (must match the ones used to create vector DB)
            self.embeddings = AzureOpenAIEmbeddings(
                azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
                openai_api_version="2024-12-01-preview",
                azure_endpoint=os.getenv("AZURE_ENDPOINT_VB"),
                openai_api_key=os.getenv("AZURE_OPENAI_API_KEY_VB"),
                chunk_size=1000
            )
            
            # Chat model for generating responses
            self.chat_model = AzureChatOpenAI(
                azure_deployment=os.getenv("CHAT_DEPLOYMENT", "gpt-4o-mini"),
                openai_api_version="2024-12-01-preview",
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                temperature=0.3,
                max_tokens=600
            )

            print("✅ Azure OpenAI clients initialized successfully")
    
        except Exception as e:
            print(f"❌ Error initializing Azure clients: {e}")
            raise

    def load_vector_store(self):
        """Load the pre-created vector datavase"""

        try:
            if not os.path.exists(self.vector_db_path):
                raise FileNotFoundError(f"Vector database not found at {self.vector_db_path}")
            
            self.vector_store = FAISS.load_local(
                self.vector_db_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )

            print(f"Vector database loaded")

        except Exception as e:
            print(f" Error loading vector database: {e}")
            raise


    def speech_to_text(self, audio_file) -> str:
        """
        Convert speech to text using GROQ whisper
         
        Args: 
            audio_file: Audio file path
             
        Returns:
            Transcribed text
        """
        try:
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            with open(audio_file, "rb") as file:
                # Fixed: Using correct API method for transcription
                transcription = client.audio.transcriptions.create(
                    file=(os.path.basename(audio_file), file.read()),
                    model="whisper-large-v3-turbo",
                    response_format="text"
                )
                # Return the actual text from the transcription object
                return str(transcription) if transcription else ""
        except Exception as e:
            print(f"❌ Error in speech-to-text: {e}")
            return ""

    def search_knowledge_base(self, query: str, k: int = 2) -> List[Dict]:
        """
        Search for the agricultural knowledge base using vector similarity

        Args: 
            query: User's question
            k: Number of similar documents to retrieve

        Returns: 
            List of relevant Q&A pairs with metadata
        """
        if not self.vector_store:
            print("11111")
            return []
        
        try:
            docs = self.vector_store.similarity_search(query, k = k)

            results = []
            for doc in docs:
                results.append(doc.page_content)

            return results
        except Exception as e:
            print(f"Error searching knowledge base: {e}")
            return []
        

    def generate_answer(self, user_question: str, retrieved_context: List[Dict]):
        """
        Generate a grouded answer using retrieved context and conversation history

        Args:
            user_question: The farmer's question
            retrieved_context: Relevant Q&A pairs from knowledge base

        Returns:
            Generated answer based on context
        """
        if not retrieved_context:
            return ("I couldn't find specific information for your question in our agricultural database. "
                   "Please try rephrasing your question or ask about topics like crop cultivation, "
                   "pest management, fertilizers, or farming techniques."), None
        

        context_parts = []
        for i, qa in enumerate(retrieved_context, 1):
            context_parts.append(
                f"Context {i}:\n"
                f"{qa}"
            )
        
        context = "\n\n".join(context_parts)  


        # Create system prompt with conversation history in mind
        system_prompt = """You are an expert agricultural advisor helping farmers in India. 
        You have access to a curated database of agricultural knowledge and the recent conversation history for context.

        Your primary goal is to provide helpful and contextually aware answers. Follow these guidelines:

        1.  **Analyze the User's Question:** First, determine if the user's question is a new query or a follow-up to the conversation.
            -   A **follow-up question** might refer to the previous answer using words like "this," "that," "it," or ask for more details on the same topic.
            -   A **new query** will introduce a different topic.

        2.  **Answering Follow-up Questions:**
            -   If it's a follow-up, your main source of information should be the **conversation history**.
            -   Refer to the provided **CONTEXT** section only if it adds relevant new information to the ongoing conversation.
            -   If the **CONTEXT** is irrelevant to the follow-up, **ignore it** and answer using the conversation history and your general knowledge. For example, if the last topic was 'PMFBY insurance' and the user asks 'what are its other benefits?', you should continue talking about PMFBY.

        3.  **Answering New Queries:**
            -   If it's a new query, base your answer primarily on the provided **CONTEXT** section from your knowledge base.

        4.  **General Style:**
            -   Be practical, specific, and actionable.
            -   Keep responses concise (2-3 sentences).
            -   Use simple, encouraging, and supportive language for farmers.
            -   If the context is only partially relevant, use what you can and mention any limitations."""
        
        
        human_prompt = f"""Please answer the farmer's question. Use the provided knowledge base context only if it is relevant, as per your instructions.

KNOWLEDGE BASE CONTEXT:
{context}

FARMER'S QUESTION: {user_question}

Answer:"""   
        
        # Construct messages payload with history
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.conversation_history) # Add conversation history
        messages.append({"role": "user", "content": human_prompt})

        completion = self.audio_client.chat.completions.create(
            model = "gpt-4o-audio-preview",
            modalities=["text", "audio"],
            audio={
                "voice": "alloy",
                "format": "wav"
            },
            messages = messages, # Use the new messages list with history
            temperature = 0.7,
            max_tokens = 1000,
            top_p = 1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        text_response = completion.choices[0].message.audio.transcript
        audio_bytes = base64.b64decode(completion.choices[0].message.audio.data)
        return [text_response, audio_bytes]

    def process_question(self, question: str) -> Dict:
        """
        Process a complete question through the RAG pipeline

        Args:
            question: The farmer's question
        
        Returns:
            Dictionary containing answer, sources, and metadeta
        """

        # Step 1: Search knowledge base
        relevant_context = self.search_knowledge_base(question, k=3)
        
        # Step 2: Generate answer
        lit = self.generate_answer(question, relevant_context)
        if lit:
            answer, audio_bytes = lit
        else: 
            print("error generatic response")
            return 

        response = {
            "question": question,
            "answer": answer,
            "sources": relevant_context,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_count": len(relevant_context),
            "audio_bytes": audio_bytes
        }
        
        # Add to conversation history for context
        self.conversation_history.append({"role": "user", "content": question})
        self.conversation_history.append({"role": "assistant", "content": answer})

        # Keep only the last 5 pairs (10 messages)
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]

        # Add to session memory for logging/stats
        self.add_to_session_memory(question, answer, relevant_context)

        return response
    
    def process_audio_question(self, audio_file) -> Dict:
        """
        Process an audio question through the complete pipeline
        
        Args:
            audio_file: Audio file containing the question
            
        Returns:
            Dictionary containing transcription, answer, audio response, and sources
        """

        question = self.speech_to_text(audio_file)
        if not question:
            return {
                "error": "Could not transcribe audio. Please try again.",
                "transcription": "",
                "answer": "",
                "audio_response": b"",
                "sources": []
            }
        # Step 2: Process the question
        response = self.process_question(question)
        return response
    
    def add_to_session_memory(self, question: str, answer: str, sources: List[Dict]):
        """Add interaction to session memory for logging and stats"""
        self.session_memory.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "question": question,
            "answer": answer,
            "sources": sources,
            "source_count": len(sources)
        })
        
        # Keep only last 20 interactions
        if len(self.session_memory) > 20:
            self.session_memory.pop(0)
    
    def get_session_memory(self) -> List[Dict]:
        """Get current session memory"""
        return self.session_memory
    
    def clear_session_memory(self):
        """Clear session memory and conversation history"""
        self.session_memory = []
        self.conversation_history = []
    
    def get_statistics(self) -> Dict:
        """Get usage statistics"""
        total_questions = len(self.session_memory)
        
        if total_questions == 0:
            return {
                "total_questions": 0,
                "avg_sources_per_question": 0,
                "common_topics": [],
                "common_regions": []
            }
        
        # Calculate average sources per question
        total_sources = sum(item["source_count"] for item in self.session_memory)
        avg_sources = total_sources / total_questions if total_questions > 0 else 0
        
        # Get common topics and regions
        all_topics = []
        all_regions = []
        
        for memory in self.session_memory:
            for source in memory["sources"]:
                if source.get("topic"):
                    all_topics.append(source["topic"])
                if source.get("region"):
                    all_regions.append(source["region"])
        
        # Count occurrences
        from collections import Counter
        common_topics = [item[0] for item in Counter(all_topics).most_common(5)]
        common_regions = [item[0] for item in Counter(all_regions).most_common(5)]
        
        return {
            "total_questions": total_questions,
            "avg_sources_per_question": round(avg_sources, 1),
            "common_topics": common_topics,
            "common_regions": common_regions
        }

