"""
Groq LLM Client Wrapper.

Provides async chat completion, token streaming, timeout protection,
and provider error handling. Falls back to educational mock stream if no API key.
"""

from collections.abc import AsyncGenerator

import httpx

from app.core.config import settings
from app.core.logging import logger
from app.core.observability.opik import opik_tracer

try:
    from groq import APIError, APITimeoutError, AsyncGroq, RateLimitError

    GROQ_SDK_AVAILABLE = True
except ImportError:
    GROQ_SDK_AVAILABLE = False


class GroqClient:
    """Production-grade asynchronous Groq client."""

    def __init__(self) -> None:
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.timeout = settings.GROQ_TIMEOUT_SECONDS
        self.client: AsyncGroq | None = None

        if self.api_key and GROQ_SDK_AVAILABLE:
            self.client = AsyncGroq(
                api_key=self.api_key,
                timeout=httpx.Timeout(self.timeout, connect=10.0),
            )
            logger.info(f"Groq client initialized with model '{self.model}'.")
        else:
            logger.info(
                "Groq API key not configured or SDK unavailable; using mock LLM generator for local development."
            )

    async def generate_response(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Generates a non-streaming completion response."""
        with opik_tracer.trace_span(
            "groq_generate_response",
            {"model": self.model, "messages_len": len(messages)},
        ) as span:
            if not self.client:
                mock_text = (
                    "[Mock Eve Response - Groq API key not set]\n"
                    "I received your message. Set GROQ_API_KEY to connect to live Groq Llama 3 models."
                )
                span["output"] = mock_text
                return mock_text

            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,  # type: ignore
                    temperature=temperature
                    if temperature is not None
                    else settings.GROQ_TEMPERATURE,
                    max_tokens=max_tokens or settings.GROQ_MAX_TOKENS,
                )
                content = response.choices[0].message.content or ""
                span["output"] = content
                return content
            except APITimeoutError as exc:
                logger.error(f"Groq API call timed out after {self.timeout}s: {exc}")
                raise TimeoutError(
                    "LLM provider timed out processing request."
                ) from exc
            except RateLimitError as exc:
                logger.error(f"Groq rate limit exceeded: {exc}")
                raise RuntimeError(
                    "LLM rate limit reached. Please try again shortly."
                ) from exc
            except APIError as exc:
                logger.error(f"Groq API error: {exc}")
                raise RuntimeError(f"Groq API error: {exc.message}") from exc
            except Exception as exc:
                logger.error(f"Unexpected error communicating with Groq: {exc}")
                raise

    async def stream_response(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[str, None]:
        """Streams completion tokens one by one asynchronously."""
        if not self.client:
            mock_tokens = [
                "Hello! ",
                "I am Eve, ",
                "your AI assistant. ",
                "I am currently operating ",
                "in mock development mode ",
                "because GROQ_API_KEY is not yet configured. ",
                "Configure GROQ_API_KEY to enable live inference with Groq!",
            ]
            for token in mock_tokens:
                yield token
            return

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore
                temperature=temperature
                if temperature is not None
                else settings.GROQ_TEMPERATURE,
                max_tokens=max_tokens or settings.GROQ_MAX_TOKENS,
                stream=True,
            )
            async for chunk in stream:
                if (
                    chunk.choices
                    and chunk.choices[0].delta
                    and chunk.choices[0].delta.content
                ):
                    yield chunk.choices[0].delta.content
        except APITimeoutError as exc:
            logger.error(f"Groq streaming timed out: {exc}")
            yield "\n[Error: LLM streaming timed out.]"
        except RateLimitError as exc:
            logger.error(f"Groq streaming rate limited: {exc}")
            yield "\n[Error: LLM rate limit exceeded. Please retry shortly.]"
        except Exception as exc:
            logger.error(f"Error during Groq streaming: {exc}")
            yield f"\n[Error communicating with LLM provider: {exc}]"


groq_client = GroqClient()
