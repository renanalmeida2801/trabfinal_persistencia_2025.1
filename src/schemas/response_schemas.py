"""Schemas genéricos de resposta para toda a API"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class MetadodosPaginacao(BaseModel):
    """Metadados de paginação genéricos"""
    total: int = Field(..., description="Total de registros")
    skip: int = Field(..., description="Registros pulados")
    limit: int = Field(..., description="Limite por página")
    has_more: bool = Field(..., description="Se há mais registros")
    current_page: int = Field(..., description="Página atual")
    total_pages: int = Field(..., description="Total de páginas")


class PaginatedResponse(BaseModel):
    """Resposta paginada genérica"""
    items: List[Dict[str, Any]] = Field(..., description="Lista de itens")
    total: int = Field(..., description="Total de registros")
    skip: int = Field(..., description="Registros pulados")
    limit: int = Field(..., description="Limite por página")
    has_more: bool = Field(..., description="Se há mais registros")
    current_page: int = Field(..., description="Página atual")
    total_pages: int = Field(..., description="Total de páginas")


class APIResponse(BaseModel):
    """Resposta padrão da API"""
    success: bool = Field(..., description="Se a operação foi bem-sucedida")
    message: str = Field(..., description="Mensagem de resposta")
    data: Dict[str, Any] = Field(..., description="Dados da resposta")


class ErrorResponse(BaseModel):
    """Resposta de erro padrão"""
    error: bool = Field(True, description="Indica que houve erro")
    message: str = Field(..., description="Mensagem de erro")
    details: Dict[str, Any] = Field({}, description="Detalhes adicionais do erro")
