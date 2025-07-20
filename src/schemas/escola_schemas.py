"""Schemas para operações com escolas"""

from typing import Optional
from pydantic import BaseModel


class EscolaCreate(BaseModel):
    """Schema para criação de escola"""
    codigo: int
    nome: Optional[str] = None
    municipio_codigo: int
    uf_codigo: int
    uf_sigla: str
    dependencia_administrativa: int
    localizacao: int
    situacao_funcionamento: int


class EscolaResponse(BaseModel):
    """Schema para resposta de escola"""
    id: str
    codigo: int
    nome: Optional[str]
    municipio_codigo: int
    uf_sigla: str
    dependencia_administrativa: int
    localizacao: int
    situacao_funcionamento: int

    class Config:
        from_attributes = True
