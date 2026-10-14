
import re
import httpx

from google import genai
from google.genai import types, errors

from backend.config import settings
from backend.rag.context_builder import build_context


client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)

UNAVAILABLE = (
    "I could not find this information in the "
    "provided documents."
)


def local_rag_fallback(question: str, context: str) -> str:
    question_lower = question.lower()

    # Reject requested years missing from the retrieved context.
    requested_years = set(
        re.findall(r"\b(?:19|20)\d{2}\b", question_lower)
    )
    available_years = set(
        re.findall(r"\b(?:19|20)\d{2}\b", context)
    )

    if requested_years and not requested_years.issubset(available_years):
        return UNAVAILABLE

    if not context.strip():
        return UNAVAILABLE

    # Identify the requested financial metric.
    if "revenue" in question_lower:
        target = "revenue"
    elif "expense" in question_lower:
        target = "expenses"
    elif "profit" in question_lower:
        target = "profit"
    else:
        # Return retrieved context only for a general report question.
        normalized_context = re.sub(
            r"\bRs\.?\s*",
            "₹",
            context,
            flags=re.IGNORECASE,
        )
        return (
            "According to the financial report:\n"
            f"{normalized_context}\n"
            "(Source: retrieved financial document)"
        )

    # Return only the requested metric.
    for line in context.splitlines():
        match = re.match(
            rf"^\s*{re.escape(target)}\s*:\s*(.+?)\s*$",
            line,
            flags=re.IGNORECASE,
        )

        if match:
            value = re.sub(
                r"\bRs\.?\s*",
                "₹",
                match.group(1).strip(),
                flags=re.IGNORECASE,
            )

            return (
                f"{target.capitalize()}: {value} "
                "(Source: retrieved financial document)"
            )

    return UNAVAILABLE


def run_rag_agent(question: str) -> str:
    context = build_context(question)

    if not context or not context.strip():
        return UNAVAILABLE

    # Validate years before asking Gemini.
    requested_years = set(
        re.findall(r"\b(?:19|20)\d{2}\b", question.lower())
    )
    available_years = set(
        re.findall(r"\b(?:19|20)\d{2}\b", context)
    )

    if requested_years and not requested_years.issubset(available_years):
        return UNAVAILABLE

    prompt = f"""
You are FinVoice AI's document-based financial assistant.

Rules:
- Answer using ONLY the retrieved context below.
- Never invent information or use outside knowledge.
- If requested information is absent, respond exactly:
  "{UNAVAILABLE}"
- Financial amounts are in Indian Rupees.
- Use ₹ for monetary values.
- Keep answers concise.
- Identify the source document when possible.
- Do not claim that a year is supported unless it appears in context.

Retrieved context:
{context}

User question:
{question}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
            ),
        )

        if response.text:
            return response.text

        return local_rag_fallback(question, context)

    except errors.ClientError as error:
        if getattr(error, "code", None) == 429:
            return local_rag_fallback(question, context)
        raise

    except (httpx.ConnectError, httpx.TimeoutException):
        return local_rag_fallback(question, context)