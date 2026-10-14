from google import genai

from backend.config import settings


client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


def create_embedding(text: str):
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )

    return response.embeddings[0].values


def create_embeddings(chunks: list[str]):
    embeddings = []

    for chunk in chunks:
        embedding = create_embedding(chunk)
        embeddings.append(embedding)

    return embeddings