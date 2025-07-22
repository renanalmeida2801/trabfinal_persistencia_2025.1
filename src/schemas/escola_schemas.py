"""Schemas para operações com escolas"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EscolaCreate(BaseModel):
    """Schema para criação de escola"""
    codigo: int
    nome: Optional[str] = None
    municipio_codigo: int
    uf_codigo: int
    uf_sigla: str
    dependencia_administrativa: int
    localizacao: int
    situacao_funcionamento: int


class EscolaResponse(BaseModel):
    """Schema para resposta de escola"""
    id: str
    codigo: int
    nome: Optional[str]
    municipio_codigo: int
    uf_sigla: str
    dependencia_administrativa: int
    localizacao: int
    situacao_funcionamento: int

    class Config:
        from_attributes = True


# ==================== RESPONSE SCHEMAS ====================

class EscolaDetalhada(BaseModel):
    """Detalhes completos de uma escola"""
    codigo: int = Field(..., description="Código da escola")
    nome: Optional[str] = Field(None, description="Nome da escola")
    municipio_codigo: int = Field(..., description="Código do município")
    municipio_nome: Optional[str] = Field(None, description="Nome do município")
    uf_codigo: int = Field(..., description="Código da UF")
    uf_sigla: str = Field(..., description="Sigla da UF")
    uf_nome: Optional[str] = Field(None, description="Nome da UF")
    dependencia_administrativa: int = Field(..., description="Código da dependência administrativa")
    dependencia_administrativa_descricao: Optional[str] = Field(None, description="Descrição da dependência")
    localizacao: int = Field(..., description="Código da localização")
    localizacao_descricao: Optional[str] = Field(None, description="Descrição da localização")
    situacao_funcionamento: int = Field(..., description="Código da situação de funcionamento")
    situacao_funcionamento_descricao: Optional[str] = Field(None, description="Descrição da situação")
    id: Optional[str] = Field(None, description="ID do documento", alias="_id")
    
    class Config:
        populate_by_name = True


class EscolaSimples(BaseModel):
    """Resposta simples para escola por ID ou código"""
    codigo: Optional[int] = Field(None, description="Código da escola")
    nome: Optional[str] = Field(None, description="Nome da escola")
    municipio_codigo: Optional[int] = Field(None, description="Código do município")
    uf_sigla: Optional[str] = Field(None, description="Sigla da UF")
    dependencia_administrativa: Optional[int] = Field(None, description="Dependência administrativa")
    localizacao: Optional[int] = Field(None, description="Localização")
    situacao_funcionamento: Optional[int] = Field(None, description="Situação de funcionamento")
    id: Optional[str] = Field(None, description="ID do documento", alias="_id")
    
    class Config:
        populate_by_name = True


class EscolaPaginadaResponse(BaseModel):
    """Resposta paginada para listagem de escolas"""
    items: List[Dict[str, Any]] = Field(..., description="Lista de escolas")
    total: int = Field(..., description="Total de registros")
    skip: int = Field(..., description="Registros pulados")
    limit: int = Field(..., description="Limite por página")
    has_more: bool = Field(..., description="Se há mais registros")
    current_page: int = Field(..., description="Página atual")
    total_pages: int = Field(..., description="Total de páginas")


class EstatisticaDependencia(BaseModel):
    """Estatística por dependência administrativa"""
    dependencia_administrativa: int = Field(..., description="Código da dependência")
    dependencia_descricao: str = Field(..., description="Descrição da dependência")
    total_escolas: int = Field(..., description="Total de escolas")
    percentual: float = Field(..., description="Percentual do total")
    distribuicao_por_uf: Optional[List[Dict[str, Any]]] = Field(None, description="Distribuição por UF")


class EscolasPorDependenciaResponse(BaseModel):
    """Resposta das escolas por dependência administrativa"""
    estatisticas: List[EstatisticaDependencia] = Field(..., description="Estatísticas por dependência")
    total_escolas: int = Field(..., description="Total geral de escolas")
    uf_filtrada: Optional[str] = Field(None, description="UF filtrada (se aplicável)")
    resumo: Dict[str, Any] = Field(..., description="Resumo das estatísticas")


class EscolaRanking(BaseModel):
    """Item do ranking de escolas"""
    posicao: int = Field(..., description="Posição no ranking")
    escola_codigo: int = Field(..., description="Código da escola")
    escola_nome: Optional[str] = Field(None, description="Nome da escola")
    municipio_nome: Optional[str] = Field(None, description="Nome do município")
    uf_sigla: str = Field(..., description="Sigla da UF")
    dependencia_administrativa_descricao: Optional[str] = Field(None, description="Dependência administrativa")
    total_participantes: int = Field(..., description="Total de participantes da escola")
    media_geral: float = Field(..., description="Média geral das provas")
    media_objetivas: float = Field(..., description="Média das provas objetivas")
    media_redacao: Optional[float] = Field(None, description="Média da redação")
    desvio_padrao: Optional[float] = Field(None, description="Desvio padrão das notas")


class RankingEscolasResponse(BaseModel):
    """Resposta do ranking de escolas por desempenho"""
    ranking: List[EscolaRanking] = Field(..., description="Lista do ranking das escolas")
    total_escolas_ranking: int = Field(..., description="Total de escolas no ranking")
    criterio_ordenacao: str = Field(..., description="Critério de ordenação utilizado")
    limite_ranking: int = Field(..., description="Limite de escolas no ranking")
    estatisticas_gerais: Dict[str, Any] = Field(..., description="Estatísticas gerais do ranking")
    melhor_escola: Optional[EscolaRanking] = Field(None, description="Escola com melhor desempenho")
