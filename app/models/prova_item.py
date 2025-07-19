from .base import MongoBaseModel

class ProvaItem(MongoBaseModel):
    codigo_item: str
    area_conhecimento: str
    acerto: bool