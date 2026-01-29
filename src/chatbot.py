import re

class Chatbot:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore

    def respond(self, user_message: str):
        retrieved_docs = self.vectorstore.retrieve(user_message)

        if not retrieved_docs:
            return "No relevant information found in the document.", []

        answer = self._generate_answer(user_message, retrieved_docs)

        return answer, retrieved_docs

    def _generate_answer(self, question, docs):
        # Combine text
        text = " ".join([d["text"] for d in docs])

        # Clean text
        text = re.sub(r"\s+", " ", text)

        # Select most relevant sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)

        keywords = set(question.lower().split())

        scored = []
        for s in sentences:
            score = sum(1 for w in s.lower().split() if w in keywords)
            scored.append((score, s))

        scored.sort(reverse=True, key=lambda x: x[0])

        best_sentences = [s for _, s in scored[:5]]

        answer = "Based on the document:\n\n" + "\n".join(best_sentences)

        return answer
