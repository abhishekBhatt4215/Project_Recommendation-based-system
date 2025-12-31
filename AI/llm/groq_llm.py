import os
from groq import Groq
from dotenv import load_dotenv
from typing import Optional


# Load environment variables
load_dotenv()


def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    return Groq(api_key=api_key)


def call_groq(prompt, system_prompt=None, model=None):
    client = get_groq_client()

    if model is None:
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    messages = []

    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })

    messages.append({
        "role": "user",
        "content": prompt
    })

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.4,
            max_tokens=1024,
            timeout=30,
        )
        return response.choices[0].message.content
    except Exception as e:
        # Wrap and re-raise to be helpful to callers
        raise RuntimeError(f"Groq LLM call failed: {e}")


# ---------------- STREAMING ----------------
def call_groq_stream(prompt: str, model: Optional[str] = None):
    """
    Generator that yields text chunks as the LLM streams output.
    """
    client = get_groq_client()
    model = model or os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    try:
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=2048,
            stream=True,
            timeout=30,
        )

        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta
            if delta and hasattr(delta, "content") and delta.content:
                yield delta.content

    except Exception as e:
        raise RuntimeError(f"Groq streaming call failed: {e}")
