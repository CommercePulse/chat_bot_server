import socket
hostname = socket.gethostname()
UPLOAD_DIR = "./upload"
INTERMEDIATE_FOLDER = "in-process"
PROCESSED_FOLDER = "processed"
PRIMARY_FOLDER = "uploaded-file"
DEFAULT_PROMPT = """From now on, you will assume the role of support executive who will answer user queries from the provided context only.
    If user asks something which is not in the context then you reply in very generic manner that you can't help or answer the provider query and user should raise the support ticket in the system.
    
    Utilize all available resources provided in the context to expand your skills and continue answering the user queries.
    """

 
BASE_URL = socket.gethostbyname(hostname)
OPENAI_API_KEY="sk-svcacct-07V3nqED8qMUwnQGO61YRq6VUFkxicrW5BiHHHF7pJa7X8ruOp_u3qT5vqWb8edT3BlbkFJy5_dBmzyT77hbLy4wafuHWGpFHJUCW_NT5VsENkunP6dSaaFaawzK1raiOEcAAA"
PINECONE_API_KEY="86de39ab-2e09-4023-9aeb-bcd877cb24a7"
PINECONE_ENV="us-east-1"
PINECONE_INDEX="chatbot"
PINECONE_TEXT_FIELD="text"
EMBED_MODEL_NAME="text-embedding-ada-002"
 
