"""Schemas para operações com resultados"""

from typing import Optional
from pydantic import BaseModel


class ResultadoCreate(BaseModel):
    """Schema para criação de resultado"""
    nu_sequencial: str
    nu_ano: int
    participante_inscricao: str
    escola_codigo: Optional[int] = None
    municipio_escola_codigo: Optional[int] = None
    municipio_escola_nome: Optional[str] = None
    uf_escola_codigo: Optional[int] = None
    uf_escola_sigla: Optional[str] = None
    municipio_prova_codigo: int
    municipio_prova_nome: str
    uf_prova_codigo: int
    uf_prova_sigla: str
    presenca_cn: Optional[int] = None
    presenca_ch: Optional[int] = None
    presenca_lc: Optional[int] = None
    presenca_mt: Optional[int] = None
    nota_cn: Optional[float] = None
    nota_ch: Optional[float] = None
    nota_lc: Optional[float] = None
    nota_mt: Optional[float] = None
    nota_redacao: Optional[float] = None
