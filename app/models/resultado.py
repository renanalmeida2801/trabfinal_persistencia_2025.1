from .base import MongoBaseModel
from typing import List
from .prova_item import ProvaItem

class Resultado(MongoBaseModel):
    nu_inscricao: str           # FK para Participante
    escola_codigo: int          # FK para Escola
    nota_cn: float
    nota_ch: float
    nota_lc: float
    nota_mt: float
    nota_redacao: float
    itens_prova: List[ProvaItem]  # Embutido