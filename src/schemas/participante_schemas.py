"""Schemas para operações com participantes"""

from pydantic import BaseModel


class ParticipanteResponse(BaseModel):
    """Schema para resposta de participante"""
    id: str
    nu_inscricao: str
    nu_ano: int
    faixa_etaria: int
    sexo: str
    estado_civil: int
    cor_raca: int
    treineiro: bool
    uf_prova: str

    class Config:
        from_attributes = True
