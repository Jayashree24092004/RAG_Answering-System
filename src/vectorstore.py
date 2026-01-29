import cohere
import fitz
from pinecone import Pinecone, ServerlessSpec

class VectorStore:
    def __init__(self, pdf_path: str, cohere_api_key: str, pinecone_api_key: str):
        self.pdf_path = pdf_path
        self.co = cohere.Client(cohere_api_key)
        self.pinecone_api_key = pinecone_api_key

        self.chunks = []
        self.embeddings = []

        self.retrieve_top_k = 10
        self.rerank_top_k = 3

        self.load_pdf()
        self.split_text()
        self.embed_chunks()

        if not self.embeddings:
            raise ValueError("No embeddings generated.")

        self.index_chunks()

    def load_pdf(self):
        self.pdf_text = self.extract_text_from_pdf(self.pdf_path)

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        text = ""
        with fitz.open(pdf_path) as pdf:
            for page in pdf:
                text += page.get_text()
        return text

    def split_text(self, chunk_size=1000):
        sentences = self.pdf_text.split(". ")
        current = ""

        for s in sentences:
            if len(current) + len(s) < chunk_size:
                current += s + ". "
            else:
                self.chunks.append(current.strip())
                current = s + ". "

        if current.strip():
            self.chunks.append(current.strip())

    def embed_chunks(self, batch_size=90):
        for i in range(0, len(self.chunks), batch_size):
            batch = self.chunks[i:i+batch_size]

            response = self.co.embed(
                texts=batch,
                input_type="search_document",
                model="embed-english-v3.0"
            )

            self.embeddings.extend(response.embeddings)

    def index_chunks(self):
        pc = Pinecone(api_key=self.pinecone_api_key)
        index_name = "rag-qa-bot"

        if index_name not in pc.list_indexes().names():
            pc.create_index(
                name=index_name,
                dimension=len(self.embeddings[0]),
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )

        self.index = pc.Index(index_name)

        vectors = [
            (str(i), emb, {"text": chunk})
            for i, (emb, chunk) in enumerate(zip(self.embeddings, self.chunks))
        ]

        self.index.upsert(vectors=vectors)

    def retrieve(self, query: str):
        query_emb = self.co.embed(
            texts=[query],
            model="embed-english-v3.0",
            input_type="search_query"
        ).embeddings[0]

        res = self.index.query(
            vector=query_emb,
            top_k=self.retrieve_top_k,
            include_metadata=True
        )

        matches = res["matches"]
        if not matches:
            return []

        docs = [m["metadata"]["text"] for m in matches]

        rerank = self.co.rerank(
            query=query,
            documents=docs,
            top_n=self.rerank_top_k,
            model="rerank-v3.5"
        )

        return [matches[r.index]["metadata"] for r in rerank.results]
