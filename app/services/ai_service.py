import uuid
import asyncio
from typing import Dict, Any, Optional
import json
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI, ChatAnthropic
import google.generativeai as genai
import openai
from app.core.config import settings


class AIService:
    def __init__(self):
        self.available_models = self._check_available_models()
        self._setup_clients()

    def _check_available_models(self) -> Dict[str, bool]:
        return {
            "openai_text": bool(settings.OPENAI_API_KEY),
            "claude_text": bool(settings.CLAUDE_API_KEY),
            "gemini_text": bool(settings.GEMINI_API_KEY),
            "openai_image": bool(settings.OPENAI_API_KEY),
            "gemini_image": bool(settings.GEMINI_API_KEY)
        }

    def _setup_clients(self):
        if self.available_models["openai_text"]:
            self.openai_llm = ChatOpenAI(
                openai_api_key=settings.OPENAI_API_KEY,
                model_name="gpt-4",
                temperature=0.7
            )

        if self.available_models["claude_text"]:
            self.claude_llm = ChatAnthropic(
                anthropic_api_key=settings.CLAUDE_API_KEY,
                model="claude-2",
                temperature=0.7
            )

        if self.available_models["gemini_text"]:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.gemini_llm = genai.GenerativeModel('gemini-pro')

    async def generate_text(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if self.available_models["openai_text"]:
                return await self._generate_with_openai(prompt, context)
            elif self.available_models["claude_text"]:
                return await self._generate_with_claude(prompt, context)
            elif self.available_models["gemini_text"]:
                return await self._generate_with_gemini(prompt, context)
            else:
                raise Exception("No text generation models available")
        except Exception as e:
            raise Exception(f"Text generation failed: {str(e)}")

    async def generate_image(self, description: str, style: str = "professional") -> Dict[str, Any]:
        try:
            if self.available_models["openai_image"]:
                return await self._generate_image_with_openai(description, style)
            elif self.available_models["gemini_image"]:
                return await self._generate_image_with_gemini(description, style)
            else:
                raise Exception("No image generation models available")
        except Exception as e:
            raise Exception(f"Image generation failed: {str(e)}")

    async def _generate_with_openai(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = self._build_system_prompt(context)
        full_prompt = f"{system_prompt}\n\nUser Request: {prompt}"

        response = await self.openai_llm.ainvoke(full_prompt)
        return self._parse_ai_response(response.content)

    async def _generate_with_claude(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = self._build_system_prompt(context)
        full_prompt = f"{system_prompt}\n\nUser Request: {prompt}"

        response = await self.claude_llm.ainvoke(full_prompt)
        return self._parse_ai_response(response.content)

    async def _generate_with_gemini(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = self._build_system_prompt(context)
        full_prompt = f"{system_prompt}\n\nUser Request: {prompt}"

        response = self.gemini_llm.generate_content(full_prompt)
        return self._parse_ai_response(response.text)

    async def _generate_image_with_openai(self, description: str, style: str) -> Dict[str, Any]:
        enhanced_prompt = f"Professional {style} style: {
            description}. Clean, modern business design."

        response = openai.Image.create(
            prompt=enhanced_prompt,
            n=1,
            size="1024x1024",
            response_format="url"
        )

        return {
            "image_url": response['data'][0]['url'],
            "description": description,
            "style": style
        }

    async def _generate_image_with_gemini(self, description: str, style: str) -> Dict[str, Any]:
        enhanced_prompt = f"Create a professional {
            style} style image: {description}"

        # Note: Gemini's image generation might be different
        # This is a placeholder for Gemini's image generation API
        # We would adjust this later dconco or you can check it for me
        response = self.gemini_llm.generate_content(enhanced_prompt)

        return {
            "image_url": "gemini_generated_image_url",  # Placeholder
            "description": description,
            "style": style
        }

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        business_name = context.get('business_name', '')
        industry = context.get('industry', '')
        tone = context.get('tone', 'professional')
        audience = context.get('target_audience', '')

        return f"""
        You are a professional business content creator. Create high-quality, engaging content.

        Business Context:
        - Name: {business_name}
        - Industry: {industry}
        - Tone: {tone}
        - Target Audience: {audience}

        Provide responses in valid JSON format with appropriate structure for the requested content type.
        Focus on creating practical, actionable business content that drives results.
        """

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        try:
            # Try to parse as JSON first
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            # If not JSON, structure it as text content
            return {
                "content": response_text.strip(),
                "type": "text_response"
            }

    def can_generate_images(self) -> bool:
        return any([
            self.available_models["openai_image"],
            self.available_models["gemini_image"]
        ])

    def get_available_services(self) -> Dict[str, bool]:
        return {
            "text_generation": any([
                self.available_models["openai_text"],
                self.available_models["claude_text"],
                self.available_models["gemini_text"]
            ]),
            "image_generation": self.can_generate_images(),
            "models_available": self.available_models
        }
