from .base import MongoBaseModel
from typing import Optional

class Escola(MongoBaseModel):
    codigo: int
    nome: Optional[str]
    rede: Optional[str]
    municipio_codigo: int  # FK para Municipio