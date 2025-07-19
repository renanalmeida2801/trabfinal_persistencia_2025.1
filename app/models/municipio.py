from .base import MongoBaseModel

class Municipio(MongoBaseModel):
    codigo: int
    nome: str
    uf: str