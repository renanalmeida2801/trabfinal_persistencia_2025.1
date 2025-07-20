# API ENEM - Dados Abertos

Sistema de API RESTful para exploração e manipulação de dados do ENEM (Exame Nacional do Ensino Médio) utilizando FastAPI e MongoDB.

## 📋 Descrição do Projeto

Este projeto foi desenvolvido como Trabalho Prático Final da disciplina de Persistência de Dados, tendo como objetivo integrar conhecimentos de:

- **Coleta e Preparação de Dados**: Dados do ENEM obtidos através do Portal Brasileiro de Dados Abertos
- **Persistência de Dados**: Modelagem utilizando MongoDB com relacionamentos apropriados
- **Desenvolvimento de API**: API RESTful completa com FastAPI
- **Consultas Avançadas**: Queries complexas, filtros dinâmicos e paginação
- **Boas Práticas**: Tratamento de erros, logging e documentação automática

## 🏗️ Arquitetura de Software

### Padrões de Projeto Implementados

#### 1. **Service Layer Pattern**
- **Localização**: `src/services/`
- **Propósito**: Centralizar lógica de negócio e separar responsabilidades
- **Benefícios**: Reutilização de código, testabilidade e manutenibilidade

#### 2. **Repository Pattern** 
- **Localização**: `src/infra/repositories/`
- **Propósito**: Abstrair operações de acesso a dados
- **Benefícios**: Desacoplamento da camada de dados e flexibilidade

#### 3. **Dependency Injection**
- **Implementação**: FastAPI Depends()
- **Propósito**: Inversão de controle e testabilidade
- **Uso**: Controllers → Services → Repositories

### Fluxo de Requisições

```
HTTP Request → Router (Controller) → Service → Repository → MongoDB
                 ↓
HTTP Response ← Schema ← Business Logic ← Data Access ← Database
```

### Tratamento de Erros Robusto

- **Logging com Traceback**: Todos os services implementam logging detalhado
- **Exception Handling**: Try/catch em todas as operações críticas  
- **Structured Logging**: Logs padronizados com contexto e níveis apropriados
- **Error Propagation**: Erros propagados adequadamente entre camadas

### Entidades Principais (5+ entidades com 8+ atributos cada):

1. **Município** - Dados geográficos dos municípios brasileiros
2. **Escola** - Informações das escolas participantes  
3. **Participante** - Dados dos candidatos do ENEM
4. **Resultado** - Desempenho e notas dos participantes
5. **QuestionarioSocioeconomico** - Respostas do questionário socioeconômico

### Relacionamentos Implementados:

- **1:N** - Município → Escolas (um município pode ter várias escolas)
- **1:N** - Participante → Resultado (um participante pode ter vários resultados ao longo dos anos)
- **1:1** - Participante ↔ QuestionarioSocioeconomico (relação de composição)

### Organização em Camadas:

- **Models**: Definições dos modelos de dados MongoDB/Pydantic
- **Schemas**: Schemas de requisição e resposta da API (separados por domínio)
- **Repositories**: Camada de acesso aos dados (padrão Repository)
- **Services**: Lógica de negócio e regras da aplicação (Service Layer Pattern)
- **Routes**: Definição dos endpoints da API REST (Controllers)
- **Config**: Configurações de logging, settings e aplicação

## 🚀 Tecnologias Utilizadas

- **FastAPI** - Framework web moderno para construção de APIs
- **MongoDB** - Banco de dados NoSQL orientado a documentos
- **Motor** - Driver assíncrono para MongoDB
- **PyMongo** - Driver Python para MongoDB
- **Pydantic** - Validação e serialização de dados
- **Pydantic Settings** - Gerenciamento de configurações
- **Pandas** - Manipulação e análise de dados
- **Uvicorn** - Servidor ASGI para desenvolvimento
- **BSON** - Serialização de dados binários JSON-like
- **Python Multipart** - Suporte para formulários multipart

## 📦 Estrutura do Projeto

```
src/
├── config/                     # Configurações da aplicação
│   ├── logs.py                # Configuração de logging
│   └── settings.py            # Configurações gerais
├── infra/                     # Camada de infraestrutura
│   ├── repositories/          # Camada de acesso a dados
│   │   ├── base_repository.py
│   │   ├── escola_repository.py
│   │   ├── municipio_repository.py
│   │   ├── participante_repository.py
│   │   └── resultado_repository.py
│   └── settings/
│       └── database.py        # Configuração do MongoDB
├── models/                    # Modelos de dados (Pydantic/MongoDB)
│   ├── base.py               # Modelos base
│   ├── escola.py
│   ├── municipio.py
│   ├── participante.py
│   ├── prova_item.py
│   ├── questionario.py
│   └── resultado.py
├── routes/                    # Definição das rotas da API
│   ├── escola_router.py      # Rotas para endpoints de escolas
│   ├── municipio_router.py   # Rotas para endpoints de municípios  
│   ├── participante_router.py # Rotas para endpoints de participantes
│   └── resultado_router.py   # Rotas para endpoints de resultados
├── schemas/                   # Schemas de requisição e resposta
│   ├── escola_schemas.py
│   ├── municipio_schemas.py
│   ├── participante_schemas.py
│   ├── resultado_schemas.py
│   └── README.md
├── scripts/                   # Scripts utilitários
│   └── load_data.py          # Script para carregar dados
├── services/                  # Lógica de negócio (Service Layer)
│   ├── escola_service.py     # Lógica de negócio para escolas
│   ├── municipio_service.py  # Lógica de negócio para municípios
│   ├── participante_service.py # Lógica de negócio para participantes
│   └── resultado_service.py  # Lógica de negócio para resultados
├── logs/                     # Arquivos de log
│   └── enem_api.log
└── main.py                   # Aplicação principal FastAPI

data/                         # Dados do ENEM
├── amostra_participantes.csv
├── amostra_resultados.csv
└── carregar_dados.py
```

## ⚙️ Configuração e Instalação

### 1. Pré-requisitos

- Python 3.10+
- MongoDB rodando na porta padrão (27017)

### 2. Instalação das dependências

```bash
# Opção 1: Usando uv (recomendado)
uv sync

# Opção 2: Usando pip tradicional
# Ativar ambiente virtual (se usando)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Instalar dependências
pip install -e .
```

### 3. Configuração do ambiente

```bash
# Copiar arquivo de configuração
cp .env.example .env

# Editar variáveis se necessário
# MONGO_URL=
# DATABASE_NAME=

# As configurações estão definidas em src/config/settings.py
```

### 4. Carregar dados no MongoDB

```bash
# Método 1: Carregamento automático via API (recomendado)
# Definir variável de ambiente para carregar dados na inicialização
export RELOAD_DATA=true
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Método 2: Executar script manualmente
cd src
python scripts/load_data.py
```

### 5. Executar a aplicação

```bash
# Método 1: Iniciar com carregamento automático de dados
export RELOAD_DATA=true
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Método 2: Iniciar sem recarregar dados (padrão)
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Método 3: Usar Python diretamente
cd src
python main.py
```

## 🔗 Endpoints da API

### Documentação Interativa
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Principais Endpoints

#### Municípios
- `GET /municipios/` - Listar municípios com paginação e filtros
- `GET /municipios/{id}` - Obter município por ID
- `GET /municipios/codigo/{codigo}` - Obter município por código
- `POST /municipios/` - Criar novo município
- `PUT /municipios/{id}` - Atualizar município
- `DELETE /municipios/{id}` - Deletar município
- `GET /municipios/estatisticas/regiao` - Estatísticas por região

#### Escolas
- `GET /escolas/` - Listar escolas com paginação e filtros
- `GET /escolas/{id}` - Obter escola por ID
- `GET /escolas/codigo/{codigo}` - Obter escola por código
- `POST /escolas/` - Criar nova escola
- `PUT /escolas/{id}` - Atualizar escola
- `DELETE /escolas/{id}` - Deletar escola
- `GET /escolas/estatisticas/por-dependencia` - Distribuição por dependência administrativa
- `GET /escolas/estatisticas/ranking-desempenho` - Ranking por desempenho médio
- `GET /escolas/search` - Buscar escolas por nome

#### Participantes
- `GET /participantes/` - Listar participantes com paginação e filtros avançados
- `GET /participantes/{id}` - Obter participante por ID
- `GET /participantes/inscricao/{nu_inscricao}` - Obter participante por número de inscrição
- `POST /participantes/` - Criar novo participante
- `PUT /participantes/{id}` - Atualizar participante
- `DELETE /participantes/{id}` - Deletar participante
- `GET /participantes/estatisticas/demograficas` - Estatísticas demográficas completas
- `GET /participantes/estatisticas/por-uf` - Distribuição por UF
- `GET /participantes/estatisticas/distribuicao-idade` - Distribuição por faixa etária
- `GET /participantes/escola/{codigo}` - Participantes de uma escola específica

#### Resultados  
- `GET /resultados/` - Listar resultados com paginação e filtros
- `GET /resultados/{id}` - Obter resultado por ID
- `GET /resultados/participante/{inscricao}` - Resultado por participante
- `POST /resultados/` - Criar novo resultado
- `GET /resultados/estatisticas/medias-gerais` - Médias gerais do ENEM
- `GET /resultados/estatisticas/ranking-uf` - Ranking das UFs
- `GET /resultados/estatisticas/participantes-destaque` - Participantes destaque
- `GET /resultados/estatisticas/distribuicao-redacao` - Distribuição notas redação
- `GET /resultados/estatisticas/periodo` - Estatísticas por período

## 🔍 Funcionalidades Avançadas

### Paginação
Todos os endpoints de listagem suportam paginação:
```
GET /municipios/?skip=0&limit=100
```

### Filtros Dinâmicos
Múltiplos filtros podem ser combinados:
```
GET /municipios/?uf_sigla=SP&regiao=Sudeste
GET /resultados/?ano=2024&uf_prova_sigla=RJ
```

### Consultas por Intervalo de Datas
```
GET /resultados/estatisticas/periodo?data_inicio=2024-01-01&data_fim=2024-12-31
```

### Agregações e Estatísticas
- Médias por área de conhecimento
- Ranking de UFs por desempenho
- Distribuição de notas por faixas
- Estatísticas socioeconômicas

## 🎯 Exemplos de Uso

### Obter ranking das UFs por média das notas
```bash
curl -X GET "http://localhost:8000/resultados/estatisticas/ranking-uf"
```

### Buscar participantes com nota acima de 800
```bash
curl -X GET "http://localhost:8000/resultados/estatisticas/participantes-destaque?nota_corte=800"
```

### Listar municípios de São Paulo com paginação
```bash
curl -X GET "http://localhost:8000/municipios/?uf_sigla=SP&skip=0&limit=50"
```

### Obter estatísticas de participantes por sexo
```bash
curl -X GET "http://localhost:8000/participantes/estatisticas/sexo"
```

### Listar escolas por dependência administrativa
```bash
curl -X GET "http://localhost:8000/escolas/estatisticas/por-dependencia"
```

### Buscar participantes por escola específica
```bash
curl -X GET "http://localhost:8000/participantes/escola/12345678"
```

### Obter estatísticas demográficas completas
```bash
curl -X GET "http://localhost:8000/participantes/estatisticas/demograficas"
```

## 🧪 Testes

Para testar a API manualmente:

1. Acesse a documentação interativa em http://localhost:8000/docs
2. Teste os endpoints utilizando a interface do Swagger
3. Utilize ferramentas como Postman ou curl para testes automatizados

## 📊 Modelagem de Dados

### Relacionamentos NoSQL

O projeto implementa relacionamentos em MongoDB através de:

- **Referências por ObjectId**: Para relacionamentos que precisam de consistência
- **Embeddocument**: Para dados que sempre são acessados juntos (QuestionarioSocioeconomico)
- **Referências por chaves**: Para relacionamentos lógicos entre entidades

### Índices de Performance

Índices criados automaticamente para otimizar consultas:
- `municipios.codigo`
- `escolas.codigo` 
- `participantes.nu_inscricao`
- `resultados.participante_inscricao`
- `resultados.nu_ano`

## 📋 Schemas e Validação

### Organização dos Schemas

O projeto utiliza uma estrutura organizada de schemas separados por domínio:

- **`schemas/municipio_schemas.py`**: MunicipioCreate, MunicipioUpdate, MunicipioResponse
- **`schemas/escola_schemas.py`**: EscolaCreate, EscolaResponse  
- **`schemas/participante_schemas.py`**: ParticipanteResponse
- **`schemas/resultado_schemas.py`**: ResultadoCreate

### Padrões de Nomenclatura

- **Create**: Schemas para criação de novos recursos
- **Update**: Schemas para atualização de recursos existentes
- **Response**: Schemas para resposta da API (saída)

## 🔧 Services Implementados

### **ResultadoService** (13 métodos)
- ✅ `criar_resultado()` - Criação com cálculo automático de médias
- ✅ `obter_resultado_por_id()` - Busca por ID com logging
- ✅ `obter_resultado_por_participante()` - Busca por inscrição 
- ✅ `listar_resultados()` - Listagem com filtros avançados
- ✅ `obter_media_notas_gerais()` - Agregação de médias por área
- ✅ `obter_ranking_uf()` - Ranking estadual de performance
- ✅ `obter_participantes_destaque()` - Notas acima de corte
- ✅ `obter_distribuicao_redacao()` - Análise de distribuição
- ✅ `obter_estatisticas_por_periodo()` - Analytics temporais

### **MunicipioService** (7 métodos)
- ✅ `criar_municipio()` - Criação com validação geográfica
- ✅ `obter_municipio_por_id()` / `obter_municipio_por_codigo()`
- ✅ `listar_municipios()` - Filtros por UF e região
- ✅ `atualizar_municipio()` / `deletar_municipio()` - CRUD completo
- ✅ `obter_estatisticas_por_regiao()` - Agregações regionais

### **ParticipanteService** (9 métodos)  
- ✅ `criar_participante()` - Validação de dados pessoais
- ✅ `obter_participante_por_id()` / `obter_participante_por_inscricao()`
- ✅ `listar_participantes()` - Filtros demográficos avançados
- ✅ `obter_estatisticas_demograficas()` - Analytics completas
- ✅ `obter_participantes_por_uf()` - Distribuição geográfica
- ✅ `obter_distribuicao_idade()` - Análise etária
- ✅ `obter_participantes_por_escola()` - Filtro institucional
- ✅ `atualizar_participante()` / `excluir_participante()` - CRUD

### **EscolaService** (11 métodos)
- ✅ `criar_escola()` - Validação institucional 
- ✅ `obter_escola_por_id()` / `obter_escola_por_codigo()`
- ✅ `listar_escolas()` - Filtros por localização e dependência
- ✅ `obter_escolas_por_uf()` - Distribuição geográfica
- ✅ `obter_escolas_por_dependencia()` - Análise administrativa
- ✅ `obter_escolas_por_localizacao()` - Urbano vs Rural
- ✅ `obter_ranking_escolas_por_desempenho()` - Top performers
- ✅ `obter_estatisticas_escola()` - Analytics institucionais
- ✅ `buscar_escolas_por_nome()` - Busca textual

## 🔒 Tratamento de Erros e Logging

### Sistema de Logging Avançado

- **Configuração**: `src/config/logs.py` com RotatingFileHandler
- **Localização**: Logs salvos em `src/logs/enem_api.log`
- **Rotação Automática**: Arquivos de 10MB com backup de 5 arquivos
- **Níveis**: INFO, WARNING, ERROR com timestamp e contexto
- **Saídas**: Console (desenvolvimento) + Arquivo (produção)

### Tratamento de Erros por Camada

#### Services (Lógica de Negócio)
- **Traceback completo** em todas as exceções
- **Logging contextual** com parâmetros da operação
- **Propagação controlada** de erros para camada superior

#### API Controllers
- **Validação de entrada**: Pydantic para validação automática
- **Status codes semânticos**: HTTP apropriados (404, 400, 500)
- **Responses padronizadas**: Estrutura consistente de erro

#### Repository (Acesso a Dados)
- **Tratamento de conexão**: Falhas de MongoDB
- **Validação de dados**: Integridade antes de persistir
- **Timeout handling**: Operações com limite de tempo

### Exemplo de Log Estruturado

```
2025-01-20 10:30:15 - INFO - enem_api - Criando participante: 190123456789
2025-01-20 10:30:15 - INFO - enem_api - Participante criado com sucesso: 190123456789
2025-01-20 10:30:20 - ERROR - enem_api - Erro ao buscar escola por código 999999: Escola não encontrada
2025-01-20 10:30:20 - ERROR - enem_api - Traceback (most recent call last):...
```

## 📈 Escalabilidade e Performance

### Otimizações Implementadas

- **Paginação obrigatória**: Evita sobrecarga de memória em listagens
- **Queries otimizadas**: Uso de índices e agregações eficientes do MongoDB
- **Conexões assíncronas**: Motor para alta concorrência (async/await)
- **Validação eficiente**: Pydantic v2 com validação rápida
- **Service Layer Caching**: Lógica de negócio reutilizável entre endpoints
- **Lazy Loading**: Dados carregados apenas quando necessários

### Carregamento Inteligente de Dados

- **Carregamento Automático**: Via variável `RELOAD_DATA=true`
- **Verificação de Integridade**: Validação de dados antes da inserção
- **Enriquecimento de Dados**: Relacionamentos e campos calculados
- **Tratamento de Duplicatas**: Upsert automático baseado em chaves únicas

### Métricas de Performance

- **~5000 participantes** processados em menos de 30 segundos
- **~1700 escolas** com relacionamentos em menos de 10 segundos  
- **~1500 municípios** enriquecidos com dados regionais
- **Agregações complexas** otimizadas com pipeline do MongoDB

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é desenvolvido para fins acadêmicos.

## 👨‍💻 Autor

Desenvolvido como Trabalho Prático Final da disciplina de Persistência de Dados - 2025.1
