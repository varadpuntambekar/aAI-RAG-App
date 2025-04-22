from langchain_ollama import OllamaLLM
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader, UnstructuredWordDocumentLoader, UnstructuredPowerPointLoader, UnstructuredExcelLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import os
import re
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
import sys
import logging
from chromadb.config import Settings
import chromadb.utils.embedding_functions 
#Declaring variables that I will use later


def get_application_path():
    # When running as script
    if getattr(sys, 'frozen', False):
        # When running as compiled exe
        return os.path.dirname(sys.executable)
    else:
        # When running as .py script
        return os.path.dirname(os.path.abspath(__file__))

# Set the working directory

# print(f"Working directory set to: {os.getcwd()}")




class embed_search_retrieve(object):

    def __init__(self, rag_directory):
        #initialize the variables such as the vectorstore
        self.persist_directory = f"{rag_directory}_chroma_embeddings"
        self.collection_store = "chroma_collection"
        self.embedding_model = OllamaEmbeddings(model='nomic-embed-text')
        logging.debug(f"Embed model: {self.embedding_model}")
        self.rag_directory = rag_directory
        self.rag_directory_abspath = os.path.abspath(rag_directory)
        logging.debug(f"RAG directory selected {self.rag_directory_abspath}")
        self.persist_directory_abspath = os.path.abspath(self.persist_directory)
        logging.debug(f"Vectorstore directory: {self.persist_directory_abspath}")
        
        logging.debug("Embed Search retrieve class initiated from ctk_interface")

        self.vectorstore = self.create_or_load_vectorstore_exception()
        application_path = get_application_path()
        os.chdir(application_path)
        logging.debug((f"{application_path}"))

   
    
    # def create_or_load_vectorstore(self):
       
    #     try:

    #         logging.debug(f"Creating or Loading vectorstore in {self.persist_directory_abspath}")
    #         self.vectorstore = Chroma(
    #         collection_name=self.collection_store,
    #         persist_directory=self.persist_directory_abspath,
    #         embedding_function=self.embedding_model
    #     )
    #         logging.debug(f"Loaded vectorstore {self.vectorstore._collection_name} with {self.vectorstore._collection.count()} embeddings")
        
    #     except Exception as e:
    #         logging.exception(f"Failed to load vectorstore: %s", e)

    #     return self.vectorstore

    def create_or_load_vectorstore_exception(self):
        logging.debug(f"Creating or Loading vectorstore in {self.persist_directory_abspath}")
        try:
            logging.debug(f"Persist directory exists: {os.path.exists(self.persist_directory_abspath)}")
            logging.debug(f"Embedding model type: {type(self.embedding_model)}")
    
    # Try to create the directory if it doesn't exist
            if not os.path.exists(self.persist_directory_abspath):
                os.makedirs(self.persist_directory_abspath)
                logging.debug(f"Created directory: {self.persist_directory_abspath}")
    
    # Create the vectorstore
            self.vectorstore = Chroma(
            collection_name=self.collection_store,
            persist_directory=self.persist_directory_abspath,
            embedding_function=self.embedding_model
    )
    
    # Test the collection immediately
            try:
                count = self.vectorstore._collection.count()
                logging.debug(f"Successfully accessed collection with {count} embeddings")
            except Exception as inner_e:
                logging.debug(f"Error accessing collection: {inner_e}")
        
            logging.debug(f"Loaded vectorstore {self.vectorstore._collection_name} with {self.vectorstore._collection.count()} embeddings")
    
            return self.vectorstore
        except Exception as e:
            logging.debug(f"Error creating vectorstore: {e}")
            import traceback
            logging.debug(f"Traceback: {traceback.format_exc()}")
            raise

    def files_to_load(self):
        '''
        Input: Directory path with multiple subdirectories, 
        Output: A list of files that haven't been embedded in the vectorstore
        '''
        all_flies_in_vectorstore = set()
        files_in_vectorstore = self.vectorstore._collection.get(include=['metadatas'])
        for metadata in files_in_vectorstore['metadatas']:
            if metadata and 'source' in metadata:
                all_flies_in_vectorstore.add(os.path.abspath(metadata['source']))
    
        files_to_load = []
        for root, _, files in os.walk(self.rag_directory_abspath):
            for file in files:
                filepath = os.path.abspath(os.path.join(root, file))
                if filepath not in all_flies_in_vectorstore:
                    files_to_load.append(filepath)

        return files_to_load

    def embded_files(self, document_list, update_progress = None):
        '''
        Input a vectorstore and a list of documents to be embedded into that vectorstore
        '''
        for i, doc in enumerate(document_list):
            logging.debug(f"Embedding file {doc.metadata.get('source')} right now")
            self.vectorstore.add_documents([doc])
            logging.debug(f"Embdedded {i+1} files out of {len(document_list)} total files")
            
            if update_progress:
                update_progress((i+1)/len(document_list))

                

        logging.debug(f"===Added all files===")
        self.updated_vectorstore = self.vectorstore
        return self.updated_vectorstore


    def load_docs(self, doc_list):
        '''
        Input: A list of files that have not been embedded
        Returns: A list of documents with metadata and page content to be split and embedded
        '''
        docs_to_split = []
        for file in doc_list:
            
            if file.endswith('.pdf'):
                loader = PyPDFLoader( file, mode='single')
                one_page = loader.load()
                docs_to_split.extend(one_page)
            
            if file.endswith('.docx' or '.doc'):
                loader = UnstructuredWordDocumentLoader(file, mode = 'single')
                one_page = loader.load()
                docs_to_split.extend(one_page)

            if file.endswith('.xlsx' ):
                loader = UnstructuredExcelLoader(file, mode='single')
                one_page = loader.load()
                docs_to_split.extend(one_page)
            
            if file.endswith('.ppt' or 'pptx'):
                loader = UnstructuredPowerPointLoader( file, mode = 'single')
                one_page = loader.load()
                docs_to_split.extend(one_page)

        logging.debug(f"==={len(docs_to_split)} Docs locked and loaded, ready to be split and embedded ====")
        return docs_to_split

    def split_docs(self,doc_list):
        '''
        Input: A list of documents to be split
        Returns: A list of chunked documents to be embedded (chunks are usually a lot bigger in number)
        '''
        text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 100)
    
        chunked_doc_list = []
        for doc in doc_list:
            logging.debug(f"Splitting doc {doc.metadata.get('source')}")
            doc_chunks = text_splitter.split_documents([doc])
            for chunk in doc_chunks:
                chunked_doc_list.append(chunk)

        logging.debug(f"===All docs now split, chunks created = {len(chunked_doc_list)}===")
        return chunked_doc_list


    def load_and_embed_docs(self, update_progress = None):
        '''
        Input: A directory path from which to load files
        Return: A vectorstore with all the files added
        '''

        #Getting a list of files that have not been loaded and embedded already in the vectorstore
        logging.debug(f"Load and Embed function activated")
        
        self.loading_file_list = self.files_to_load()

        logging.debug(len(self.loading_file_list)) 
        if not self.loading_file_list:
            logging.debug(f"All docs from this folder have already been embedded")
        #loading the files that are not in the vectorstore
        self.files_loaded = self.load_docs(doc_list=self.loading_file_list)

    #chunking the loaded files
        self.chunked_flies = self.split_docs(doc_list=self.files_loaded)

    #embedding these chunked files
        self.updated_vectorstore = self.embded_files(document_list= self.chunked_flies, update_progress = update_progress)

        return self.updated_vectorstore

    def retrieve_chunks(self, question, n_results = 3):
        '''
        Input: Query that the user asks and the vectorstore which stores all the embeddings
        '''
        
        retriever = self.updated_vectorstore.as_retriever(search_kwargs = {'k': n_results})
        retrieved_chunks = retriever.invoke(question)

        return retrieved_chunks





def chat(question, context):
    '''
    Takes in a user input and generates a response from an LLM
    '''
    
    
    template = '''
            You are a question answer answering assistant with Retrieval Augmented Generation Capabilities. The context entered
            here is the question entered by the user and a document that has been searched and retrieved to be the most relevant to the 
            user's query.

            If asked by the user specifically, you can also act as a summarization agent, that summarizes the document in 100 words or so.

            Use three sentences maximum to answer the question and also provide a brief explanation as to which information in the context helped
            you answer the user's question.


        "Context": {context}
        "question":{question}
        "Answer":

            '''
    prompt = ChatPromptTemplate.from_template(template)


    model = OllamaLLM(model="llama3.2:1b")
    
    inputs = {
        "context":context,
        "question":question

    }
    


    chain = ( 
             prompt 
             | model
    )
    if question.lower() == 'exit':
        ai_message = "It was nice chatting with you"
        return ai_message
        
    else:
        ai_message = chain.invoke(inputs)
        return ai_message
            
