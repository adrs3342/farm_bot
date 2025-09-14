"""
this script creates a vector database using openai embedding, faiss and Langchain
"""
import json
import os
import sys
from typing import List, Dict
from dotenv import load_dotenv

# LangChain imports
from langchain_openai import AzureOpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
# Load environment variables
load_dotenv()

embeddings = AzureOpenAIEmbeddings(
                azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
                openai_api_version="2024-12-01-preview",
                azure_endpoint="https://azureopenaigenai2.openai.azure.com/",
                openai_api_key=os.getenv("AZURE_OPENAI_API_KEY_VB"),
                chunk_size=1000
            )
with open("data.json", 'r', encoding='utf-8') as file:
                data = json.load(file)
def create_documtents(json_data: List[Dict]) -> List[Document]:
    """Converts json data to langchain documents"""
    documents = []

    for item in json_data:
        doc_text = f"""
        Full Context: This advisory is about {item['topic']} in {item['region']}. The question asked is "{item['question']}", and the recommended answer is "{item['answer']}".
"""
        
        doc = Document(
            page_content = doc_text,
            metadata = {  # adding metadeta so that i can use them later for retrieving based on the filter or using for keyword search
                "id": item["id"],
                "region": item["region"],
                "topic": item["topic"],
                "search_text": f"{item['question']} {item['answer']} {item['region']} {item['topic']}",
            }
        )

        documents.append(doc) 
    print(f"Created {len(documents)} documents for vector indexing")
    return documents


def create_vector_store(documents: List[Document]) -> FAISS:
    """Create FAISS vector store from documents"""

    try:
        vector_store = FAISS.from_documents(documents, embeddings)
        print("vectore store created successfully")
        return vector_store
    except Exception as e:
        print(f"error creating vector store {e}")
documents = create_documtents(data)
v_db = create_vector_store(documents)
v_db.save_local("faiss_index")