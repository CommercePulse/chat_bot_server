import os
from config import constants
from utils.backgroud_exeption import handleExceptions
from utils.processor import parse_pdf,parse_text
from dotenv import load_dotenv
from pinecone import Pinecone
load_dotenv()
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.embeddings.openai import OpenAIEmbeddings
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
    
    # @handleExceptions
    async def vectorize_documents_main(self,namespace_id: str):
       
        in_process_dir: str = os.path.join(constants.UPLOAD_DIR, namespace_id, constants.PRIMARY_FOLDER)
 
        print(f"Using OpenAI Key---------: {os.getenv('OPENAI_API_KEY')}")

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

                # shutil.move(file_path, os.path.join(processed_dir, file))
                os.remove(file_path)


        # pinecone_namespace = f"ns_{namespace_id}"
        pinecone_namespace = namespace_id

        # print('documents.items()---',documents.items())
        # return
        for key, val in documents.items(): 
            vectorstore_from_docs_faq = PineconeVectorStore.from_documents(
                documents[key],
                index_name=os.getenv('PINECONE_INDEX'),
                embedding=embed_model,
                namespace=pinecone_namespace
            )

        return {"message":"To access your bot, use below URL. (Note: Copy this for future reference, else you won't be able to","url":f"{os.getenv('BASE_URL')}?namespace_id={namespace_id}&status=chat&route=llm"}


        
        # st.success(f"Total {len(documents[namespace_id])} documents created in vector database.")
        # st.write("To access your bot, use below URL. (Note: Copy this for future reference, else you won't be able to "
        #          "access your bot)")
        # st.write(f"{os.getenv('BASE_URL')}?namespace_id={namespace_id}&status=chat&route=llm")
   
    @handleExceptions
    def delete_vectorized_docs(self, namespace_id: str, key: str, values: list[str]):
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
        # Define the prompt template with placeholders for question, chatHistory, and file
        print("inside chain resp ---")
        template = """Answer the question based only on the following context:
        File Content: {fileContent}
        Chat History: {chatHistory}
        question: {question}
        """
        index = pc.Index(os.getenv('PINECONE_INDEX'))
        # Create the prompt template
        prompt_template = ChatPromptTemplate.from_template(template)

        vectorstore = PineconeVectorStore(
            index=index, embedding=embed_model, text_key=os.getenv('PINECONE_TEXT_FIELD'), namespace=namespace_id
        ) 

        retrieved_data = vectorstore.as_retriever().invoke(question)

        # Create an empty string to hold the combined page contents
        fileContent = ""

        # Iterate through each document and append its page_content to the combined string
        for doc in retrieved_data:
            fileContent += doc.page_content.strip() + "\n" 

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
                yield chunk 
  

      
            