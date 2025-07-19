from .base import MongoBaseModel
from typing import Optional
from .questionario import QuestionarioSocioeconomico

class Participante(MongoBaseModel):
    nu_inscricao: str
    nu_ano: int
    faixa_etaria: int
    sexo: str
    estado_civil: int
    cor_raca: int
    nacionalidade: int
    st_conclusao: int
    ano_concluiu: Optional[int]
    ensino: Optional[int]
    treineiro: bool
    municipio_prova: int
    uf_prova: str
    questionario: QuestionarioSocioeconomico