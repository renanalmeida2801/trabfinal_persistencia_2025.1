"""Schemas para operações com municípios"""

from typing import Optional
from pydantic import BaseModel


class MunicipioCreate(BaseModel):
    """Schema para criação de município"""
    codigo: int
    nome: str
    uf_codigo: int
    uf_sigla: str
    regiao: Optional[str] = None
    populacao: Optional[int] = None
    pib_per_capita: Optional[float] = None
    idh: Optional[float] = None


class MunicipioUpdate(BaseModel):
    """Schema para atualização de município"""
    nome: Optional[str] = None
    regiao: Optional[str] = None
    populacao: Optional[int] = None
    pib_per_capita: Optional[float] = None
    idh: Optional[float] = None


class MunicipioResponse(BaseModel):
    """Schema para resposta de município"""
    id: str
    codigo: int
    nome: str
    uf_codigo: int
    uf_sigla: str
    regiao: Optional[str]
    populacao: Optional[int]
    pib_per_capita: Optional[float]
    idh: Optional[float]

    class Config:
        from_attributes = True
