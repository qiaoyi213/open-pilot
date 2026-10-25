import os
from typing import List, Optional
import uuid

#import openai
from openai import OpenAI
from utils.MyVectorDBConnector import MyVectorDBConnector
import pymupdf4llm
from llama_index.readers.file import PyMuPDFReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode

class RAGModel:
    def __init__(self):
        
        self.vector_db = MyVectorDBConnector("my_db")
        

    def load_pdf(self, path: str) -> None:
        """
        Load documents from a PDF file and add them to the Chroma collection.
        
        :param path: Path to the PDF file
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        
        try:
            
            loader = PyMuPDFReader()
            documents = loader.load(file_path=path)

            # 使用 SentenceSplitter 分割句子为节点（可选）
            splitter = SentenceSplitter()
            nodes = splitter.get_nodes_from_documents(documents)

            # 存入向量数据库（注意提取纯文本）
            self.vector_db.add_documents([node.text for node in nodes])
           
        except Exception as e:
            raise Exception(f"Error loading PDF: {str(e)}")
    
    def generate(self, prompt: str, num_results: int = 5) -> str:
        """
        Generate a response based on the prompt and retrieved documents.
        
        :param prompt: Input prompt
        :param max_tokens: Maximum number of tokens in the response
        :param num_results: Number of documents to retrieve
        :param top_p: Top p sampling parameter
        :param temperature: Temperature for response generation
        :return: Generated response
        """
        try:
            results = self.vector_db.search(
                query=prompt,
                top_n=num_results
            )
            
            retrieved_docs = results['documents'][0]
            context = "\n".join(retrieved_docs)

            return context
            
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
        