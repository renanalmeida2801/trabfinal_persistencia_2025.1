"""Schemas para operações com municípios"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MunicipioCreate(BaseModel):
    """Schema para criação de município"""
    codigo: int
    nome: str
    uf_codigo: int
    uf_sigla: str
    regiao: Optional[str] = None
    populacao: Optional[int] = None
    pib_per_capita: Optional[float] = None
    idh: Optional[float] = None


class MunicipioUpdate(BaseModel):
    """Schema para atualização de município"""
    nome: Optional[str] = None
    regiao: Optional[str] = None
    populacao: Optional[int] = None
    pib_per_capita: Optional[float] = None
    idh: Optional[float] = None


class MunicipioResponse(BaseModel):
    """Schema para resposta de município"""
    id: str
    codigo: int
    nome: str
    uf_codigo: int
    uf_sigla: str
    regiao: Optional[str]
    populacao: Optional[int]
    pib_per_capita: Optional[float]
    idh: Optional[float]

    class Config:
        from_attributes = True


# ==================== RESPONSE SCHEMAS ====================

class MunicipioDetalhado(BaseModel):
    """Detalhes completos de um município"""
    codigo: int = Field(..., description="Código do município")
    nome: str = Field(..., description="Nome do município")
    uf_codigo: int = Field(..., description="Código da UF")
    uf_sigla: str = Field(..., description="Sigla da UF")
    uf_nome: Optional[str] = Field(None, description="Nome da UF")
    regiao: Optional[str] = Field(None, description="Região geográfica")
    populacao: Optional[int] = Field(None, description="População estimada")
    pib_per_capita: Optional[float] = Field(None, description="PIB per capita")
    idh: Optional[float] = Field(None, description="Índice de Desenvolvimento Humano")
    densidade_demografica: Optional[float] = Field(None, description="Densidade demográfica")
    id: Optional[str] = Field(None, description="ID do documento", alias="_id")
    
    class Config:
        populate_by_name = True


class MunicipioSimples(BaseModel):
    """Resposta simples para município por ID ou código"""
    codigo: Optional[int] = Field(None, description="Código do município")
    nome: Optional[str] = Field(None, description="Nome do município")
    uf_codigo: Optional[int] = Field(None, description="Código da UF")
    uf_sigla: Optional[str] = Field(None, description="Sigla da UF")
    regiao: Optional[str] = Field(None, description="Região")
    populacao: Optional[int] = Field(None, description="População")
    pib_per_capita: Optional[float] = Field(None, description="PIB per capita")
    idh: Optional[float] = Field(None, description="IDH")
    id: Optional[str] = Field(None, description="ID do documento", alias="_id")
    
    class Config:
        populate_by_name = True


class MunicipioPaginadoResponse(BaseModel):
    """Resposta paginada para listagem de municípios"""
    items: List[Dict[str, Any]] = Field(..., description="Lista de municípios")
    total: int = Field(..., description="Total de registros")
    skip: int = Field(..., description="Registros pulados")
    limit: int = Field(..., description="Limite por página")
    has_more: bool = Field(..., description="Se há mais registros")
    current_page: int = Field(..., description="Página atual")
    total_pages: int = Field(..., description="Total de páginas")
    filtros_aplicados: Optional[Dict[str, Any]] = Field(None, description="Filtros aplicados")


class MunicipioOperationResponse(BaseModel):
    """Resposta para operações de CRUD"""
    success: bool = Field(..., description="Se a operação foi bem-sucedida")
    message: Optional[str] = Field(None, description="Mensagem da operação")
    municipio_id: Optional[str] = Field(None, description="ID do município afetado")


class EstatisticaRegiao(BaseModel):
    """Estatística por região geográfica"""
    regiao: str = Field(..., description="Nome da região")
    total_municipios: int = Field(..., description="Total de municípios na região")
    percentual: float = Field(..., description="Percentual do total")
    populacao_total: Optional[int] = Field(None, description="População total da região")
    populacao_media: Optional[float] = Field(None, description="População média por município")
    pib_per_capita_medio: Optional[float] = Field(None, description="PIB per capita médio")
    idh_medio: Optional[float] = Field(None, description="IDH médio da região")
    maior_municipio: Optional[str] = Field(None, description="Nome do maior município")
    menor_municipio: Optional[str] = Field(None, description="Nome do menor município")


class ResumoGeralMunicipios(BaseModel):
    """Resumo geral dos municípios"""
    total_municipios: int = Field(..., description="Total de municípios")
    total_populacao: Optional[int] = Field(None, description="População total")
    municipios_por_uf: Dict[str, int] = Field(..., description="Contagem por UF")
    regiao_com_mais_municipios: Optional[str] = Field(None, description="Região predominante")


class EstatisticasRegiaoResponse(BaseModel):
    """Resposta das estatísticas por região"""
    estatisticas_por_regiao: List[EstatisticaRegiao] = Field(..., description="Estatísticas por região")
    resumo_geral: ResumoGeralMunicipios = Field(..., description="Resumo geral")
    total_regioes: int = Field(..., description="Total de regiões")
