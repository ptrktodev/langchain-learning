from dotenv import load_dotenv  
load_dotenv()  
  
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnableLambda
from pydantic import BaseModel, Field 
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq.chat_models import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory

def get_session_history(session_id: int):
    """
    Retorna o objeto de histórico de chat para uma sessão específica.
    
    Args:
        session_id: Identificador único da sessão de conversa
        
    Returns:
        SQLChatMessageHistory: Objeto que gerencia o histórico no SQLite
    """
    # Cria/conecta ao banco SQLite e retorna o histórico da sessão
    return SQLChatMessageHistory(
        session_id, 
        connection='sqlite:///chat_memory02.db'
    )

# Inicialização do modelo
llm = ChatGroq(model='llama-3.3-70b-versatile', temperature=0)

# Estrutura de dados para roteamento
class Rota(BaseModel):  
    escolha: int = Field(
        description="1 = Planos, Pagamentos e Contratações | 2 = Unidades, Utilização e Dados do Cliente"
    )  
    pensamento: str = Field(
        description="Justificativa da escolha da rota"
    )  
    duvida: str = Field(
        description="Pergunta original do cliente"
    )

# Parser de saída estruturada
parser = PydanticOutputParser(pydantic_object=Rota) 

# Template de roteamento
prompt_router = ChatPromptTemplate([
    ("system", """Você é um roteador inteligente de atendimento ao cliente.

    Analise a pergunta e classifique em um dos setores:

    **Setor 1 - Planos, Pagamentos e Contratações:**
    - Informações sobre planos (Black, Fit, Smart)
    - Valores e formas de pagamento
    - Contratação e cancelamento
    - Benefícios e fidelidade

    **Setor 2 - Unidades, Utilização e Dados do Cliente:**
    - Inauguração de unidades
    - Localização e horários
    - Cadastro de convidados
    - Uso do app e totens
    - Dados cadastrais

    {instructions}"""),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{user_input}")
]).partial(instructions=parser.get_format_instructions())

# Setor 1: Planos e Pagamentos
def setor_planos(rota: Rota) -> str:
    """Processa dúvidas sobre planos, pagamentos e contratações"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Você é um consultor especializado em planos de academia Smart Fit.

        📋 **INFORMAÇÕES DOS PLANOS:**

        🏆 **Plano Black** - R$ 129,90/mês
        • Acesso ilimitado a TODAS as unidades do Brasil
        • Massagem inclusa (conforme disponibilidade)
        • Leve até 5 amigos por mês (1 por dia)
        • Máxima flexibilidade de treino
        • Fidelidade: 12 meses

        💪 **Plano Fit** - R$ 99,90/mês
        • Acesso ilimitado à unidade escolhida
        • Melhor custo-benefício para treino regular
        • Fidelidade: 12 meses

        ⚡ **Plano Smart** - R$ 119,90/mês
        • Acesso à unidade escolhida
        • SEM fidelidade - cancele quando quiser
        • Ideal para quem busca flexibilidade contratual

        **INSTRUÇÕES:**
        - Seja objetivo e consultivo
        - Destaque benefícios relevantes à dúvida
        - Use emojis com moderação para facilitar leitura
        - Sugira o melhor plano quando apropriado
        - Mantenha tom amigável e profissional"""),
        ("user", "{pergunta}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({'pergunta': rota.duvida})

# Setor 2: Unidades e Utilização
def setor_unidades(rota: Rota) -> str:
    """Processa dúvidas sobre unidades, app e serviços"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Você é um assistente especializado em unidades e serviços Smart Fit.

        📍 **INFORMAÇÕES SOBRE UNIDADES:**

        **Inauguração de Novas Unidades:**
        - Unidades em pré-venda ainda não têm data definida
        - Clientes da pré-venda são avisados por e-mail
        - Acompanhe sua caixa de entrada para atualizações

        **Convidados Black (até 5 por mês):**

        📱 *Pelo App Smart Fit:*
        1. Faça login no app
        2. Acesse: Conta → Convidado Black
        3. Permita acesso à localização
        4. Cadastre o convidado
        5. Libere o acesso (gera código válido por 10 minutos)

        🖥️ *Pelos Totens na Unidade:*
        1. Localize o totem de autoatendimento
        2. Siga as instruções na tela
        3. Cadastre e libere o convidado

        ⚠️ **Regras:**
        - Máximo: 1 convidado por dia
        - Limite: 5 convidados por mês
        - Código expira em 10 minutos

        **INSTRUÇÕES:**
        - Forneça informações precisas e passo a passo
        - Seja claro sobre limitações e regras
        - Mantenha tom prestativo e paciente"""),
        ("user", "{pergunta}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({'pergunta': rota.duvida})

# Handler para casos não mapeados
def rota_padrao(rota: Rota) -> str:
    """Mensagem padrão para rotas não identificadas"""
    return (
        "🤔 Desculpe, não consegui identificar o setor adequado para sua dúvida.\n\n"
        "Por favor, reformule sua pergunta ou escolha um dos temas:\n"
        "• Planos, valores e contratação\n"
        "• Unidades, convidados e utilização\n\n"
        f"Sua pergunta: {rota.duvida}"
    )

# Chain principal com roteamento
chain_principal = prompt_router | llm | parser | RunnableBranch(
    (lambda x: x.escolha == 1, RunnableLambda(setor_planos)),
    (lambda x: x.escolha == 2, RunnableLambda(setor_unidades)),
    RunnableLambda(rota_padrao)
)

runnable_with_history = RunnableWithMessageHistory(
    chain_principal,
    get_session_history,
    input_messages_key="user_input",
    history_messages_key="history"
)

while True:
    # Solicita input do usuário
    pergunta = input("Digite seu prompt (ou 'sair' para encerrar): ")

    # Verifica se o usuário quer sair
    if pergunta.lower() == 'sair':
        break
    
    # Processa a mensagem do usuário
    else:
        # Invoca a chain com histórico
        response = runnable_with_history.invoke(
                {'user_input': pergunta},  # Input do usuário
                config={
                    'configurable': { 'session_id': 1}
                }
        )   
        
        # Exibe a resposta do modelo
        print(response)
        print()  # Linha em branco para melhor legibilidade
