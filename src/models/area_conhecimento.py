from typing import Optional
from pydantic import Field
from models.base import MongoBaseModel


class AreaConhecimento(MongoBaseModel):
    """Modelo para área de conhecimento do ENEM"""

    codigo: str = Field(..., description="Código único da área (CN, CH, LC, MT, RE)")
    nome: str = Field(..., description="Nome completo da área de conhecimento")
    descricao: Optional[str] = Field(None, description="Descrição detalhada da área")
    sigla: str = Field(..., description="Sigla da área de conhecimento")
    peso_default: float = Field(
        1.0, description="Peso padrão para cálculos", ge=0.1, le=10.0
    )
    ativa: bool = Field(True, description="Indica se a área está ativa no sistema")

    class Config:
        json_schema_extra = {
            "example": {
                "codigo": "CN",
                "nome": "Ciências da Natureza e suas Tecnologias",
                "descricao": "Área que engloba Física, Química e Biologia",
                "sigla": "CN",
                "peso_default": 1.0,
                "ativa": True,
            }
        }
