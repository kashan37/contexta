import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


class RAGPipeline:

    def generate_answer(self, question, retrieved_chunks):

        context = "\n\n".join(retrieved_chunks)

        prompt = f"""
You are a helpful AI assistant.

Answer ONLY using the provided context.

If the answer is not present in the context,
say:
'I couldn't find the answer in the provided document.'
Be friendly andcheerful in your response.

Context:
{context}

Question:
{question}

Answer:
"""

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0
            }
        )

        return response.text