import streamlit as st
import time
import re
from datetime import date
from fpdf import FPDF

# Configuração da página e remoção do espaço em branco superior
st.set_page_config(page_title="Indenização de Voos", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 750px;
    }
    
    div.stButton > button[kind="primary"] {
        background-color: #16a34a !important;
        border-color: #16a34a !important;
        color: white !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #15803d !important;
        border-color: #15803d !important;
    }

    @keyframes pulse-slow {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.03); }
        100% { opacity: 1; transform: scale(1); }
    }
    .pulsing-text {
        display: inline-block;
        animation: pulse-slow 2s infinite ease-in-out;
    }

    .doc-container {
        font-family: "Times New Roman", Times, serif;
        font-size: 14px;
        background-color: #FFFFFF;
        color: #000000;
        padding: 40px;
        border: 2px solid #333333;
        outline: 4px solid #f0f2f6;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
        margin-top: 20px;
        margin-bottom: 20px;
        border-radius: 2px;
        line-height: 1.6;
        text-align: justify;
    }
    .doc-header {
        text-align: center;
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 40px;
    }
    .blur-text {
        color: transparent;
        text-shadow: 0 0 8px rgba(0,0,0,0.7);
        user-select: none;
    }
    
    .highlight-box {
        border-left: 5px solid #16a34a;
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: #1e293b !important;
    }
    .highlight-box h3, .highlight-box p, .highlight-box span {
        color: #1e293b !important;
    }
    
    .whatsapp-float {
        position: fixed;
        bottom: 25px;
        right: 25px;
        background-color: #25d366;
        color: white !important;
        width: 55px;
        height: 55px;
        border-radius: 50%;
        text-align: center;
        box-shadow: 2px 4px 10px rgba(0,0,0,0.3);
        z-index: 9999;
        text-decoration: none !important;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .whatsapp-float:hover {
        background-color: #128c7e !important;
        color: white !important;
    }

    @media (max-width: 768px) {
        h1 {
            font-size: 1.75rem !important;
            line-height: 1.2 !important;
        }
        h2 {
            font-size: 1.4rem !important;
            line-height: 1.2 !important;
        }
    }
    </style>

    <a href="https://wa.me/556281096811?text=Ol%C3%A1,%20estou%20no%20site%20e%20preciso%20de%20ajuda%20com%20a%20minha%20peti%C3%A7%C3%A3o%20de%20voo." target="_blank" class="whatsapp-float" title="Suporte WhatsApp">
        <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" fill="currentColor" viewBox="0 0 16 16">
          <path d="M13.601 2.326A7.854 7.854 0 0 0 7.994 0C3.627 0 .068 3.558.064 7.926c0 1.399.366 2.76 1.057 3.965L0 16l4.204-1.102a7.933 7.933 0 0 0 3.79.965h.004c4.368 0 7.926-3.558 7.93-7.93A7.898 7.898 0 0 0 13.601 2.326zM7.994 14.521a6.573 6.573 0 0 1-3.356-.92l-.24-.144-2.494.654.666-2.433-.156-.251a6.56 6.56 0 0 1-1.007-3.505c0-3.626 2.957-6.584 6.591-6.584a6.56 6.56 0 0 1 4.66 1.931 6.558 6.558 0 0 1 1.928 4.66c-.004 3.639-2.961 6.592-6.592 6.592zm3.615-4.934c-.197-.099-1.17-.578-1.353-.646-.182-.065-.315-.099-.445.099-.133.193-.513.646-.627.775-.114.133-.232.148-.43.05-.197-.1-.836-.308-1.592-.985-.59-.525-.985-1.175-1.103-1.372-.114-.198-.012-.304.088-.403.087-.088.197-.232.296-.348.1-.114.133-.198.198-.33.065-.134.034-.248-.015-.347-.05-.099-.445-1.076-.612-1.47-.16-.389-.323-.335-.445-.34l-.38-.008c-.133 0-.348.048-.53.247-.182.198-.694.678-.694 1.654 0 .976.71 1.916.81 2.049.098.133 1.394 2.132 3.383 2.992.47.205.84.326 1.129.418.475.152.904.129 1.246.078.38-.058 1.171-.48 1.338-.943.164-.464.164-.86.114-.943-.049-.084-.182-.133-.38-.232z"/>
        </svg>
    </a>
""", unsafe_allow_html=True)

LINKS_TJ = {
    "AC": "https://www.tjac.jus.br", "AL": "https://www.tjal.jus.br", "AP": "https://www.tjap.jus.br",
    "AM": "https://www.tjam.jus.br", "BA": "https://www.tjba.jus.br", "CE": "https://www.tjce.jus.br",
    "DF": "https://www.tjdft.jus.br", "ES": "https://www.tjes.jus.br", "GO": "https://www.tjgo.jus.br",
    "MA": "https://www.tjma.jus.br", "MT": "https://www.tjmt.jus.br", "MS": "https://www.tjms.jus.br",
    "MG": "https://www.tjmg.jus.br", "PA": "https://www.tjpa.jus.br", "PB": "https://www.tjpb.jus.br",
    "PR": "https://www.tjpr.jus.br", "PE": "https://www.tjpe.jus.br", "PI": "https://www.tjpi.jus.br",
    "RJ": "https://www.tjrj.jus.br", "RN": "https://www.tjrn.jus.br", "RS": "https://www.tjrs.jus.br",
    "RO": "https://www.tjro.jus.br", "RR": "https://www.tjrr.jus.br", "SC": "https://www.tjsc.jus.br",
    "SP": "https://www.tjsp.jus.br", "SE": "https://www.tjse.jus.br", "TO": "https://www.tjto.jus.br"
}
ESTADOS = list(LINKS_TJ.keys())

ESTADOS_TEXTO = {
    "AC": "DO ESTADO DO ACRE", "AL": "DO ESTADO DE ALAGOAS", "AP": "DO ESTADO DO AMAPÁ",
    "AM": "DO ESTADO DO AMAZONAS", "BA": "DO ESTADO DA BAHIA", "CE": "DO ESTADO DO CEARÁ",
    "DF": "DO DISTRITO FEDERAL", "ES": "DO ESTADO DO ESPÍRITO SANTO", "GO": "DO ESTADO DE GOIÁS",
    "MA": "DO ESTADO DO MARANHÃO", "MT": "DO ESTADO DE MATO GROSSO", "MS": "DO ESTADO DE MATO GROSSO DO SUL",
    "MG": "DO ESTADO DE MINAS GERAIS", "PA": "DO ESTADO DO PARÁ", "PB": "DO ESTADO DA PARAÍBA",
    "PR": "DO ESTADO DO PARANÁ", "PE": "DO ESTADO DE PERNAMBUCO", "PI": "DO ESTADO DO PIAUÍ",
    "RJ": "DO ESTADO DO RIO DE JANEIRO", "RN": "DO ESTADO DO RIO GRANDE DO NORTE", "RS": "DO ESTADO DO RIO GRANDE DO SUL",
    "RO": "DO ESTADO DE RONDÔNIA", "RR": "DO ESTADO DE RORAIMA", "SC": "DO ESTADO DE SANTA CATARINA",
    "SP": "DO ESTADO DE SÃO PAULO", "SE": "DO ESTADO DE SERGIPE", "TO": "DO ESTADO DO TOCANTINS"
}

CIAS_MAPPING = {
    "LATAM": "LATAM Airlines Brasil", "GOL": "GOL Linhas Aéreas S.A.",
    "Azul": "Azul Linhas Aéreas Brasileiras S.A.", "Voepass": "Voepass Linhas Aéreas",
    "TAP": "TAP Air Portugal", "American Airlines": "American Airlines Inc.",
    "United Airlines": "United Airlines Inc.", "Delta": "Delta Air Lines Inc.",
    "Copa Airlines": "Compañía Panameña de Aviación S.A.", "Air France": "Air France",
    "KLM": "KLM Royal Dutch Airlines", "Aerolíneas Argentinas": "Aerolíneas Argentinas S.A.",
    "Emirates": "Emirates Airlines", "Qatar": "Qatar Airways", "Outra": "Outra"
}
CIAS_SIMPLES = list(CIAS_MAPPING.keys())

AEROPORTOS_NACIONAIS = [
    "São Paulo - Congonhas (CGH)", "São Paulo - Guarulhos (GRU)",
    "São Paulo - Viracopos / Campinas (VCP)", "Rio de Janeiro - Santos Dumont (SDU)",
    "Rio de Janeiro - Galeão (GIG)", "Belo Horizonte - Confins (CNF)",
    "Brasília - Presidente Juscelino Kubitschek (BSB)", "Salvador - Deputado Luís Eduardo Magalhães (SSA)",
    "Fortaleza - Pinto Martins (FOR)", "Recife - Guararapes (REC)",
    "Curitiba - Afonso Pena (CWB)", "Porto Alegre - Salgado Filho (POA)",
    "Goiânia - Santa Genoveva (GYN)", "Florianópolis - Hercílio Luz (FLN)",
    "Vitória - Eurico de Aguiar Salles (VIX)", "Manaus - Eduardo Gomes (MAO)",
    "Belém - Val-de-Cans (BEL)", "Cuiabá - Marechal Rondon (CGB)",
    "Campo Grande (CGR)", "Maceió - Zumbi dos Palmares (MCZ)",
    "Aracaju - Santa Maria (AJU)", "Natal - Governador Aluízio Alves (NAT)",
    "João Pessoa - Presidente Castro Pinto (JPA)", "São Luís - Marechal Cunha Machado (SLZ)",
    "Teresina - Senador Petrônio Portella (THE)", "Palmas - Lysias Rodrigues (PMW)",
    "Porto Velho - Governador Jorge Teixeira (PVH)", "Rio Branco - Plácido de Castro (RBR)",
    "Macapá - Alberto Alcolumbre (MCP)", "Boa Vista - Atlas Brasil Cantanhede (BVB)",
    "Outro / Não listado"
]

AEROPORTOS_INTERNACIONAIS = AEROPORTOS_NACIONAIS[:-1] + [
    "Portugal - Lisboa (LIS)", "Portugal - Porto (OPO)",
    "Estados Unidos - Miami (MIA)", "Estados Unidos - Nova York (JFK)",
    "Estados Unidos - Orlando (MCO)", "Argentina - Buenos Aires (EZE)",
    "França - Paris (CDG)", "Espanha - Madri (MAD)",
    "Chile - Santiago (SCL)", "Itália - Roma (FCO)",
    "Outro / Não listado"
]

def formatar_cpf(cpf_string):
    cpf_numeros = re.sub(r'\D', '', cpf_string)
    if len(cpf_numeros) == 11:
        return f"{cpf_numeros[:3]}.{cpf_numeros[3:6]}.{cpf_numeros[6:9]}-{cpf_numeros[9:]}"
    return cpf_string

def gerar_pdf(uf, nome, cpf, endereco, cia_completa, pnr, trecho, data_voo_br, tipo_voo, problema):
    pdf = FPDF()
    pdf.add_page()
    
    def txt(texto):
        return str(texto).encode('latin-1', 'replace').decode('latin-1')

    uf_texto = ESTADOS_TEXTO.get(uf, f"DO ESTADO DE {uf}")

    pdf.set_font("Arial", 'B', 12)
    pdf.multi_cell(0, 6, txt(f"EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DO JUIZADO ESPECIAL CÍVEL DA COMARCA {uf_texto}"), align="C")
    pdf.ln(8)
    
    pdf.set_font("Arial", '', 10)
    qualificacao = f"{nome.upper()}, portador(a) do CPF nº {cpf}, residente e domiciliado(a) em {endereco}, vem, respeitosamente, à presença de Vossa Excelência, propor a presente:"
    pdf.multi_cell(0, 5, txt(qualificacao), align="J")
    pdf.ln(4)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.multi_cell(0, 5, txt("AÇÃO DE INDENIZAÇÃO POR DANOS MORAIS E MATERIAIS"), align="C")
    pdf.ln(4)
    
    pdf.set_font("Arial", '', 10)
    em_face = f"Em face de {cia_completa.upper()}, pessoa jurídica de direito privado, pelos fatos e fundamentos jurídicos a seguir expostos:"
    pdf.multi_cell(0, 5, txt(em_face), align="J")
    pdf.ln(4)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.multi_cell(0, 5, txt("I - DOS FATOS"), align="L")
    pdf.set_font("Arial", '', 10)
    fatos = (f"O(A) requerente adquiriu bilhetes aéreos sob o código localizador {pnr}, para o trecho entre {trecho} ({tipo_voo}), com data prevista para o voo em {data_voo_br}.\n\n"
             f"Ocorre que, na data aprazada, a empresa requerida falhou na prestação do serviço contratado, incorrendo em {problema.lower()} da viagem, sem prestar a devida assistência material, em afronta direta às normativas aplicáveis.\n\n"
             f"Tal falha causou severos transtornos, angústia e abalo emocional ao(à) requerente, que teve sua rotina abruptamente desorganizada por ato exclusivo da companhia aérea.")
    pdf.multi_cell(0, 5, txt(fatos), align="J")
    pdf.ln(4)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.multi_cell(0, 5, txt("II - DO DIREITO"), align="L")
    pdf.set_font("Arial", '', 10)
    direito = ("A relação jurídica estabelecida submete-se às regras protetivas do Código de Defesa do Consumidor (Lei nº 8.078/90) e legislação complementar aplicável à espécie. A responsabilidade da companhia aérea é objetiva, respondendo pelos danos causados aos consumidores independentemente da existência de culpa, nos termos do art. 14 do referido diploma legal.\n\n"
               "Ademais, a jurisprudência pacífica dos Tribunais consolidou o entendimento de que o dano moral decorrente de falha grave no transporte aéreo opera-se in re ipsa, dispensando a comprovação de efetivo sofrimento psicológico, bastando a demonstração do descaso e do transtorno suportado.")
    pdf.multi_cell(0, 5, txt(direito), align="J")
    pdf.ln(4)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.multi_cell(0, 5, txt("III - DOS PEDIDOS"), align="L")
    pdf.set_font("Arial", '', 10)
    pedidos = ("Diante do exposto, requer a Vossa Excelência:\n"
               "a) A citação da empresa ré para, querendo, contestar a presente ação sob pena de revelia;\n"
               "b) A procedência total da ação para condenar a requerida ao pagamento de indenização por danos morais no valor de R$ 10.000,00 (dez mil reais);\n"
               "c) A concessão dos benefícios da justiça gratuita, por ser o(a) requerente hipossuficiente.\n\n"
               f"Dá-se à causa o valor de R$ 10.000,00.\n\n"
               "Termos em que,\nPede deferimento.\n\n"
               f"{uf}, {data_voo_br}.\n\n"
               f"___________________________________\n{nome.upper()}")
    pdf.multi_cell(0, 5, txt(pedidos), align="J")
    
    return bytes(pdf.output(dest='S'), encoding='latin-1')

@st.dialog("Termos e Condições de Uso")
def mostrar_termos():
    st.markdown("""
    ### 1. Objeto da Plataforma
    Este sistema tem caráter estritamente instrumental, auxiliando o usuário na formatação autônoma de documentos para protocolo no Juizado Especial Cível (JEC).
    
    ### 2. Autonomia do Usuário
    O usuário é integralmente responsável pelas informações fornecidas e pelo protocolo da petição perante o Tribunal competente. A plataforma não substitui a consultoria jurídica formal, atuando como ferramenta de autoatendimento.
    
    ### 3. Responsabilidade sobre Prazos
    Cabe ao usuário a conferência das datas e limites legais de prescrição aplicáveis ao seu caso específico.
    """)
    if st.button("Fechar", use_container_width=True):
        st.rerun()

@st.dialog("Política de Privacidade")
def mostrar_privacidade():
    st.markdown("""
    ### 1. Coleta de Dados
    Coletamos apenas os dados essenciais estritamente necessários para preenchimento da petição inicial e envio de comunicações transacionais (como e-mail e CPF).
    
    ### 2. Armazenamento e Segurança
    Os dados informados são processados em memória de sessão e não são comercializados ou compartilhados com terceiros para fins publicitários.
    
    ### 3. Conformidade
    Tratamento de dados alinhado aos princípios da Lei Geral de Proteção de Dados (LGPD - Lei nº 13.709/2018).
    """)
    if st.button("Fechar", use_container_width=True):
        st.rerun()

if 'etapa' not in st.session_state:
    st.session_state.etapa = 1
if 'target_etapa' not in st.session_state:
    st.session_state.target_etapa = 1

def ir_para_etapa(destino):
    st.session_state.target_etapa = destino
    st.session_state.etapa = "loading"
    st.rerun()

if st.session_state.etapa == "loading":
    st.markdown("""
        <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(4px); z-index: 999999; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; font-family: sans-serif;">
            <div style="background: white; color: #1e293b; padding: 35px 45px; border-radius: 16px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3); text-align: center; max-width: 400px; width: 90%;">
                <div style="border: 4px solid #f3f3f3; border-top: 4px solid #16a34a; border-radius: 50%; width: 45px; height: 45px; animation: spin 1s linear infinite; margin: 0 auto 20px auto;"></div>
                <h3 style="margin: 0 0 10px 0; font-size: 19px; font-weight: 700; color: #1e293b;">Processando dados...</h3>
                <p style="margin: 0; font-size: 14px; color: #64748b; line-height: 1.4;">Analisando parâmetros regulatórios e estruturando documento jurídico.</p>
            </div>
        </div>
        <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>
    """, unsafe_allow_html=True)
    time.sleep(2.0)
    st.session_state.etapa = st.session_state.target_etapa
    st.rerun()

# --- ETAPA 1: CAPTAÇÃO BASEADA NA DOR ---
elif st.session_state.etapa == 1:
    st.markdown("""
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 35px; border-radius: 16px; color: white; margin-bottom: 20px;">
            <span style="background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); font-size: 11px; font-weight: 600; padding: 5px 12px; border-radius: 20px; text-transform: uppercase; display: inline-flex; align-items: center; gap: 6px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                Verificação Rápida e Sem Riscos
            </span>
            <h1 style="font-size: 32px; font-weight: 800; margin-top: 14px; line-height: 1.2;">
                Voo atrasado ou cancelado?<br>
                <span style="color: #60a5fa;" class="pulsing-text">Receba até R$ 10.000!</span>
            </h1>
            <p style="color: #cbd5e1; font-size: 15px; margin-top: 8px;">
                Você tem direitos garantidos por lei. Nós cuidamos de toda a burocracia para você ser compensado de forma rápida.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### O que deu errado com o seu voo?")
    
    problema_escolhido = st.radio(
        "Selecione o incidente principal:",
        ["Voo Atrasado (mais de 3h)", "Voo Cancelado", "Perda de Conexão / Outros"],
        index=0 if st.session_state.get('problema') in [None, "Voo Atrasado (mais de 3h)"] else 0,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### Seus Dados Cadastrais")
    
    nome = st.text_input("Nome Completo:", placeholder="Digite seu nome completo", value=st.session_state.get('nome', ''))
    email = st.text_input("E-mail para envio da Petição:", placeholder="seu@email.com", value=st.session_state.get('email', ''))
    
    index_cia = 0
    if 'cia_simples' in st.session_state and st.session_state.cia_simples in CIAS_SIMPLES:
        index_cia = CIAS_SIMPLES.index(st.session_state.cia_simples)
    cia_selecionada = st.selectbox("Companhia Aérea Responsável:", CIAS_SIMPLES, index=index_cia)
    
    st.markdown("")
    if st.button("Descubra o quanto pode ganhar ➡️", type="primary", use_container_width=True):
        if len(nome.strip().split()) < 2:
            st.error("Por favor, insira seu nome completo (Nome e Sobrenome).")
        elif not email or "@" not in email or "." not in email:
            st.error("Por favor, insira um e-mail válido.")
        else:
            st.session_state.problema = problema_escolhido
            st.session_state.nome = nome.strip()
            st.session_state.primeiro_nome = nome.strip().split()[0]
            st.session_state.email = email.strip()
            st.session_state.cia_simples = cia_selecionada
            st.session_state.cia_completa = CIAS_MAPPING[cia_selecionada]
            ir_para_etapa(2)

# --- ETAPA 2: ROTA, CONEXÕES E DADOS DO VOO ---
elif st.session_state.etapa == 2:
    primeiro_nome = st.session_state.get('primeiro_nome', 'Visitante')
    st.title(f"Agora, {primeiro_nome}, precisamos dos detalhes da sua rota")
    
    endereco = st.text_input("Endereço Residencial Completo:", placeholder="Rua, Número, Bairro, Cidade - CEP", value=st.session_state.get('endereco', ''))
    cpf_input = st.text_input("CPF (Formato: 000.000.000-00):", max_chars=14, placeholder="000.000.000-00", value=st.session_state.get('cpf', ''))
    
    index_estado = 0
    if 'uf' in st.session_state and st.session_state.uf in ESTADOS:
        index_estado = ESTADOS.index(st.session_state.uf)
    uf = st.selectbox("Selecione seu Estado (UF) para protocolo:", ESTADOS, index=index_estado)

    tipo_voo = st.radio("Tipo de Voo:", ["Nacional", "Internacional"], horizontal=True, index=0 if st.session_state.get('tipo_voo', 'Nacional') == 'Nacional' else 1)

    lista_aeroportos = AEROPORTOS_NACIONAIS if tipo_voo == "Nacional" else AEROPORTOS_INTERNACIONAIS

    col1, col2 = st.columns(2)
    with col1:
        index_origem = lista_aeroportos.index(st.session_state.get('origem_sel', lista_aeroportos[0])) if st.session_state.get('origem_sel') in lista_aeroportos else 0
        origem_sel = st.selectbox("Aeroporto Específico de Origem:", lista_aeroportos, index=index_origem)
        if origem_sel == "Outro / Não listado":
            origem = st.text_input("Digite a Origem (Cidade - Sigla IATA):", placeholder="Ex: Ribeirão Preto - SP (RAO)", value=st.session_state.get('origem_custom', ''))
        else:
            origem = origem_sel

    with col2:
        index_destino = lista_aeroportos.index(st.session_state.get('destino_sel', lista_aeroportos[1] if len(lista_aeroportos) > 1 else lista_aeroportos[0])) if st.session_state.get('destino_sel') in lista_aeroportos else (1 if len(lista_aeroportos) > 1 else 0)
        destino_sel = st.selectbox("Aeroporto Específico de Destino Final:", lista_aeroportos, index=index_destino)
        if destino_sel == "Outro / Não listado":
            destino = st.text_input("Digite o Destino (Cidade - Sigla IATA):", placeholder="Ex: Joinville - SC (JOI)", value=st.session_state.get('destino_custom', ''))
        else:
            destino = destino_sel
        
    tipo_conexao = st.radio("O voo foi direto ou teve conexões?", ["Sim, foi um voo direto", "Não, teve no mínimo 1 conexão"], horizontal=True)
    
    nao_lembro_dados = st.checkbox("Não tenho o código PNR ou número do voo em mãos agora", value=st.session_state.get('nao_lembro_dados', False))

    if not nao_lembro_dados:
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            pnr = st.text_input("Código Localizador (PNR):", max_chars=6, placeholder="Ex: XYZ123", value=st.session_state.get('pnr', '')).upper()
        with col_v2:
            num_voo = st.text_input("Identificação do Voo Principal:", placeholder="Ex: G3 1409", value=st.session_state.get('num_voo', ''))
    else:
        pnr = "PENDENTE_USUARIO"
        num_voo = "PENDENTE_USUARIO"
        st.info(f"💡 Tudo bem, {primeiro_nome}! Você poderá atualizar esses dados posteriormente com o suporte ou na petição.")
        
    data_voo = st.date_input("Data do Voo:", max_value=date(2026, 7, 28), format="DD/MM/YYYY")

    hoje = date(2026, 7, 28)
    dias_passados = (hoje - data_voo).days
    prazo_valido = True
    limite_texto = ""
    
    if tipo_voo == "Nacional" and dias_passados > (5 * 365):
        prazo_valido = False
        limite_texto = "5 anos (Voo Nacional)"
    elif tipo_voo == "Internacional" and dias_passados > (2 * 365):
        prazo_valido = False
        limite_texto = "2 anos (Voo Internacional)"

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("⬅️ Voltar", use_container_width=True):
            ir_para_etapa(1)
    with col_b2:
        if st.button("Continuar para Pré-visualização ➡️", type="primary", use_container_width=True):
            origem_valida = origem.strip() if origem_sel == "Outro / Não listado" else origem
            destino_valida = destino.strip() if destino_sel == "Outro / Não listado" else destino
            
            if not endereco or len(re.sub(r'\D', '', cpf_input)) != 11:
                st.error("Por favor, preencha o endereço completo e um CPF válido com 11 dígitos.")
            elif not nao_lembro_dados and (len(pnr) != 6 or not num_voo):
                st.error("Preencha o PNR (6 dígitos) e a identificação do voo, ou marque a opção 'Não tenho o código PNR ou número do voo em mãos agora'.")
            elif not origem_valida or not destino_valida:
                st.error("Preencha os aeroportos de origem e destino.")
            elif origem_valida == destino_valida:
                st.error("A origem e o destino não podem ser iguais.")
            elif not prazo_valido:
                st.error(f"❌ Não é possível prosseguir. O prazo limite legal de {limite_texto} para requerer esta indenização já expirou.")
            else:
                st.session_state.endereco = endereco
                st.session_state.cpf = formatar_cpf(cpf_input)
                st.session_state.uf = uf
                st.session_state.nao_lembro_dados = nao_lembro_dados
                st.session_state.pnr = pnr
                st.session_state.num_voo = num_voo
                st.session_state.origem_sel = origem_sel
                st.session_state.destino_sel = destino_sel
                st.session_state.origem_custom = origem if origem_sel == "Outro / Não listado" else ""
                st.session_state.destino_custom = destino if destino_sel == "Outro / Não listado" else ""
                st.session_state.origem = origem_valida
                st.session_state.destino = destino_valida
                st.session_state.trecho = f"{origem_valida} até {destino_valida}"
                st.session_state.data_voo_br = data_voo.strftime("%d/%m/%Y")
                st.session_state.tipo_voo = tipo_voo
                st.session_state.tipo_conexao = tipo_conexao
                ir_para_etapa(3)

# --- ETAPA 3: VISUALIZAÇÃO PRÉVIA ---
elif st.session_state.etapa == 3:
    if st.button("⬅️ Corrigir Dados"):
        ir_para_etapa(2)
            
    primeiro_nome = st.session_state.get('primeiro_nome', 'Visitante')
    st.title("Pré-visualização da sua Petição")
    st.info(f"{primeiro_nome}, confira os dados estruturados abaixo. A fundamentação legal completa será liberada na finalização.")
    
    uf_extenso_preview = ESTADOS_TEXTO.get(st.session_state.uf, f"DO ESTADO DE {st.session_state.uf}")

    pnr_val = st.session_state.pnr
    pnr_html = f'<span style="color: red;">{pnr_val}</span>' if pnr_val == "PENDENTE_USUARIO" else pnr_val

    num_voo_val = st.session_state.num_voo
    num_voo_html = f'<span style="color: red;">{num_voo_val}</span>' if num_voo_val == "PENDENTE_USUARIO" else num_voo_val

    st.markdown(f"""
    <div class="doc-container">
        <div class="doc-header">
            EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DO JUIZADO ESPECIAL CÍVEL DA COMARCA {uf_extenso_preview}
        </div>
        <p><b>REQUERENTE:</b> {st.session_state.nome.upper()}, portador(a) do CPF nº {st.session_state.cpf}, residente e domiciliado(a) em {st.session_state.endereco}. E-mail: {st.session_state.email}.</p>
        <p align="center"><b>AÇÃO DE INDENIZAÇÃO POR DANOS MORAIS E MATERIAIS</b></p>
        <p><b>REQUERIDO:</b> {st.session_state.cia_completa.upper()}, pessoa jurídica de direito privado...</p>
        <p><b>I - DOS FATOS</b><br>
        O(A) requerente adquiriu bilhetes aéreos sob o código localizador {pnr_html} (Voo {num_voo_html}), para o trecho entre {st.session_state.trecho} ({st.session_state.tipo_voo}), com data marcada para {st.session_state.data_voo_br}. Incidente registrado: {st.session_state.problema}. Ocorre que a empresa falhou gravemente na prestação do serviço...</p>
        <p><b>II - DO DIREITO</b></p>
        <p class="blur-text">
        A relação jurídica submete-se às regras do Código de Defesa do Consumidor. A responsabilidade da companhia aérea é objetiva nos termos do artigo 14 da Lei 8078/90. O dano moral ocorre in re ipsa configurando quebra das resoluções da ANAC aplicáveis à espécie e jurisprudência pacífica do STJ.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("⬅️ Voltar para Edição", use_container_width=True):
            ir_para_etapa(2)
    with col_b2:
        if st.button("Continuar para Finalização", type="primary", use_container_width=True):
            ir_para_etapa(4)

# --- ETAPA 4: PAGAMENTO E ENTREGA ---
elif st.session_state.etapa == 4:
    if st.button("⬅️ Voltar para Visualização"):
        ir_para_etapa(3)

    st.title("Liberação do seu Documento")
    
    if 'pagamento_aprovado' not in st.session_state:
        st.session_state.pagamento_aprovado = False

    if not st.session_state.pagamento_aprovado:
        st.markdown(f"""
        <div class="highlight-box">
            <h3 style="margin-top: 0; margin-bottom: 10px; font-size: 18px; font-weight: 700;">Fique com 100% da sua indenização</h3>
            <p style="margin: 0; font-size: 14px; line-height: 1.5;">Advogados e intermediários cobram até 30% do que você ganha no tribunal. Com a petição pronta, você mesmo protocola em minutos e coloca todo o valor no bolso, sem dor de cabeça.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.link_button("Liberar Meu Documento Agora (R$ 56,90)", "https://link-do-mercado-pago.com", type="primary", use_container_width=True)
        
        st.markdown("---")
        st.write("🔧 **Ambiente de Teste:**")
        if st.button("⚡ Simular Pagamento Aprovado (Bypass de Teste)"):
            st.session_state.pagamento_aprovado = True
            st.rerun()
            
    else:
        st.success("🎉 Pagamento Confirmado com Sucesso!")
        st.info(f"Uma cópia de segurança da sua petição também foi encaminhada para o e-mail cadastrado: **{st.session_state.email}**.")
        
        pdf_bytes = gerar_pdf(
            st.session_state.uf, 
            st.session_state.nome, 
            st.session_state.cpf,
            st.session_state.endereco, 
            st.session_state.cia_completa, 
            st.session_state.pnr,
            st.session_state.trecho, 
            st.session_state.data_voo_br, 
            st.session_state.tipo_voo,
            st.session_state.problema
        )
        
        st.download_button(
            label="📥 Baixar Minha Petição Oficial (PDF)",
            data=pdf_bytes,
            file_name=f"peticao_atraso_voo_{st.session_state.pnr}.pdf",
            mime="application/pdf",
            type="primary"
        )
        
        st.markdown("---")
        st.subheader("Roteiro Prático: Como Resolver seu Problema Agora")
        
        st.markdown(f"""
        Como o valor padrão pedido é de R$ 10.000,00 (abaixo de 20 salários mínimos), **você não precisa de advogado**. 
        Siga o processo passo a passo:
        
        1. **Baixe o PDF** no botão acima (ou confira seu e-mail).
        2. **Separe seus Documentos:** Tire foto ou salve em PDF o seu RG/CPF, Comprovante de Residência e o seu Cartão de Embarque/E-ticket.
        3. **Acesse o Tribunal:** Clique no botão oficial abaixo correspondente ao seu estado (**TJ{st.session_state.uf}**).
        4. **Cadastre-se e Envie:** Entre usando sua conta do **Gov.br**, selecione 'Ajuizamento de Causa Própria' (ou Atermação Online) e anexe esta Petição junto com seus documentos.
        """)
        
        link_do_tribunal = LINKS_TJ.get(st.session_state.uf, "https://www.tjsp.jus.br")
        st.link_button(f"🔗 Protocolar Petição no Portal do TJ{st.session_state.uf}", link_do_tribunal)
        
        st.markdown("""
        ---
        💡 *Dica Alternativa Express:* Você também pode simplesmente copiar os trechos dos 'Fatos' da sua petição e abrir uma reclamação direta no portal **Consumidor.gov.br**. As companhias costumam fazer propostas de acordo em dinheiro lá em até 10 dias úteis para evitar o processo judicial.
        """)

st.markdown("---")
col_footer1, col_footer2, col_footer3 = st.columns(3)
with col_footer1:
    if st.button("Termos de Uso", key="link_termos", use_container_width=True):
        mostrar_termos()
with col_footer2:
    if st.button("Política de Privacidade", key="link_priv", use_container_width=True):
        mostrar_privacidade()
with col_footer3:
    st.markdown("<p style='text-align: center; color: gray; font-size: 12px;'>© 2026 Indenização de Voos</p>", unsafe_allow_html=True)