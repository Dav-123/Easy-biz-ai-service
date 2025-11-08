import asyncio
from datetime import datetime
from typing import Dict, Any
from app.services.ai_service import AIService
from app.services.task_service import TaskService
from app.modals.schemas import TaskStatus


class ContentService:
    def __init__(self):
        self.ai_service = AIService()
        self.task_service = TaskService()

    async def generate_brand_kit(self, request_data: Dict[str, Any]) -> str:
        task_id = self.task_service.create_task()
        asyncio.create_task(self._process_brand_kit(task_id, request_data))
        return task_id

    async def _process_brand_kit(self, task_id: str, request_data: Dict[str, Any]):
        try:
            self.task_service.update_task(task_id, TaskStatus.PROCESSING)
            prompts = request_data["prompts"]

            # Brand identity with real AI
            brand_identity = {}
            try:
                brand_identity = await self.ai_service.generate_text(
                    "Create a complete brand identity including brand name, tagline, mission statement, brand values, tone of voice, color palette, and typography suggestions.",
                    prompts
                )
            except Exception as e:
                brand_identity = {"error": f"Brand generation failed: {
                    str(e)}", "name": prompts.get("business_name", "Unknown")}

            # Logo with real AI
            logo_result = None
            try:
                if self.ai_service.can_generate_images():
                    logo_description = f"Professional logo for {prompts.get('business_name')} in {
                        prompts.get('industry')} industry"
                    logo_result = await self.ai_service.generate_image(
                        logo_description,
                        prompts.get('logo_style', 'modern')
                    )
            except Exception as e:
                logo_result = {"error": f"Logo generation failed: {str(e)}"}

            # Social media with real AI
            social_content = {}
            try:
                social_content = await self.ai_service.generate_text(
                    "Create 5 social media post ideas with captions and hashtags for brand promotion.",
                    {**prompts, **brand_identity}
                )
            except Exception as e:
                social_content = {
                    "error": f"Social media generation failed: {str(e)}"}

            result = {
                "brand_identity": brand_identity,
                "logo": logo_result,
                "social_media": social_content,
                "generated_at": datetime.utcnow().isoformat()
            }

            self.task_service.update_task(
                task_id, TaskStatus.COMPLETED, result)

        except Exception as e:
            self.task_service.update_task(
                task_id, TaskStatus.FAILED, error=str(e))

    async def generate_social_media(self, request_data: Dict[str, Any]) -> str:
        task_id = self.task_service.create_task()
        asyncio.create_task(self._process_social_media(task_id, request_data))
        return task_id

    async def _process_social_media(self, task_id: str, request_data: Dict[str, Any]):
        try:
            self.task_service.update_task(task_id, TaskStatus.PROCESSING)
            prompts = request_data["prompts"]

            posts = []
            platforms = ["Facebook", "Instagram", "Twitter", "LinkedIn"]

            for platform in platforms:
                try:
                    post_content = await self.ai_service.generate_text(
                        f"Create 3 engaging {platform} posts for {prompts.get(
                            'business_name')}. Include captions and relevant hashtags.",
                        {**prompts, "platform": platform}
                    )
                    posts.append({
                        "platform": platform,
                        "content": post_content
                    })
                except Exception as e:
                    posts.append({
                        "platform": platform,
                        "error": f"Post generation failed: {str(e)}"
                    })

            banners = []
            try:
                if self.ai_service.can_generate_images():
                    for platform in platforms:
                        banner_desc = f"Professional social media banner for {
                            prompts.get('business_name')} on {platform}"
                        banner = await self.ai_service.generate_image(banner_desc)
                        banners.append({
                            "platform": platform,
                            "banner": banner
                        })
            except Exception as e:
                banners = [{"error": f"Banner generation failed: {str(e)}"}]

            result = {
                "posts": posts,
                "banners": banners,
                "generated_at": datetime.utcnow().isoformat()
            }

            self.task_service.update_task(
                task_id, TaskStatus.COMPLETED, result)

        except Exception as e:
            self.task_service.update_task(
                task_id, TaskStatus.FAILED, error=str(e))

    async def generate_website_content(self, request_data: Dict[str, Any]) -> str:
        task_id = self.task_service.create_task()
        asyncio.create_task(
            self._process_website_content(task_id, request_data))
        return task_id

    async def _process_website_content(self, task_id: str, request_data: Dict[str, Any]):
        try:
            self.task_service.update_task(task_id, TaskStatus.PROCESSING)
            prompts = request_data["prompts"]

            sections = ["hero", "about", "services", "testimonials", "contact"]
            website_content = {}

            for section in sections:
                try:
                    section_content = await self.ai_service.generate_text(
                        f"Create engaging {
                            section} section content for a business website. Include headline, subheadline, and body content.",
                        {**prompts, "section": section}
                    )
                    website_content[section] = section_content
                except Exception as e:
                    website_content[section] = {
                        "error": f"Section generation failed: {str(e)}"}

            result = {
                "website_content": website_content,
                "template_suggestions": ["modern", "professional", "minimalist", "corporate"],
                "generated_at": datetime.utcnow().isoformat()
            }

            self.task_service.update_task(
                task_id, TaskStatus.COMPLETED, result)

        except Exception as e:
            self.task_service.update_task(
                task_id, TaskStatus.FAILED, error=str(e))
