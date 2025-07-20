from typing import Any, Dict, Optional

from pydantic import Field

from .base import MongoBaseModel, PyObjectId


class Participante(MongoBaseModel):
    nu_inscricao: str = Field(..., description="Número de inscrição do participante")
    nu_ano: int = Field(..., description="Ano da prova")
    faixa_etaria: int = Field(..., description="Faixa etária do participante")
    sexo: str = Field(..., description="Sexo do participante (M/F)")
    estado_civil: int = Field(..., description="Estado civil")
    cor_raca: int = Field(..., description="Cor/raça")
    nacionalidade: int = Field(..., description="Nacionalidade")
    st_conclusao: int = Field(..., description="Status de conclusão do ensino médio")
    ano_concluiu: Optional[int] = Field(
        None, description="Ano que concluiu o ensino médio"
    )
    ensino: Optional[int] = Field(None, description="Tipo de ensino médio")
    treineiro: bool = Field(False, description="Se é treineiro")

    municipio_prova_codigo: int = Field(..., description="Código do município da prova")
    municipio_prova_id: Optional[PyObjectId] = Field(
        None, description="Referência ao município da prova"
    )
    uf_prova: str = Field(..., description="UF onde fez a prova")

    questionario: Optional[Dict[str, Any]] = Field(
        None, description="Respostas do questionário socioeconômico"
    )

    total_provas_realizadas: Optional[int] = Field(
        0, description="Total de provas que o participante realizou"
    )

    class Config:
        collection = "participantes"
