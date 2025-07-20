from typing import List, Optional

from pydantic import Field

from .base import MongoBaseModel


class ProvaItem(MongoBaseModel):
    codigo_prova: str = Field(..., description="Código identificador da prova")
    area: str = Field(..., description="Área do conhecimento (CN, CH, LC, MT)")
    ano: int = Field(..., description="Ano da prova")
    numero_questoes: int = Field(..., description="Número total de questões")
    gabarito: str = Field(..., description="Gabarito da prova")
    questoes: Optional[List[str]] = Field(None, description="Lista das questões")

    # Estatísticas da prova
    media_geral: Optional[float] = Field(None, description="Média geral da prova")
    desvio_padrao: Optional[float] = Field(None, description="Desvio padrão")
    numero_participantes: Optional[int] = Field(
        0, description="Número de participantes"
    )

    class Config:
        collection = "provas_itens"
