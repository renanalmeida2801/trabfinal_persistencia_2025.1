from typing import Optional
from pydantic import Field

from .base import MongoBaseModel, PyObjectId


class Escola(MongoBaseModel):
    codigo: int = Field(..., description="Código da escola")
    nome: Optional[str] = Field(None, description="Nome da escola")
    municipio_codigo: int = Field(..., description="Código do município da escola")
    municipio_id: Optional[PyObjectId] = Field(None, description="Referência ao município")
    uf_codigo: int = Field(..., description="Código da UF da escola")
    uf_sigla: str = Field(..., description="Sigla da UF da escola")
    dependencia_administrativa: int = Field(..., description="Tipo de dependência administrativa")
    localizacao: int = Field(..., description="Localização da escola (urbana/rural)")
    situacao_funcionamento: int = Field(..., description="Situação de funcionamento")
    total_participantes: Optional[int] = Field(0, description="Total de participantes da escola")

    class Config:
        collection = "escolas"
