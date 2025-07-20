# API ENEM - Dados Abertos

Sistema de API RESTful para exploração e manipulação de dados do ENEM (Exame Nacional do Ensino Médio) utilizando FastAPI e MongoDB.

## 📋 Descrição do Projeto

Este projeto foi desenvolvido como Trabalho Prático Final da disciplina de Persistência de Dados, tendo como objetivo integrar conhecimentos de:

- **Coleta e Preparação de Dados**: Dados do ENEM obtidos através do Portal Brasileiro de Dados Abertos
- **Persistência de Dados**: Modelagem utilizando MongoDB com relacionamentos apropriados
- **Desenvolvimento de API**: API RESTful completa com FastAPI
- **Consultas Avançadas**: Queries complexas, filtros dinâmicos e paginação
- **Boas Práticas**: Tratamento de erros, logging e documentação automática

## 🏗️ Arquitetura

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
- **Services**: Lógica de negócio e regras da aplicação
- **Routes**: Definição dos endpoints da API REST
- **Config**: Configurações de logging e aplicação

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
│   ├── escola_routes.py
│   ├── municipio_routes.py
│   ├── participante_routes.py
│   └── resultado_routes.py
├── schemas/                   # Schemas de requisição e resposta
│   ├── escola_schemas.py
│   ├── municipio_schemas.py
│   ├── participante_schemas.py
│   ├── resultado_schemas.py
│   └── README.md
├── scripts/                   # Scripts utilitários
│   └── load_data.py          # Script para carregar dados
├── services/                  # Lógica de negócio
│   ├── municipio_service.py
│   └── resultado_service.py
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
# Executar script de carregamento
python src/scripts/load_data.py
```

### 5. Executar a aplicação

```bash
# Iniciar servidor de desenvolvimento
uvicorn main:app --reload --host 0.0.0.0 --port 8000
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
- `GET /escolas/estatisticas/dependencia` - Estatísticas por dependência administrativa
- `GET /escolas/estatisticas/top-participantes` - Escolas com mais participantes

#### Participantes
- `GET /participantes/` - Listar participantes com paginação e filtros
- `GET /participantes/{id}` - Obter participante por ID
- `GET /participantes/inscricao/{nu_inscricao}` - Obter participante por número de inscrição
- `GET /participantes/estatisticas/sexo` - Distribuição por sexo
- `GET /participantes/estatisticas/faixa-etaria` - Distribuição por faixa etária
- `GET /participantes/estatisticas/cor-raca` - Distribuição por cor/raça

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
curl -X GET "http://localhost:8000/escolas/estatisticas/dependencia"
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

Esta separação facilita a manutenção e reutilização dos schemas em diferentes partes da aplicação.

## 🔒 Tratamento de Erros e Logging

- **Validação de entrada**: Pydantic para validação automática
- **Tratamento de exceções**: Handlers globais para erros
- **Logging estruturado**: Logs detalhados salvos em `src/logs/enem_api.log`
- **Códigos HTTP apropriados**: Status codes semânticos
- **Configuração de logs**: Configurada em `src/config/logs.py`

## 📈 Escalabilidade e Performance

- **Paginação obrigatória**: Evita sobrecarga de memória
- **Queries otimizadas**: Uso de índices e agregações eficientes
- **Conexões assíncronas**: Motor para alta concorrência
- **Validação eficiente**: Pydantic com validação rápida

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
