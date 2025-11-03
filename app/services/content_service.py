import asyncio
from datetime import datetime
from typing import Dict, Any
from .ai_service import AIService
from .task_service import TaskService
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
            
            brand_identity = await self.ai_service.generate_text(
                "Create a complete brand identity including brand name, tagline, mission statement, brand values, tone of voice, color palette, and typography suggestions.",
                prompts
            )
            
            logo_result = None
            if self.ai_service.can_generate_images():
                try:
                    logo_prompt = f"Create a detailed logo description for {prompts['business_name']} in the {prompts['industry']} industry. Focus on symbolism and professional design."
                    logo_description = await self.ai_service.generate_text(logo_prompt, prompts)
                    logo_result = await self.ai_service.generate_image(
                        logo_description.get('content', logo_description),
                        prompts.get('logo_style', 'modern')
                    )
                except Exception as e:
                    print(f"Logo generation skipped: {e}")
            
            social_content = await self.ai_service.generate_text(
                "Create 5 social media post ideas with captions and hashtags for brand promotion.",
                {**prompts, **brand_identity}
            )
            
            result = {
                "brand_identity": brand_identity,
                "logo": logo_result,
                "social_media": social_content,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            self.task_service.update_task(task_id, TaskStatus.COMPLETED, result)
            
        except Exception as e:
            self.task_service.update_task(task_id, TaskStatus.FAILED, error=str(e))
    
    async def generate_social_media(self, request_data: Dict[str, Any]) -> str:
        task_id = self.task_service.create_task()
        asyncio.create_task(self._process_social_media(task_id, request_data))
        return task_id
    
    async def _process_social_media(self, task_id: str, request_data: Dict[str, Any]):
        try:
            self.task_service.update_task(task_id, TaskStatus.PROCESSING)
            prompts = request_data["prompts"]
            
            platforms = ["Facebook", "Instagram", "Twitter", "LinkedIn"]
            posts = []
            
            for platform in platforms:
                post_content = await self.ai_service.generate_text(
                    f"Create 3 engaging {platform} posts for {prompts['business_name']}. Include captions and relevant hashtags.",
                    {**prompts, "platform": platform}
                )
                posts.append({
                    "platform": platform,
                    "content": post_content
                })
            
            banners = []
            if self.ai_service.can_generate_images():
                try:
                    for platform in platforms:
                        banner_desc = f"Professional social media banner for {prompts['business_name']} on {platform}. Business in {prompts['industry']} industry."
                        banner = await self.ai_service.generate_image(banner_desc)
                        banners.append({
                            "platform": platform,
                            "banner": banner
                        })
                except Exception as e:
                    print(f"Banner generation skipped: {e}")
            
            result = {
                "posts": posts,
                "banners": banners,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            self.task_service.update_task(task_id, TaskStatus.COMPLETED, result)
            
        except Exception as e:
            self.task_service.update_task(task_id, TaskStatus.FAILED, error=str(e))
    
    async def generate_website_content(self, request_data: Dict[str, Any]) -> str:
        task_id = self.task_service.create_task()
        asyncio.create_task(self._process_website_content(task_id, request_data))
        return task_id
    
    async def _process_website_content(self, task_id: str, request_data: Dict[str, Any]):
        try:
            self.task_service.update_task(task_id, TaskStatus.PROCESSING)
            prompts = request_data["prompts"]
            
            sections = ["hero", "about", "services", "testimonials", "contact"]
            website_content = {}
            
            for section in sections:
                section_content = await self.ai_service.generate_text(
                    f"Create engaging {section} section content for a business website. Include headline, subheadline, and body content.",
                    {**prompts, "section": section}
                )
                website_content[section] = section_content
            
            result = {
                "website_content": website_content,
                "template_suggestions": ["modern", "professional", "minimalist", "corporate"],
                "generated_at": datetime.utcnow().isoformat()
            }
            
            self.task_service.update_task(task_id, TaskStatus.COMPLETED, result)
            
        except Exception as e:
            self.task_service.update_task(task_id, TaskStatus.FAILED, error=str(e))
    
    async def generate_business_plan(self, request_data: Dict[str, Any]) -> str:
        task_id = self.task_service.create_task()
        asyncio.create_task(self._process_business_plan(task_id, request_data))
        return task_id
    
    async def _process_business_plan(self, task_id: str, request_data: Dict[str, Any]):
        try:
            self.task_service.update_task(task_id, TaskStatus.PROCESSING)
            prompts = request_data["prompts"]
            
            business_plan = await self.ai_service.generate_text(
                "Create a comprehensive business plan including executive summary, market analysis, marketing strategy, operational plan, and financial projections.",
                prompts
            )
            
            result = {
                "business_plan": business_plan,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            self.task_service.update_task(task_id, TaskStatus.COMPLETED, result)
            
        except Exception as e:
            self.task_service.update_task(task_id, TaskStatus.FAILED, error=str(e))
