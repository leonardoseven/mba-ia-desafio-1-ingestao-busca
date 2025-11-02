# Desafio MBA Engenharia de Software com IA - Full Cycle

Sistema de busca semântica usando RAG (Retrieval-Augmented Generation) com LangChain, PostgreSQL com pgvector, suportando OpenAI e Google Gemini.

## 📋 Requisitos

- Python 3.8+ instalado
- Docker e Docker Compose instalados
- Conta OpenAI ou Google (para API keys)

## 🚀 Instalação e Configuração

### 1. Clonar o repositório (se aplicável)

```bash
git clone <url-do-repositorio>
cd 1-langchain_busca_semantica
```

### 2. Criar ambiente virtual

**Windows:**
```bash
python -m venv venv
cd venv\Scripts
activate
cd ..\..
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Configuração do Banco de Dados PostgreSQL
DATABASE_URL=postgresql://postgres:postgres@localhost:5439/rag
PG_VECTOR_COLLECTION_NAME=documentos_collection

# Caminho do arquivo PDF para ingestão
PDF_PATH=./document.pdf

# Configuração de Embeddings (escolha um provider)
EMBEDDING_PROVIDER=openai  # ou "gemini"
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
GEMINI_EMBEDDING_MODEL=models/embedding-001

# Configuração de LLM (escolha um provider)
LLM_PROVIDER=gemini  # ou "openai"

# API Keys (configure conforme o provider escolhido)
OPENAI_API_KEY=sua_chave_openai_aqui
GOOGLE_API_KEY=sua_chave_google_aqui
```

**Importante:**
- Para usar OpenAI: configure `OPENAI_API_KEY`
- Para usar Gemini: configure `GOOGLE_API_KEY`
- Você pode usar embeddings de um provider e LLM de outro (ex: embeddings OpenAI + LLM Gemini)

### 5. Subir o banco de dados PostgreSQL com pgvector

```bash
docker-compose up -d
```

Este comando irá:
- Subir um container PostgreSQL na porta 5439
- Criar automaticamente a extensão `vector` (pgvector)
- Banco de dados: `rag`
- Usuário: `postgres`
- Senha: `postgres`

**Verificar se está rodando:**
```bash
docker ps
```

Você deve ver o container `postgres_rag` rodando.

## 📄 Processo de Ingestão de Documentos

Após configurar o ambiente, é necessário fazer a ingestão do PDF no banco de dados vetorial.

### Executar ingestão

```bash
python src/ingest.py
```

Este processo irá:
1. Validar as variáveis de ambiente
2. Carregar o PDF do caminho especificado em `PDF_PATH`
3. Dividir o documento em chunks de 1000 caracteres (com overlap de 150)
4. Gerar embeddings para cada chunk usando o provider configurado
5. Armazenar os chunks no PostgreSQL com pgvector

**Tempo estimado:** Depende do tamanho do PDF (alguns segundos a minutos)

## 💬 Usar o Chat para Busca Semântica

Após a ingestão, você pode fazer perguntas sobre o documento usando busca semântica.

### Executar chat

```bash
python src/chat.py
```

Este comando iniciará um chat interativo onde você pode:
1. Digitar perguntas sobre o conteúdo do PDF
2. Receber respostas baseadas apenas no contexto do documento
3. Continuar fazendo perguntas (loop interativo)
4. Para sair, use `Ctrl+C`

**Exemplo de uso:**
```
Digite sua pergunta: O que é inteligência artificial?
[Resposta baseada no documento...]

Digite sua pergunta: Quais são as principais aplicações mencionadas?
[Resposta baseada no documento...]
```

## 🏗️ Estrutura do Projeto

```
1-langchain_busca_semantica/
├── src/
│   ├── ingest.py       # Script de ingestão de documentos
│   ├── search.py       # Módulo de busca semântica e RAG
│   └── chat.py         # Interface de chat interativo
├── docker-compose.yml  # Configuração do PostgreSQL com pgvector
├── requirements.txt    # Dependências Python
├── .env               # Variáveis de ambiente (criar manualmente)
├── document.pdf       # Documento para ingestão
└── README.md          # Este arquivo
```

## 🔧 Comandos Úteis

### Ver logs do PostgreSQL
```bash
docker-compose logs postgres
```

### Parar o banco de dados
```bash
docker-compose down
```

### Parar e remover volumes (limpar dados)
```bash
docker-compose down -v
```

### Reinstalar dependências
```bash
pip install --force-reinstall -r requirements.txt
```

## ⚙️ Configurações Avançadas

### Alterar provider de embeddings/LLM


### Alterar modelo usado

Edite no `.env`:
- `OPENAI_EMBEDDING_MODEL=text-embedding-3-small` (para outros embeddings OpenAI)
- `GEMINI_EMBEDDING_MODEL=models/embedding-001` (para outros embeddings Gemini)

## 🐛 Solução de Problemas

### Erro: "Environment variable X is not set"
- Verifique se o arquivo `.env` existe na raiz do projeto
- Confirme que todas as variáveis necessárias estão configuradas

### Erro: "PDF file not found"
- Verifique se o caminho em `PDF_PATH` está correto
- Use caminho absoluto ou relativo ao diretório raiz

### Erro: "Connection refused" no banco de dados
- Verifique se o Docker está rodando: `docker ps`
- Confirme se o PostgreSQL está ativo: `docker-compose ps`
- Verifique se a porta 5439 está disponível

### Erro de API Key inválida
- Verifique se as chaves estão corretas no `.env`
- Para OpenAI: obtenha em https://platform.openai.com/api-keys
- Para Gemini: obtenha em https://makersuite.google.com/app/apikey

## 📚 Tecnologias Utilizadas

- **LangChain**: Framework para construção de aplicações LLM
- **PostgreSQL**: Banco de dados relacional
- **pgvector**: Extensão para armazenar e buscar vetores
- **OpenAI API**: Para embeddings e modelos GPT
- **Google Gemini API**: Para embeddings e modelos Gemini
- **Python 3.8+**: Linguagem de programação

## 📝 Notas

- O sistema usa RAG (Retrieval-Augmented Generation) para responder perguntas baseadas apenas no contexto do documento
- Se uma pergunta não estiver no contexto, o sistema responderá: "Não tenho informações necessárias para responder sua pergunta."
- Você pode fazer ingestão múltiplas vezes - novos documentos serão adicionados à coleção existente
- Para limpar o banco e começar do zero, pare o Docker e remova os volumes: `docker-compose down -v`
