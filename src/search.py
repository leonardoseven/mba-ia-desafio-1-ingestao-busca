import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_postgres import PGVector
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""


def get_embeddings():
    provider = os.getenv("EMBEDDING_PROVIDER", "openai").lower()
    
    if provider == "openai":
        model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        return OpenAIEmbeddings(model=model)
    elif provider == "gemini":
        model = os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")
        return GoogleGenerativeAIEmbeddings(model=model)
    else:
        raise RuntimeError(f"EMBEDDING_PROVIDER deve ser 'openai' ou 'gemini'. Valor atual: {provider}")


def get_llm():
    """Retorna o LLM baseado na variável de ambiente LLM_PROVIDER"""
    llm_provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    if llm_provider == "openai":
        model = os.getenv("OPENAI_MODEL", "gpt-5-nano")
        return ChatOpenAI(model=model, temperature=0.1)
    elif llm_provider == "gemini":
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
        return ChatGoogleGenerativeAI(model=model, temperature=0.1)
    else:
        raise RuntimeError(f"LLM_PROVIDER deve ser 'openai' ou 'gemini'. Valor atual: {llm_provider}")


def search_prompt(question=None):
    try:
        # Valida variáveis de ambiente necessárias
        required_vars = ["PG_VECTOR_COLLECTION_NAME", "DATABASE_URL"]
        
        embedding_provider = os.getenv("EMBEDDING_PROVIDER", "openai").lower()
        if embedding_provider == "openai" and not os.getenv("OPENAI_API_KEY"):
            required_vars.append("OPENAI_API_KEY")
        elif embedding_provider == "gemini" and not os.getenv("GOOGLE_API_KEY"):
            required_vars.append("GOOGLE_API_KEY")
        
        llm_provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        if llm_provider == "openai" and not os.getenv("OPENAI_API_KEY"):
            required_vars.append("OPENAI_API_KEY")
        elif llm_provider == "gemini" and not os.getenv("GOOGLE_API_KEY"):
            required_vars.append("GOOGLE_API_KEY")
        
        for var in required_vars:
            if not os.getenv(var):
                raise RuntimeError(f"Environment variable {var} is not set")
        
        embeddings = get_embeddings()
        
        store = PGVector(
            embeddings=embeddings,
            collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
            connection=os.getenv("DATABASE_URL"),
            use_jsonb=True
        )
        
        results = store.similarity_search_with_score(question, k=10)      

        template = PromptTemplate(
          input_variables=["contexto", "pergunta"],
          template=PROMPT_TEMPLATE,
        )

        llm = get_llm()
        
        chain = template| llm | StrOutputParser()

        response = chain.invoke({"contexto": results, "pergunta": question})
        return response
        
    except Exception as e:
        print(f"Erro ao criar chain RAG: {e}")
        return None