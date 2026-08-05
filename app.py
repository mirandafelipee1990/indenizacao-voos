import streamlit as st
import time
import re
import locale
import mercadopago
import os
import requests
from datetime import date
from fpdf import FPDF
from supabase import create_client, Client

# --- CONFIGURAÇÃO SUPABASE ---
SUPABASE_URL = "https://vratkswxzhwnjkwltjyi.supabase.co"
SUPABASE_KEY = "sb_publishable_6q7iqojRH_zOWGJv83Xstg_CSTAEdIq"
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    supabase = None

try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
    except:
        pass

st.set_page_config(
    page_title="Resolfix - Notificação Extrajudicial de Voo",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def carregar_dados_supabase(id_pedido):
    if supabase:
        resposta = supabase.table("pedidos").select("*").eq("id", id_pedido).execute()
        if len(resposta.data) > 0:
            dados = resposta.data[0]
            for chave, valor in dados.items():
                if chave != "id":
                    st.session_state[chave] = valor
            st.session_state.id_pedido = id_pedido
            return True
    return False

# --- CAPTURA DA URL (RECUPERAÇÃO DE CARRINHO OU RETORNO DO MP) ---
query_params = st.query_params

ref_id = query_params.get("external_reference") or query_params.get("recuperar")

if ref_id:
    sucesso = carregar_dados_supabase(ref_id)
    if sucesso:
        st.session_state.etapa = 4
        status_param = query_params.get("status") or query_params.get("collection_status")
        
        # 1. Verifica se a URL diz aprovado OU se o banco já gravou como 'processed'
        if status_param in ["approved", "sucesso"] or st.session_state.get("status") == "processed":
            st.session_state.pagamento_aprovado = True
        else:
            # 2. Se a URL diz 'pending', faz uma checagem real na API do MP para evitar o falso negativo
            try:
                sdk_temp = mercadopago.SDK("APP_USR-1689026143657988-072919-e2bdce9cb1761b0cf1a4298c53034a33-188311197")
                busca = sdk_temp.payment().search({"external_reference": ref_id})
                pagamentos = busca.get("response", {}).get("results", [])
                st.session_state.pagamento_aprovado = any(p.get("status") == "approved" for p in pagamentos)
            except:
                st.session_state.pagamento_aprovado = False

# --- CAPTURA DE DADOS VIA E-MAIL (RECUPERAÇÃO ANTIGA) ---
for chave in ["nome", "email", "cpf", "uf"]:
    if chave in query_params and chave not in st.session_state:
        st.session_state[chave] = query_params[chave]

st.markdown('<div id="topo"></div>', unsafe_allow_html=True)

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
    div[data-testid="stLinkButton"] > a {
        background-color: #16a34a !important;
        border-color: #16a34a !important;
        color: white !important;
        text-decoration: none !important;
    }
    div[data-testid="stLinkButton"] > a:hover {
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
    @media (max-width: 768px) {
        h1 {
            font-size: 1.75rem !important;
            line-height: 1.2 !important;
        }
        h2 {
            font-size: 1.4rem !important;
            line-height: 1.2 !important;
        }
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }
    </style>
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

def obter_texto_fatos(problema):
    if problema == "Voo Atrasado (mais de 4h)":
        return "Ocorre que, na data aprazada, o voo contratado sofreu um atraso superior a 4 horas, deixando o(a) requerente aguardando no aeroporto por longo período sem a devida assistência material por parte da companhia aérea, em afronta direta às normativas da ANAC e do Código de Defesa do Consumidor."
    elif problema == "Voo Cancelado":
        return "Ocorre que, na data aprazada, a empresa requerida procedeu ao cancelamento imotivado da viagem, frustrando completamente o planejamento do(a) requerente e deixando-o(a) desamparado(a), sem o suporte material obrigatório ou reacomodação em tempo útil."
    else:
        return "Ocorre que, durante a execução do contrato de transporte, o(a) requerente enfrentou falhas graves na prestação do serviço com quebra de itinerário e perda de conexão, sem a assistência material adequada ou solução célere por parte da companhia aérea."

def formatar_cpf(cpf_string):
    cpf_numeros = re.sub(r'\D', '', cpf_string)
    if len(cpf_numeros) == 11:
        return f"{cpf_numeros[:3]}.{cpf_numeros[3:6]}.{cpf_numeros[6:9]}-{cpf_numeros[9:]}"
    return cpf_string

def gerar_pdf(uf, nome, cpf, endereco, cia_completa, pnr, num_voo, trecho, data_voo_br, tipo_voo, problema, conexoes_info):
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
    
    trecho_voo_str = f" (Voo {num_voo})" if num_voo and num_voo != "PENDENTE_USUARIO" else ""
    pnr_str = "pendente" if pnr == "PENDENTE_USUARIO" else f"código localizador {pnr}"
    
    trecho_fatos_especifico = obter_texto_fatos(problema)
    
    fatos = (f"O(A) requerente adquiriu bilhetes aéreos sob o {pnr_str}{trecho_voo_str}, para o trecho entre {trecho} ({tipo_voo}), com data prevista para o voo em {data_voo_br}.\n\n"
             f"{conexoes_info}"
             f"{trecho_fatos_especifico}\n\n"
             f"Tal falha ultrapassa o mero aborrecimento cotidiano, causando severos transtornos, angústia e abalo emocional ao(à) requerente, que teve sua rotina abruptamente desorganizada por ato exclusivo da companhia aérea.")
    
    pdf.multi_cell(0, 5, txt(fatos), align="J")
    pdf.ln(4)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.multi_cell(0, 5, txt("II - DO DIREITO"), align="L")
    pdf.set_font("Arial", '', 10)
    direito = ("A relação jurídica estabelecida submete-se às regras protetivas do Código de Defesa do Consumidor (Lei nº 8.078/90) e legislação complementar aplicável à espécie. A responsabilidade da companhia aérea é objetiva, respondendo pelos danos causados aos consumidores independentemente da existência de culpa, nos termos do art. 14 do referido diploma legal.\n\n"
               "Ademais, a jurisprudência pacífica dos Tribunais e as resoluções da ANAC consolidaram o entendimento de que atrasos superiores a 4 horas ou cancelamentos sem aviso prévio geram direito à reacomodação e configuram dano moral in re ipsa, dispensando a comprovação de efetivo sofrimento psicológico, bastando a demonstração do descaso e do transtorno suportado.")
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

def avancar_etapa(destino):
    st.session_state.target_etapa = destino
    st.session_state.etapa = "loading"
    st.rerun()

def voltar_etapa(destino):
    st.session_state.etapa = destino
    st.rerun()

@st.dialog("⚠️ Atenção: Informação Pendente")
def aviso_pendencia():
    st.error("Você deixou o Código Localizador (PNR) como pendente.")
    st.write("Recomendamos que você retorne e preencha essa informação antes de prosseguir para o pagamento, pois a petição ficará incompleta e o juizado pode exigir esse dado posteriormente.")
    if st.button("Voltar e Preencher (Recomendado)", type="primary", use_container_width=True):
        voltar_etapa(2)

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
    
    time.sleep(1.0)
    st.session_state.etapa = st.session_state.target_etapa
    st.markdown("<script>window.parent.scrollTo({ top: 0, behavior: 'instant' });</script>", unsafe_allow_html=True)
    st.rerun()

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
                Gere sua petição pronta em 5 minutos e protocole você mesmo, sem pagar honorários a advogados.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 1. O que deu errado com o seu voo?")
    problema_escolhido = st.radio(
        "Selecione o incidente principal:",
        ["Voo Atrasado (mais de 4h)", "Voo Cancelado", "Perda de Conexão / Outros"],
        index=0 if st.session_state.get('problema') in [None, "Voo Atrasado (mais de 4h)"] else 0,
        label_visibility="collapsed"
    )

    st.markdown("### 2. Relato do Ocorrido")
    relato_danos = st.text_area(
        "Descreva brevemente o que aconteceu e os prejuízos sofridos:",
        placeholder="Ex: Fiquei mais de 5 horas aguardando no aeroporto sem assistência adequada...",
        value=st.session_state.get('relato_danos', '')
    )

    st.markdown("### 3. Companhia Aérea")
    index_cia = None
    if 'cia_simples' in st.session_state and st.session_state.cia_simples in CIAS_SIMPLES:
        index_cia = CIAS_SIMPLES.index(st.session_state.cia_simples)
    cia_selecionada = st.selectbox("Qual foi a companhia aérea responsável?", CIAS_SIMPLES, index=index_cia, placeholder="Selecione a companhia aérea...")

    st.markdown("")
    if st.button("Continuar ➡️", type="primary", use_container_width=True):
        if not cia_selecionada:
            st.error("Por favor, selecione a companhia aérea responsável.")
        else:
            st.session_state.problema = problema_escolhido
            st.session_state.relato_danos = relato_danos
            st.session_state.cia_simples = cia_selecionada
            st.session_state.cia_completa = CIAS_MAPPING[cia_selecionada]
            avancar_etapa(2)

elif st.session_state.etapa == 2:
    st.markdown("### Dados do Voo")
    
    tipo_voo = st.radio("Tipo de Voo:", ["Nacional", "Internacional"], horizontal=True, index=0 if st.session_state.get('tipo_voo', 'Nacional') == 'Nacional' else 1)
    lista_aeroportos = AEROPORTOS_NACIONAIS if tipo_voo == "Nacional" else AEROPORTOS_INTERNACIONAIS
    
    col1, col2 = st.columns(2)
    with col1:
        index_origem = None
        if 'origem_sel' in st.session_state and st.session_state.get('origem_sel') in lista_aeroportos:
            index_origem = lista_aeroportos.index(st.session_state.get('origem_sel'))
        origem_sel = st.selectbox("Aeroporto Específico de Origem:", lista_aeroportos, index=index_origem, placeholder="Escolha o aeroporto de origem...")
        
        if origem_sel == "Outro / Não listado":
            origem = st.text_input("Digite a Origem (Cidade - Sigla IATA):", placeholder="Ex: Ribeirão Preto - SP (RAO)", value=st.session_state.get('origem_custom', ''))
        else:
            origem = origem_sel if origem_sel else ""

    with col2:
        index_destino = None
        if 'destino_sel' in st.session_state and st.session_state.get('destino_sel') in lista_aeroportos:
            index_destino = lista_aeroportos.index(st.session_state.get('destino_sel'))
        destino_sel = st.selectbox("Aeroporto Específico de Destino Final:", lista_aeroportos, index=index_destino, placeholder="Escolha o aeroporto de destino...")
        
        if destino_sel == "Outro / Não listado":
            destino = st.text_input("Digite o Destino (Cidade - Sigla IATA):", placeholder="Ex: Joinville - SC (JOI)", value=st.session_state.get('destino_custom', ''))
        else:
            destino = destino_sel if destino_sel else ""

    tipo_conexao = st.radio("O voo foi direto ou teve conexões?", ["Voo Direto", "Teve Conexão(ões)"], horizontal=True)
    conexoes_info = ""
    aeroportos_conexao = ""
    if tipo_conexao == "Teve Conexão(ões)":
        aeroportos_conexao = st.text_input("Informe as cidades/aeroportos de conexão (Escalas):", placeholder="Ex: Conexão em Brasília (BSB)", value=st.session_state.get('aeroportos_conexao', ''))
        if aeroportos_conexao:
            conexoes_info = f"O trajeto incluiu conexões/escalas em {aeroportos_conexao}.\n\n"

    data_voo = st.date_input("Data do Voo:", max_value=date(2026, 7, 28), format="DD/MM/YYYY")

    if 'checked_nao_lembro' not in st.session_state:
        st.session_state.checked_nao_lembro = False
        
    pnr_input_val = st.session_state.get('pnr_input', '')
    if pnr_input_val and pnr_input_val != "PENDENTE_USUARIO":
        st.session_state.checked_nao_lembro = False

    col_v1, col_v2 = st.columns(2)
    aviso_pendente = st.session_state.checked_nao_lembro
    
    with col_v1:
        label_pnr = "⚠️ Código Localizador (PNR) - Pendente:" if aviso_pendente else "Código Localizador (PNR):"
        pnr = st.text_input(label_pnr, max_chars=6, placeholder="Ex: XYZ123", key="pnr_input").upper()
    with col_v2:
        num_voo = st.text_input("Identificação do Voo Principal (Opcional):", placeholder="Ex: G3 1409", key="num_voo_input")

    checked_atual = st.checkbox(
        "Não tenho o código PNR em mãos agora", 
        value=st.session_state.checked_nao_lembro
    )
    st.session_state.checked_nao_lembro = checked_atual
    if st.session_state.checked_nao_lembro:
        pnr = "PENDENTE_USUARIO"
        num_voo = ""
        st.info("💡 Tudo bem! Você poderá atualizar esse dado posteriormente com o suporte ou na petição.")

    st.markdown("---")
    st.markdown("### Seus Dados")
    
    nome = st.text_input("Nome Completo:", placeholder="Digite seu nome completo", value=st.session_state.get('nome', ''))
    email = st.text_input("E-mail para envio da Petição:", placeholder="seu@email.com", value=st.session_state.get('email', ''))
    
    index_estado = None
    if 'uf' in st.session_state and st.session_state.uf in ESTADOS:
        index_estado = ESTADOS.index(st.session_state.uf)
    uf = st.selectbox("Selecione seu Estado (UF) para protocolo:", ESTADOS, index=index_estado, placeholder="Selecione o estado (UF)...")
    
    endereco = st.text_input("Endereço Residencial Completo:", placeholder="Rua, Número, Bairro, Cidade - CEP", value=st.session_state.get('endereco', ''))
    
    cpf_input = st.text_input("CPF (Apenas os números):", max_chars=11, placeholder="00000000000", value=st.session_state.get('cpf', ''))
    
    st.markdown("<p style='font-size: 14px; color: #64748b; margin-top: -10px; margin-bottom: 15px;'><span style='color: #16a34a;'>🔒</span> Dados protegidos pela LGPD (Lei nº 13.709/18) e utilizados exclusivamente para esta petição.</p>", unsafe_allow_html=True)

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
            voltar_etapa(1)
    with col_b2:
        if st.button("Continuar para Pré-visualização ➡️", type="primary", use_container_width=True):
            origem_valida = origem.strip() if origem_sel == "Outro / Não listado" else origem
            destino_valida = destino.strip() if destino_sel == "Outro / Não listado" else destino
            cpf_limpo = re.sub(r'\D', '', cpf_input)

            if not origem_sel:
                st.error("Por favor, selecione o aeroporto de origem.")
            elif not destino_sel:
                st.error("Por favor, selecione o aeroporto de destino final.")
            elif not origem_valida or not destino_valida:
                st.error("Preencha os aeroportos de origem e destino.")
            elif origem_valida == destino_valida:
                st.error("A origem e o destino não podem ser iguais.")
            elif not st.session_state.checked_nao_lembro and len(pnr) != 6:
                st.error("Preencha o Código Localizador (PNR) com exatamente 6 dígitos, ou marque a opção de que não possui o código em mãos.")
            elif not prazo_valido:
                st.error(f"❌ Não é possível prosseguir. O prazo limite legal de {limite_texto} para requerer esta indenização já expirou.")
            elif len(nome.strip().split()) < 2:
                st.error("Por favor, insira seu nome completo (Nome e Sobrenome).")
            elif not email or "@" not in email or "." not in email:
                st.error("Por favor, insira um e-mail válido.")
            elif not uf:
                st.error("Por favor, selecione o Estado (UF) para protocolo.")
            elif not endereco:
                st.error("Por favor, preencha o seu endereço completo.")
            elif len(cpf_limpo) != 11:
                st.error("Por favor, insira um CPF válido com 11 dígitos numéricos.")
            else:
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
                st.session_state.aeroportos_conexao = aeroportos_conexao
                st.session_state.conexoes_info = conexoes_info
                st.session_state.nao_lembro_dados = st.session_state.checked_nao_lembro
                st.session_state.pnr = pnr
                st.session_state.num_voo = num_voo.strip()
                st.session_state.nome = nome.strip()
                st.session_state.primeiro_nome = nome.strip().split()[0]
                st.session_state.email = email.strip()
                st.session_state.uf = uf
                st.session_state.endereco = endereco
                st.session_state.cpf = cpf_limpo
                
                # --- GERAÇÃO DE ID E SALVAMENTO NO SUPABASE ---
                if 'id_pedido' not in st.session_state:
                    st.session_state.id_pedido = f"PED-{int(time.time())}-{cpf_limpo}"
                
                dados_db = {
                    "id": st.session_state.id_pedido,
                    "nome": st.session_state.nome,
                    "email": st.session_state.email,
                    "cpf": st.session_state.cpf,
                    "uf": st.session_state.uf,
                    "endereco": st.session_state.endereco,
                    "problema": st.session_state.problema,
                    "cia_simples": st.session_state.cia_simples,
                    "cia_completa": st.session_state.cia_completa,
                    "origem": st.session_state.origem,
                    "destino": st.session_state.destino,
                    "trecho": st.session_state.trecho,
                    "tipo_voo": st.session_state.tipo_voo,
                    "data_voo_br": st.session_state.data_voo_br,
                    "conexoes_info": st.session_state.conexoes_info,
                    "pnr": st.session_state.pnr,
                    "num_voo": st.session_state.num_voo,
                    "status": "pending"
                }

                if supabase:
                    try:
                        supabase.table("pedidos").upsert(dados_db).execute()
                    except Exception:
                        pass
                
                # --- INTEGRAÇÃO COM MAKE.COM (Webhook Inicial) ---
                webhook_url = "https://hook.us2.make.com/ypgqbrgk8l9hgevkzvo1pphjiyefwmsf"
                try:
                    requests.post(webhook_url, json=dados_db, timeout=5)
                except Exception:
                    pass
                # ------------------------------------------------
                
                avancar_etapa(3)

elif st.session_state.etapa == 3:
    if st.button("⬅️ Corrigir Dados"):
        voltar_etapa(2)

    primeiro_nome = st.session_state.get('primeiro_nome', 'Visitante')
    st.title("Pré-visualização da sua Petição")
    st.info(f"{primeiro_nome}, confira os dados estruturados abaixo. A fundamentação legal completa será liberada na finalização.")

    uf_extenso_preview = ESTADOS_TEXTO.get(st.session_state.uf, f"DO ESTADO DE {st.session_state.uf}")
    pnr_val = st.session_state.pnr
    pnr_html = f'<span style="color: red;">{pnr_val}</span>' if pnr_val == "PENDENTE_USUARIO" else pnr_val
    num_voo_val = st.session_state.get('num_voo', '')
    num_voo_html = f" (Voo {num_voo_val})" if num_voo_val else ""
    cpf_formatado = formatar_cpf(st.session_state.get('cpf', ''))
    
    trecho_fatos_preview = obter_texto_fatos(st.session_state.get('problema', 'Voo Atrasado (mais de 4h)'))

    st.markdown(f"""
    <div class="doc-container">
        <div class="doc-header">
            EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DO JUIZADO ESPECIAL CÍVEL DA COMARCA {uf_extenso_preview}
        </div>
        <p><b>REQUERENTE:</b> {st.session_state.nome.upper()}, portador(a) do CPF nº {cpf_formatado}, residente e domiciliado(a) em {st.session_state.endereco}. E-mail: {st.session_state.email}.</p>
        <p align="center"><b>AÇÃO DE INDENIZAÇÃO POR DANOS MORAIS E MATERIAIS</b></p>
        <p><b>REQUERIDO:</b> {st.session_state.cia_completa.upper()}, pessoa jurídica de direito privado...</p>
        <p><b>I - DOS FATOS</b><br>
        O(A) requerente adquiriu bilhetes aéreos sob o código localizador {pnr_html}{num_voo_html}, para o trecho entre {st.session_state.trecho} ({st.session_state.tipo_voo}), com data marcada para {st.session_state.data_voo_br}. {trecho_fatos_preview}</p>
        <p><b>II - DO DIREITO</b></p>
        <p class="blur-text">
        A relação jurídica submete-se às regras do Código de Defesa do Consumidor. A responsabilidade da companhia aérea é objetiva nos termos do artigo 14 da Lei 8078/90. O dano moral ocorre in re ipsa configurando quebra das resoluções da ANAC aplicáveis à espécie e jurisprudência pacífica do STJ.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("⬅️ Voltar para Edição", use_container_width=True):
            voltar_etapa(2)
    with col_b2:
        if st.button("Continuar para Finalização", type="primary", use_container_width=True):
            if st.session_state.pnr == "PENDENTE_USUARIO":
                aviso_pendencia()
            else:
                avancar_etapa(4)

elif st.session_state.etapa == 4:
    if st.button("⬅️ Voltar para Visualização"):
        voltar_etapa(3)
        
    st.title("Liberação do seu Documento")

    if 'pagamento_aprovado' not in st.session_state:
        st.session_state.pagamento_aprovado = False

    sdk = mercadopago.SDK("APP_USR-1689026143657988-072919-e2bdce9cb1761b0cf1a4298c53034a33-188311197")

    if not st.session_state.pagamento_aprovado:
        st.markdown("""
        <div class="highlight-box">
            <h3 style="margin-top: 0; margin-bottom: 10px; font-size: 18px; font-weight: 700;">Maximize o valor da sua indenização</h3>
            <p style="margin: 0; font-size: 14px; line-height: 1.5;">Advogados costumam cobrar até 30% do valor final. Com a petição estruturada com os fundamentos corretos, você mesmo faz o protocolo online em poucos minutos. Ações bem fundamentadas no Juizado Especial possuem um alto índice de acordos e procedência favorável ao consumidor, sem complicação.</p>
        </div>
        """, unsafe_allow_html=True)

        if 'link_pagamento' not in st.session_state:
            if 'id_pedido' not in st.session_state:
                st.session_state.id_pedido = f"PED-{int(time.time())}-{st.session_state.cpf}"
                
            preference_data = {
                "items": [
                    {
                        "title": "Petição Indenização Voo",
                        "quantity": 1,
                        "unit_price": 1.00
                    }
                ],
                "back_urls": {
                    "success": "https://resolfix.com.br",
                    "failure": "https://resolfix.com.br",
                    "pending": "https://resolfix.com.br"
                },
                "auto_return": "approved",
                "external_reference": st.session_state.id_pedido
            }
            
            resposta = sdk.preference().create(preference_data)
            st.session_state.link_pagamento = resposta["response"]["init_point"]
        
        st.link_button(
            "Pagar com PIX ou Cartão (Liberar Petição)", 
            st.session_state.link_pagamento, 
            type="primary", 
            use_container_width=True
        )

        st.markdown("---")
        st.info("🔄 **Aguardando confirmação do pagamento...** Assim que o PIX ou cartão for compensado, esta página atualizará automaticamente.")

        col_btest1, col_btest2 = st.columns(2)
        with col_btest1:
            if st.button("⚡ Simular Pagamento Aprovado (Bypass de Teste)"):
                st.session_state.pagamento_aprovado = True
                st.rerun()

        # --- POLLING AUTOMÁTICO PARA RECONHECER O PIX SEM RECARREGAR ---
        try:
            busca = sdk.payment().search({"external_reference": st.session_state.id_pedido})
            pagamentos = busca.get("response", {}).get("results", [])
            if any(p.get("status") == "approved" for p in pagamentos):
                st.session_state.pagamento_aprovado = True
                st.rerun()
        except Exception:
            pass

        time.sleep(5)
        st.rerun()
        # -------------------------------------------------------------

    else:
        # --- INÍCIO DA SINCRONIZAÇÃO DE ABAS (FRONTEND) ---
        st.markdown("""
        <script>
        const bc = new BroadcastChannel('resolfix_payment');
        const urlParams = new URLSearchParams(window.location.search);
        
        if (urlParams.has('status') || urlParams.has('collection_status')) {
            bc.postMessage('fechar_aba_duplicada');
        }
        
        bc.onmessage = (event) => {
            if (event.data === 'fechar_aba_duplicada' && !urlParams.has('status') && !urlParams.has('collection_status')) {
                document.body.innerHTML = "<div style='display:flex; height:100vh; align-items:center; justify-content:center; font-family:sans-serif; background:#f0f2f6; text-align:center; padding:20px;'><div style='background:white; padding:40px; border-radius:10px; box-shadow:0 4px 6px rgba(0,0,0,0.1);'><h2 style='color:#16a34a;'>Pagamento Concluído! 🎉</h2><p style='color:#64748b;'>O processo de sucesso está sendo exibido na aba que se abriu.<br>Você já pode fechar esta tela original com segurança.</p></div></div>";
            }
        };
        </script>
        """, unsafe_allow_html=True)
        # --- FIM DA SINCRONIZAÇÃO DE ABAS ---

        st.success("🎉 Pagamento Confirmado com Sucesso!")
        st.info(f"Uma cópia de segurança da sua petição também foi encaminhada para o e-mail cadastrado: **{st.session_state.email}**.")

        cpf_formatado = formatar_cpf(st.session_state.get('cpf', ''))
        pdf_bytes = gerar_pdf(
            st.session_state.uf, 
            st.session_state.nome, 
            cpf_formatado,
            st.session_state.endereco, 
            st.session_state.cia_completa, 
            st.session_state.pnr,
            st.session_state.get('num_voo', ''),
            st.session_state.trecho, 
            st.session_state.data_voo_br, 
            st.session_state.tipo_voo,
            st.session_state.problema,
            st.session_state.get('conexoes_info', '')
        )

        # --- DISPARO AUTOMÁTICO DO PDF POR E-MAIL E TRAVA ATÔMICA ---
        if 'email_enviado' not in st.session_state:
            processar_webhook = True
            
            if supabase:
                resposta = supabase.table("pedidos").update({"status": "processed"}).eq("id", st.session_state.id_pedido).eq("status", "pending").execute()
                
                if len(resposta.data) == 0:
                    processar_webhook = False
                    
            if processar_webhook:
                webhook_email_url = "https://hook.us2.make.com/3jhvmkkpyfyhpallgj27r95gb4nka1o2"
                link_do_tribunal = LINKS_TJ.get(st.session_state.uf, "https://www.tjsp.jus.br")
                
                files = {'arquivo': (f"peticao_atraso_voo_{st.session_state.pnr}.pdf", pdf_bytes, 'application/pdf')}
                data = {
                    'email': st.session_state.email, 
                    'nome': st.session_state.nome,
                    'pnr': st.session_state.pnr,
                    'uf': st.session_state.uf,
                    'link_tj': link_do_tribunal
                }
                
                try:
                    requests.post(webhook_email_url, files=files, data=data, timeout=10)
                except Exception:
                    pass
                    
            st.session_state.email_enviado = True
        # -------------------------------------------------------------

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
        st.link_button(f"🔗 Protocolar Petição em Portal do TJ{st.session_state.uf}", link_do_tribunal)

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
    st.markdown("<p style='text-align: center; color: gray; font-size: 12px;'>© 2026 Resolfix - Indenização de Voos</p>", unsafe_allow_html=True)