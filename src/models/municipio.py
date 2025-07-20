from typing import Optional

from pydantic import Field

from .base import MongoBaseModel


class Municipio(MongoBaseModel):
    codigo: int = Field(..., description="Código do município")
    nome: str = Field(..., description="Nome do município")
    uf_codigo: int = Field(..., description="Código da UF")
    uf_sigla: str = Field(..., description="Sigla da UF")
    regiao: Optional[str] = Field(None, description="Região do país")
    populacao: Optional[int] = Field(None, description="População estimada")
    pib_per_capita: Optional[float] = Field(None, description="PIB per capita")
    idh: Optional[float] = Field(None, description="Índice de Desenvolvimento Humano")

    class Config:
        collection = "municipios"
