import os

from groq import Groq
from sqlalchemy.orm import Session

from app import models


class ChatService:
    def __init__(self):
        self.model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        self.client = None

    def _get_client(self) -> Groq:
        if self.client is None:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY is not configured")
            self.client = Groq(api_key=api_key)
        return self.client

    async def ask_question(self, doc_id: str, question: str, user_id: str, db: Session) -> str:
        client = self._get_client()

        # Get relevant chunks using RAG
        relevant_chunks = self.retrieve_relevant_chunks(doc_id, question, db, top_k=3)
        context = "\n".join([chunk.text_content for chunk in relevant_chunks]).strip()

        # Create prompt
        prompt = f"""
You are a helpful document assistant.
Answer only from the provided document context.
If the answer is not in the context, say you could not find it in the document.
If the context contains images, describe them.
You can translate content if the user asks.

Document Context:
{context or "No relevant document context was found."}

Question:
{question}
"""

        response = client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        answer = response.choices[0].message.content or "I could not generate an answer."

        # Save to chat history
        user_message = models.ChatMessage(
            document_id=doc_id,
            user_id=user_id,
            role="user",
            content=question,
        )
        assistant_message = models.ChatMessage(
            document_id=doc_id,
            user_id=user_id,
            role="assistant",
            content=answer,
        )
        db.add(user_message)
        db.add(assistant_message)
        db.commit()

        return answer

    def retrieve_relevant_chunks(self, doc_id: str, question: str, db: Session, top_k: int = 3):
        # Simple keyword-based search
        chunks = db.query(models.DocumentChunk).filter(models.DocumentChunk.document_id == doc_id).all()

        if not chunks:
            return []

        # Score chunks based on keyword overlap
        question_words = set(question.lower().split())
        scores = []

        for chunk in chunks:
            chunk_words = set(chunk.text_content.lower().split())
            overlap = len(question_words & chunk_words)
            scores.append((chunk, overlap))

        # Sort by score and return top_k
        scores.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in scores[:top_k]]
