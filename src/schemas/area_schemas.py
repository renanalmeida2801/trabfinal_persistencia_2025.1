from typing import Optional
from pydantic import BaseModel, Field


class AreaConhecimentoBase(BaseModel):
    """Schema base para área de conhecimento"""

    codigo: str = Field(..., description="Código único da área")
    nome: str = Field(..., description="Nome da área de conhecimento")
    descricao: Optional[str] = Field(None, description="Descrição da área")
    sigla: str = Field(..., description="Sigla da área")
    peso_default: float = Field(1.0, description="Peso padrão da área")
    ativa: bool = Field(True, description="Se a área está ativa")


class AreaConhecimentoCreate(AreaConhecimentoBase):
    """Schema para criação de área de conhecimento"""

    pass


class AreaConhecimentoUpdate(BaseModel):
    """Schema para atualização de área de conhecimento"""

    nome: Optional[str] = Field(None, description="Nome da área de conhecimento")
    descricao: Optional[str] = Field(None, description="Descrição da área")
    sigla: Optional[str] = Field(None, description="Sigla da área")
    peso_default: Optional[float] = Field(None, description="Peso padrão da área")
    ativa: Optional[bool] = Field(None, description="Se a área está ativa")


class AreaConhecimentoSimples(AreaConhecimentoBase):
    """Schema simplificado para retorno de área"""

    id: Optional[str] = Field(None, alias="_id")

    class Config:
        populate_by_name = True


class AreaConhecimentoOperationResponse(BaseModel):
    """Schema para resposta de operações"""

    success: bool
    message: str
    area_id: str
