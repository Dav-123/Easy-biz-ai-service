import magic
import os
import tempfile
from typing import Dict, Any, Optional, List
from fastapi import UploadFile, HTTPException, status
import PyPDF2
import docx
import io
from PIL import Image
import base64

class FileProcessor:
    SUPPORTED_MIME_TYPES = {
        'application/pdf': 'pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
        'text/plain': 'txt',
        'image/jpeg': 'image',
        'image/png': 'image',
        'image/webp': 'image'
    }
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @classmethod
    async def validate_and_process_file(cls, file: UploadFile) -> Dict[str, Any]:
        """
        Validate file type and size, then process based on file type.
        """
        # Check file size
        content = await file.read()
        if len(content) > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds {cls.MAX_FILE_SIZE // 1024 // 1024}MB limit"
            )
        
        # Validate file type
        mime_type = magic.from_buffer(content, mime=True)
        file_extension = cls.SUPPORTED_MIME_TYPES.get(mime_type)
        
        if not file_extension:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type: {mime_type}"
            )
        
        # Reset file pointer
        await file.seek(0)
        
        # Process file based on type
        if mime_type.startswith('image/'):
            return await cls._process_image_file(content, file_extension)
        else:
            return await cls._process_document_file(content, file_extension, mime_type)
    
    @staticmethod
    async def _process_document_file(content: bytes, extension: str, mime_type: str) -> Dict[str, Any]:
        """
        Process document files and extract text content.
        """
        try:
            text_content = ""
            
            if mime_type == 'application/pdf':
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
            
            elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                doc = docx.Document(io.BytesIO(content))
                for paragraph in doc.paragraphs:
                    text_content += paragraph.text + "\n"
            
            elif mime_type == 'text/plain':
                text_content = content.decode('utf-8')
            
            return {
                "type": "document",
                "extension": extension,
                "content": text_content.strip(),
                "size": len(content),
                "word_count": len(text_content.split())
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to process document: {str(e)}"
            )
    
    @staticmethod
    async def _process_image_file(content: bytes, extension: str) -> Dict[str, Any]:
        """
        Process image files and extract metadata.
        """
        try:
            with Image.open(io.BytesIO(content)) as img:
                return {
                    "type": "image",
                    "extension": extension,
                    "format": img.format,
                    "size": len(content),
                    "dimensions": {
                        "width": img.width,
                        "height": img.height
                    },
                    "mode": img.mode,
                    "base64_preview": cls._create_image_preview(content)
                }
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to process image: {str(e)}"
            )
    
    @staticmethod
    def _create_image_preview(image_data: bytes, max_size: tuple = (200, 200)) -> str:
        """
        Create a base64 encoded preview of the image.
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=85)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return f"data:image/jpeg;base64,{img_str}"
        except Exception:
            return ""

def validate_file_type(file: UploadFile, allowed_types: List[str]) -> bool:
    """
    Validate if file type is in allowed types.
    """
    mime_type = magic.from_buffer(file.file.read(1024), mime=True)
    file.file.seek(0)  # Reset file pointer
    
    return mime_type in allowed_types

async def extract_text_from_file(file: UploadFile) -> str:
    """
    Extract text content from various file types.
    """
    processor = FileProcessor()
    result = await processor.validate_and_process_file(file)
    
    if result["type"] == "document":
        return result["content"]
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text extraction only supported for document files"
        )

async def compress_image(image_data: bytes, quality: int = 85, max_dimension: int = 1200) -> bytes:
    """
    Compress image while maintaining quality.
    """
    try:
        image = Image.open(io.BytesIO(image_data))
        
        # Calculate new dimensions maintaining aspect ratio
        if image.width > max_dimension or image.height > max_dimension:
            ratio = min(max_dimension / image.width, max_dimension / image.height)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        # Save compressed image
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=quality, optimize=True)
        
        return output.getvalue()
        
    except Exception as e:
        raise Exception(f"Image compression failed: {str(e)}")

def get_file_metadata(file_path: str) -> Dict[str, Any]:
    """
    Get comprehensive metadata for a file.
    """
    try:
        file_stats = os.stat(file_path)
        mime_type = magic.from_file(file_path, mime=True)
        
        return {
            "file_name": os.path.basename(file_path),
            "file_size": file_stats.st_size,
            "file_type": mime_type,
            "created_time": file_stats.st_ctime,
            "modified_time": file_stats.st_mtime,
            "extension": os.path.splitext(file_path)[1].lower()
        }
    except Exception as e:
        raise Exception(f"Failed to get file metadata: {str(e)}")