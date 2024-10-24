import os
from config import constants
from utils.backgroud_exeption import handleExceptions
from utils.processor import parse_pdf,parse_text
from dotenv import load_dotenv
from pinecone import Pinecone
load_dotenv()
from langchain_openai import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI 
from langchain_pinecone import  PineconeVectorStore
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.chains import RetrievalQA
from langchain.agents import Tool
from langchain.agents import initialize_agent
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI



embed_model = OpenAIEmbeddings(
    model=os.getenv('EMBED_MODEL_NAME'),
    openai_api_key=os.getenv('OPENAI_API_KEY')
)

# conversational memory
conversational_memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    k=5,
    return_messages=True
)

        
pc=Pinecone(api_key=os.getenv('PINECONE_API_KEY'), environment=os.getenv('PINECONE_ENV'))

class PineconeService:  
    
    @handleExceptions
    async def vectorize_documents_main(self,namespace_id: str):
            print("inside the vectorize_documents_main")
            in_process_dir: str = os.path.join(constants.UPLOAD_DIR, namespace_id, constants.PRIMARY_FOLDER)
    
            documents = dict()
            documents[namespace_id] = list()

            for file in os.listdir(in_process_dir):
                if os.path.isdir(file):
                    print(f"Skipping {file}")
                    continue

                if not os.path.isdir(file):
                    file_path: str = os.path.join(in_process_dir, file)
                    print(f"Processing file: {file}")
                    file_ext = file.split('.')[-1]
                    if file_ext == 'txt':
                        documents[namespace_id].extend(parse_text(file_path))
                    elif file_ext == 'pdf':
                        documents[namespace_id].extend(parse_pdf(file_path))

                    os.remove(file_path)

            pinecone_namespace = namespace_id

            
            for key, val in documents.items(): 
                vectorstore_from_docs_faq = PineconeVectorStore.from_documents(
                    documents[key],
                    index_name=os.getenv('PINECONE_INDEX'),
                    embedding=embed_model,
                    namespace=pinecone_namespace
                )

            return {"message":"To access your bot, use below URL. (Note: Copy this for future reference, else you won't be able to","url":f"{os.getenv('BASE_URL')}?namespace_id={namespace_id}&status=chat&route=llm"}

     
  
    @handleExceptions
    async def delete_vectorized_docs(self, namespace_id: str, key: str, values: list[str]):
        index = pc.Index(os.getenv('PINECONE_INDEX'))   
        filter_condition = {key: {"$in": values}}
        response = index.delete(delete_all=False, namespace=namespace_id, filter=filter_condition)
        return response   

    async def get_agent(self,namespace_id: str):
        
        index = pc.Index(os.getenv('PINECONE_INDEX'))

        vectorstore = PineconeVectorStore(
            index=index, embedding=embed_model, text_key=os.getenv('PINECONE_TEXT_FIELD'), namespace=namespace_id
        ) 

        # chat completion llm
        llm = ChatOpenAI(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            model_name=os.getenv('MODEL'),
            temperature=os.getenv('TEMPERATURE'),
            # streaming=True   
        ) 

        # Use the retriever with the filter
        # retriever = vectorstore.as_retriever(filter=filter_condition) 

        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever()
        ) 

        tools = [
            Tool(
                name='Knowledge Base',
                func=qa.run,
                description=(
                    'use this tool when answering general knowledge queries to get '
                    'more information about the topic'
                )
            )
        ]
    
        agent = initialize_agent(
            agent='chat-conversational-react-description',
            tools=tools,
            llm=llm,
            verbose=True,
            max_iterations=3,
            early_stopping_method='generate',
            memory=conversational_memory
        )
        
        
        # # Fetch data directly from the vector store using the retriever
        # retrieved_data = vectorstore.as_retriever().get_relevant_documents(user_query)
        # # Print the data retrieved from the vector database
        # print('Data retrieved from vector database----:', retrieved_data)
        # # Optionally, run the agent to generate a response based on the retrieved data
        # response = await agent.invoke({"input": user_query})
        # print('Response from agent:', response)
        # if conversational_memory.chat_memory.messages:
        #   chat_history = conversational_memory.chat_memory.messages
        #   for i, message in enumerate(chat_history):
        #       print(f"Conversation {i + 1}: {message.content}")
        # else:
        #     print("No conversations found in memory.")

        return agent

    async def chain_resp(self,namespace_id: str,question: str, chatHistory: str):
        print("inside chain resp ---")
        # template = """Answer only based on the provided document content and chat history. Do not use external sources like Google or any other database. If the document contains relevant information, answer strictly based on that information. If the document does not contain an answer to the question, respond with 'There is no answer to your question in the document.' If the question is irrelevant to the document or cannot be answered based on the document, respond with 'Irrelevant question.'

        # Refer to the chat history only for context if needed, not for factual information
        
        # File Content: {fileContent}
        # Chat History: {chatHistory}
        # question: {question}
        
        # I have a document where each paragraph includes a specific page number and file name. When answering my question, please ensure that the answer references the corresponding page number and file name from the document you are using. Here's the structure of the data:

        # For More Reference See Page Number: X in File Name: Y <Paragraph>
        # Based on this, please answer my question with specific references to the source.
        # Format the text response based on the language detected. If the language is Arabic or any other right-to-left language, ensure the text is displayed in a right-to-left format with proper alignment. If the language is English or another left-to-right language, ensure the text follows a left-to-right format. Consider appropriate punctuation, alignment, and spacing based on the direction of the text.
        # """
        
        # deployed one
        
    #     template = """Answer the user's question based on the provided document content.However, respond to general conversational cues (like greetings, follow-ups, or small talk) interactively. For example, respond to greetings (e.g., "Hi," "Hello","Help Me Out") with an appropriate greeting in return, or engage in follow-up questions with a conversational tone.

    #     Input:

    #     File Content: {fileContent}
    #     Chat History: {chatHistory}
    #     Question: {question}
        
    #     Additional Guidelines:

    #     1. Chat History for Relevance: Use the chat history to evaluate the relevance of the question, but not for factual information.
        
    #     2. citing relevant sections with page numbers and file names in the following structure:provide the below line in the language of question
        
    #     For More Reference See Page Number: X in File Name: Y <Paragraph>.
        
    #     Stickily do this Translate this citation line into the same language as the question (e.g.,Arabic for Arabic, French for French, English for English). 
        
    #     3. Ensure the response follows the correct text direction and formatting based on the language:
    #     Right-to-left formatting for languages like Arabic(if there is list number should be right to left).
    #     Left-to-right formatting for languages like English or French.
    #    .
    #     """
        
       
        # template = """Answer the user's question based on the provided document content. Respond to general conversational cues (like greetings, follow-ups, or small talk) interactively without referencing the document. For example, respond to greetings (e.g., "Hi," "Hello", "Help Me Out") with an appropriate greeting in return, or engage in follow-up questions with a conversational tone.

        # Input:

        # File Content: {fileContent}
        # Chat History: {chatHistory}
        # Question: {question}
        
        # Additional Guidelines:

        # 1. Chat History for Relevance: Use the chat history to evaluate the relevance of the question. **If and only if** the question relates to the content of the document, provide relevant references by citing sections with page numbers and file names in the following structure:

        #     For More Reference See Page Number: X in File Name: Y <Paragraph>.

        # 2. .**Translate this citation line And Response into the same language as the question (e.g., Arabic for Arabic, French for French, English for English).**.

        # 3. Ensure the response follows the correct text direction and formatting based on the language:
        #     - Right-to-left formatting for languages like Arabic (if there is a list, number it right-to-left).
        #     - Left-to-right formatting for languages like English or French.

        # 4. **If the question does not relate to the document, do not provide any citation**."""

        template = """Answer the user's question based on the provided document content. Respond to general conversational cues (like greetings, follow-ups, or small talk) interactively without referencing the document. For example, respond to greetings (e.g., "Hi," "Hello", "Help Me Out") with an appropriate greeting in return, or engage in follow-up questions with a conversational tone.

            Input:

            File Content: {fileContent}
            Chat History: {chatHistory}
            Question: {question}
            
            Additional Guidelines:

            1. Chat History for Relevance: Use the chat history to evaluate the relevance of the question. **If and only if** the question relates to the content of the document, provide relevant references by citing sections with page numbers and file names in the following structure:

                For More Reference, See Page Number: X in File Name: Y <Paragraph>.

            2. If the user is not specific, or multiple references are relevant for the single answer, provide one appropriate answer, but list all relevant references, formatted as:

                For More Reference:
                - See Page Number: X in File Name: Y <Paragraph>.
                - See Page Number: Z in File Name: W <Paragraph>.

            3. Translate this citation line and response into the same language as the question (e.g., Arabic for Arabic, French for French, English for English).

            4. Ensure the response follows the correct text direction and formatting based on the language:
                - Right-to-left formatting for languages like Arabic (if there is a list, number it right-to-left).
                - Left-to-right formatting for languages like English or French.

            5. **If the question does not relate to the document, do not provide any citation**."""


        index = pc.Index(os.getenv('PINECONE_INDEX'))
        # Create the prompt template
        prompt_template = ChatPromptTemplate.from_template(template)

        vectorstore = PineconeVectorStore(
            index=index, embedding=embed_model, text_key=os.getenv('PINECONE_TEXT_FIELD'), namespace=namespace_id
        ) 

        # retrieved_data = vectorstore.as_retriever().invoke(question)
        retrieved_data = vectorstore.similarity_search(question,namespace=namespace_id, k=20)
        
        # Create an empty string to hold the combined page contents
        fileContent = ""

        # Iterate through each document and append its page_content to the combined string
        for doc in retrieved_data:
            # print("doc----",doc)
            fileContent += f"{doc.page_content.strip()} \n Page No :{doc.metadata['page']} \n File Name : {doc.metadata['name']}" 

        # print("fileContent--",fileContent)
        if fileContent is None:
            yield "There is no answer to your question in the document."
        else:   
            # Initialize the OpenAI model with environment variables or default values
            llm = ChatOpenAI(
                model_name=os.getenv('MODEL'),
                temperature=os.getenv('TEMPERATURE'),
                # Default temperature if not set
            )

            # Create an LLM chain with the prompt, LLM, and output parser
            prompt =  prompt_template.format(question=question,chatHistory=chatHistory,fileContent = fileContent)
            
            print("Request Send To ChatGPT  ::",prompt)
            chain = llm | StrOutputParser()

            for chunk in chain.stream(prompt):
                    # print("chunk---",chunk)
                    yield chunk 
  

      
            