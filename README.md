# LLM RAG LangChain

![Sample UI](doc/1.png)

## Description

This project is a prototype agent that uses Large Language Model (LLM) with Retrieval-Augmented Generation (RAG) and various tools to assist with different tasks. The agent is designed to provide relevant and accurate answers based on the given context.

## Features

- **LLM Integration**: Utilizes OpenAI and Ollama models for natural language processing.
- **Retrieval-Augmented Generation (RAG)**: Enhances answer accuracy by retrieving information from relevant documents.
- **Various Tools**: Provides tools for checking orders, creating orders, getting product lists, and more.
- **Chat Interface**: Interactive chat interface using Streamlit.

## Project Structure

- `app.py`: Main file to run the Streamlit application.
- `llm_model.py`: Manages the LLM models used (OpenAI or Ollama).
- `vector_document.py`: Handles documents and processes them into vectors.
- `vector_store_documents.py`: Stores and retrieves vector documents.
- `tools.py`: Defines various tools used by the agent.
- `llm_invocation.py`: Manages sessions and LLM agent invocation.
- `api_client.py`: Manages communication with external APIs.
- `config.py`: Configuration file for storing environment variables.
- `api`: Contains service functions for tools.

## Installation

1. **Clone the Repository**:

   ```sh
   git clone https://github.com/bonkzero404/LLM-RAG-LangChain.git
   cd LLM-RAG-LangChain
   ```

2. **Create a Virtual Environment**:

   ```sh
   python -m venv env
   source env/bin/activate  # For Mac/Linux users
   # .\env\Scripts\activate  # For Windows users
   ```

3. **Install Dependencies**:

   ```sh
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a .env file and add the required environment variables:
   ```env
   OPENAI_MODEL=your_openai_model
   OPENAI_EMBEDDINGS_MODEL=your_openai_embeddings_model
   OLLAMA_MODEL=your_ollama_model
   OLLAMA_EMBEDDINGS_MODEL=your_ollama_embeddings_model
   WITH_OLLAMA=False
   API_URL=https://api.yourdomain.com
   DATA_PATH=./data
   CHROMA_PATH=./chroma
   CHROMA_COLLECTION=your_chroma_collection
   ```
   For a complete configuration of environment variables, refer to the [.env.example](https://github.com/bonkzero404/LLM-RAG-LangChain/blob/main/.env.example) file and [.env.example](https://github.com/bonkzero404/LLM-RAG-LangChain/blob/main/api/.env.example) from api.

## Running the Application

1. **Run Fast API**:

   ```sh
   cd api && uvicorn main:app --reload --port 5050
   ```

   Open the OAS http://localhost:5050/docs

2. **Run Streamlit**:

   ```sh
   streamlit run app.py
   ```

3. **Interact with the Agent**:
   Open your browser and access `http://localhost:8501` to start interacting with the agent.

## Usage

- **Chat with the Agent**: Ask questions or make requests in the chat box.
- **Select LLM Model**: Choose the LLM model to use from the sidebar.
- **View Information Sources**: View information sources from the available text files.

## User Interface

1. **Basic Information**
   ![Sample UI](doc/1.png)
2. **Order Services**
   ![Sample UI](doc/2.png)
3. **Integrate to Payment Gateway**
   ![Sample UI](doc/5.png)
4. **Check Order Status**
   ![Sample UI](doc/3.png)
5. **Request Report Orders**
   ![Sample UI](doc/4.png)
