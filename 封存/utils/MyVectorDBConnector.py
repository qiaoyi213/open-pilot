import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

default_ef = embedding_functions.DefaultEmbeddingFunction() # chroma内置的向量转换模型 -- all-MiniLM-L6-v2


class MyVectorDBConnector:
    def __init__(self, collection_name, embedding_fn=default_ef):

        # 1、 Ephemeral Client ：基于内存（一旦服务器重启则数据就会清空，不推荐）
        chroma_client = chromadb.Client(Settings(allow_reset=True))  # 基于内存的模式
        # 注意：此处为了测试，实际不需要每次 reset()，并且是不可逆的！
        chroma_client.reset()
        # 2、 Persistent Client ：持久化的形式，把数据落盘（推荐）
        # chroma_client = chromadb.PersistentClient(path="./chroma")

        # 创建一个 collection
        self.collection = chroma_client.get_or_create_collection(name=collection_name)
        self.embedding_fn = embedding_fn # 此处代码设置，若不传入模型，则默认使用内置的向量转换模型

    def add_documents(self, documents):
        '''向 collection 中添加文档与向量'''
        # documents
        self.collection.add(
            embeddings=self.embedding_fn(documents),  # 每个文档的向量
            documents=documents,  # 文档的原文
            ids=[f"id{i}" for i in range(len(documents))]  # 每个文档的 id ，向量索引
        )
        print("Load Successful")

    def search(self, query, top_n):
        '''检索向量数据库'''
        # query 检索的文本 string
        # top_n 要检索出几个文档
        results = self.collection.query(
            query_embeddings=self.embedding_fn([query]),
            n_results=top_n
        )
        return results