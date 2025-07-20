"""Schemas de requisição e resposta da API"""

from .municipio_schemas import MunicipioCreate, MunicipioResponse, MunicipioUpdate
from .escola_schemas import EscolaCreate, EscolaResponse
from .participante_schemas import ParticipanteResponse
from .resultado_schemas import ResultadoCreate

__all__ = [
    "MunicipioCreate",
    "MunicipioUpdate", 
    "MunicipioResponse",
    "EscolaCreate",
    "EscolaResponse",
    "ParticipanteResponse",
    "ResultadoCreate",
]
