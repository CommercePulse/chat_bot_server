from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import PyPDFLoader
import re

def parse_pdf(file_path: str) -> list:
    # loader = PyPDFLoader(file_path)
    # documents = loader.load()
    # file_name = file_path.split("\\")[-1]
    # text_splitter = RecursiveCharacterTextSplitter(
    #     chunk_size=700, chunk_overlap=100, separators=["\n", " ", ""])
    # docs = text_splitter.split_documents(documents)
    

    # for idx, text in enumerate(docs):
    #             docs[idx].metadata['name']=file_name
    #             docs[idx].metadata['type']='pdf'

    # print(f"\t Total documents created: {len(docs)}",docs)
    # return docs
    
    loader = PyMuPDFLoader(file_path)
    documents = loader.load()
    # file_name = file_path.split("\\")[-1]
    file_name = re.search(r'[^/]+$', file_path).group(0)
    for idx, text in enumerate(documents):
                documents[idx].metadata['name']=file_name
                documents[idx].metadata['type']='pdf'

    print(f"\t Total documents created: {len(documents)}",documents)
    return documents

def parse_text(file_path: str) -> list:
    file_data = open(file_path, 'r', encoding='utf-8')
    file_content = file_data.read()
    print(f"\t Reading a file: {file_path}\n\t Length of the File: {len(file_content)}")
    file_name = file_path.split("\\")[-1]
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
        length_function=len
    )
    docs = text_splitter.create_documents([file_content])
    for idx, text in enumerate(docs):
                docs[idx].metadata['name']=file_name
                docs[idx].metadata['type']='txt'

    print(f"\t Total documents created: {len(docs)}")
    return docs