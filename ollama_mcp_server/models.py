"""Pydantic models for Ollama API requests and responses"""
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class Message(BaseModel):
    """Chat message"""
    role: str = Field(..., description="Message role (system, user, assistant)")
    content: str = Field(..., description="Message content")
    
    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        valid_roles = ["system", "user", "assistant"]
        if v not in valid_roles:
            raise ValueError(f"Role must be one of: {', '.join(valid_roles)}")
        return v


class GenerateOptions(BaseModel):
    """Generation options for Ollama API"""
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(None, ge=1)
    seed: Optional[int] = Field(None)
    num_predict: Optional[int] = Field(None, ge=-1)
    stop: Optional[List[str]] = Field(None)
    
    class Config:
        extra = "allow"  # Allow additional options


class ModelInfo(BaseModel):
    """Model information"""
    name: str
    modified_at: Optional[datetime] = None
    size: Optional[int] = None
    digest: Optional[str] = None
    
    @field_validator("modified_at", mode="before")
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class ModelDetails(BaseModel):
    """Detailed model information"""
    modelfile: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    template: Optional[str] = None
    license: Optional[str] = None


class GenerateRequest(BaseModel):
    """Generate completion request"""
    model: str
    prompt: str
    stream: bool = False
    options: Optional[GenerateOptions] = None


class ChatRequest(BaseModel):
    """Chat completion request"""
    model: str
    messages: List[Message]
    stream: bool = False
    options: Optional[GenerateOptions] = None


class EmbeddingsRequest(BaseModel):
    """Embeddings request"""
    model: str
    prompt: Union[str, List[str]]


class GenerateResponse(BaseModel):
    """Generate completion response"""
    model: str
    created_at: datetime
    response: str
    done: bool
    context: Optional[List[int]] = None
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None
    
    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class ChatResponse(BaseModel):
    """Chat completion response"""
    model: str
    created_at: datetime
    message: Message
    done: bool
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None
    
    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class EmbeddingsResponse(BaseModel):
    """Embeddings response"""
    model: Optional[str] = None
    embedding: Optional[List[float]] = None
    embeddings: Optional[List[List[float]]] = None
    
    def get_embeddings(self) -> List[List[float]]:
        """Get embeddings in standardized format"""
        if self.embeddings is not None:
            return self.embeddings
        elif self.embedding is not None:
            return [self.embedding]
        else:
            return []


class ModelListResponse(BaseModel):
    """Model list response"""
    models: List[ModelInfo]


class ProcessModel(BaseModel):
    """Running model information"""
    name: str
    model: str
    size: int
    digest: str
    expires_at: datetime
    
    @field_validator("expires_at", mode="before")
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class ProcessListResponse(BaseModel):
    """Process list response"""
    models: List[ProcessModel]


class ErrorResponse(BaseModel):
    """Error response from Ollama API"""
    error: str
    details: Optional[Dict[str, Any]] = None