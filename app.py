import streamlit as st
import time
import re
from datetime import date
from fpdf import FPDF
import streamlit.components.v1 as components

# Configuração da página
st.set_page_config(
    page_title="Resolfix - Indenização de Voos",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- ESTILIZAÇÃO CSS (Mobile Otimizado + Botões Flutuantes Duplos Compactos) ---
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

    /* Botão Flutuante: Voltar ao Topo (Compacto - Esquerda) */
    .back-to-top {
        position: fixed;
        bottom: 15px;
        left: 15px;
        z-index: 9999;
        background-color: #1E3A8A;
        color: white !important;
        padding: 6px 10px;
        border-radius: 20px;
        text-decoration: none !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        font-size: 11px;
        font-weight: bold;
    }
    .back-to-top:hover {
        background-color: #2563EB;
        color: white !important;
    }

    /* Botão Flutuante: WhatsApp (Compacto - Direita) */
    .whatsapp-float {
        position: fixed;
        bottom: 15px;
        right: 15px;
        z-index: 9999;
        background-color: #25D366;
        color: white !important;
        padding: 6px 10px;
        border-radius: 20px;
        text-decoration: none !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        font-size: 11px;
        font-weight: bold;
    }
    .whatsapp-float:hover {
        background-color: #20ba5a;
        color: white !important;
    }

    @media (max-width: 768px) {
        h1 { font-size: 1.75rem !important; line-height: 1.2 !important; }
        h2 { font-size: 1.4rem !important; line-height: 1.2 !important; }
    }
</style>

<!-- Âncora do Topo -->
<div id="top-anchor"></div>
""", unsafe_allow_html=True)

def scroll_to_top():
    components.html(
        """
        <script>
            window.parent.scrollTo({top: 0, behavior: 'smooth'});
        </script>
        """,
        height=0,
    )

LINKS_TJ = {
    "AC": "https://www.tjac.jus.br", "AL": "https://www.tjal.jus.br", "AP": "https://www.tjap.jus.br",
    "AM": "https://www.tjam.jus.br", "BA": "https://www.tjba.jus.br", "CE": "https://www.tjce.jus.br",
    "DF": "https://www.tjdft.jus.br", "ES": "https://www.tjes.jus.br", "GO": "https://www.tjgo.jus.br",
    "MA": "https://www.tjma.jus.br", "MT": "https://www.tjmt.jus.br", "MS": "https://www.tjms.jus.br",
    "MG": "https://www.tjmg.jus.br", "PA": "https://www.tjpa.jus.br", "PB": "https://www.tjpb.jus.br",
    "PR": "https://www.tjpr.jus.br", "PE": "https://www.tjpe.jus.br", "PI": "https://www.tjpi.jus.br",
    "RJ": "https://www.tjrj.jus.br", "RN": "https://www.tjrn.jus.br", "RS": "https://www.tjrs.jus.br",
    "RO": "https://www.tjro.jus.br", "RR": "https://www.tjrr.jus.br", "SE": "https://www.tjse.jus.br",
    "SC": "https://www.tjsc.jus.br", "SP": "https://www.tjsp.jus.br", "TO": "https://www.tjto.jus.br"
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
    "São Paulo Congonhas (CGH)", "São Paulo Guarulhos (GRU)",
    "Viracopos / Campinas (VCP)", "Rio de Janeiro Santos Dumont (SDU)",
    "Rio de Janeiro Galeão (GIG)", "Belo Horizonte Confins (CNF)",
    "Brasília Presidente Juscelino Kubitschek (BSB)", "Salvador Deputado Luís Eduardo Magalhães (SSA)",
    "Fortaleza Pinto Martins (FOR)", "Recife Guararapes (REC)",
    "Curitiba Afonso Pena (CWB)", "Porto Alegre Salgado Filho (POA)",
    "Goiânia Santa Genoveva (GYN)", "Florianópolis Hercílio Luz (FLN)",
    "Vitória Eurico de Aguiar Salles (VIX)", "Manaus Eduardo Gomes (MAO)",
    "Belém Val-de-Cans (BEL)", "Cuiabá Marechal Rondon (CGB)",
    "Campo Grande (CGR)", "Maceió Zumbi dos Palmares (MCZ)",
    "Aracaju Santa Maria (AJU)", "Natal Governador Aluízio Alves (NAT)",
    "João Pessoa Presidente Castro Pinto (JPA)", "São Luís Marechal Cunha Machado (SLZ)",
    "Teresina Senador Petrônio Portella (THE)", "Palmas Lysias Rodrigues (PMW)",
    "Porto Velho Governador Jorge Teixeira (PVH)", "Rio Branco Plácido de Castro (RBR)",
    "Macapá Alberto Alcolumbre (MCP)", "Boa Vista Atlas Brasil Cantanhede (BVB)",
    "Outro / Não listado"
]

AEROPORTOS_INTERNACIONAIS = AEROPORTOS_NACIONAIS[:-1] + [
    "Portugal Lisboa (LIS)", "Portugal Porto (OPO)",
    "Estados Unidos Miami (MIA)", "Estados Unidos Nova York (JFK)",
    "Estados Unidos Orlando (MCO)", "Argentina Buenos Aires (EZE)",
    "França Paris (CDG)", "Espanha Madri (MAD)", "Chile Santiago (SCL)",
    "Itália Roma (FCO)", "Outro / Não listado"
]

def formatar_cpf(cpf_string):
    cpf_numeros = re.sub(r'\D', '', cpf_string)
    if len(cpf_numeros) == 11:
        return f"{cpf_numeros[:3]}.{cpf_numeros[3:6]}.{cpf_numeros[6:9]}-{cpf_numeros[9:]}"
    return cpf_string

def gerar_pdf(uf, nome, cpf, endereco, cia_completa, pnr, num_voo, trecho, data_voo_br, tipo_voo, problema):
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
    
    fatos = (f"O(A) requerente adquiriu bilhetes aéreos sob o {pnr_str}{trecho_voo_str}, para o trecho entre {trecho} ({tipo_voo}), com data prevista para o voo em {data_voo_br}.\n\n"
             f"Ocorre que, na data aprazada, a empresa requerida falhou na prestação do serviço contratado, incorrendo em {problema.lower()} da viagem, sem prestar a devida assistência material, em afronta direta às normativas aplicáveis.\n\n"
             f"Tal falha causou severos transtornos, angústia e abalo emocional ao(à) requerente, que teve sua rotina abruptamente desorganizada por ato exclusivo da companhia aérea.")
    pdf.multi_cell(0, 5, txt(fatos), align="J")
    pdf.ln(4)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.multi_cell(0, 5, txt("II - DO DIREITO"), align="L")
    pdf.set_font("Arial", '', 10)
    direito = ("A relação jurídica estabelecida submete-se às regras protetivas do Código de Defesa do Consumidor (Lei nº 8.078/90) e legislação complementar aplicável à espécie. A responsabilidade da companhia aérea é objetiva, respondendo pelos danos casados aos consumidores independentemente da existência de culpa, nos termos do art. 14 do referido diploma legal.\n\n"
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
               "Dá-se à causa o valor de R$ 10.000,00.\n\n"
               "Termos em que,\nPede deferimento.\n\n"
               f"{uf}, {data_voo_br}.\n\n{nome.upper()}")
    pdf.multi_cell(0, 5, txt(pedidos), align="J")
    return bytes(pdf.output(dest='S'), encoding='latin-1')

@st.dialog("Termos e Condições de Uso")
def mostrar_termos():
    st.markdown("""
    ### 1. Objeto da Plataforma
    Este sistema tem caráter estritamente instrumental, auxiliando o usuário na formatação autônoma de documentos para protocolo no Juizado Especial Cível (JEC).
    ### 2. Autonomia do Usuário
    O usuário é integralmente responsável pelas informações fornecidas e pelo protocolo da petição perante o Tribunal competente.
    ### 3. Responsabilidade sobre Prazos
    Cabe ao usuário a conferência das datas e limites legais de prescrição aplicáveis ao seu caso específico.
    """)
    if st.button("Fechar", use_container_width=True):
        st.rerun()

@st.dialog("Política de Privacidade")
def mostrar_privacidade():
    st.markdown("""
    ### 1. Coleta de Dados
    Coletamos apenas os dados essenciais estritamente necessários para preenchimento da petição inicial e envio de comunicações transacionais.
    ### 2. Armazenamento e Segurança
    Os dados informados são processados em memória de sessão e não são comercializados ou compartilhados com terceiros para fins publicitários.
    ### 3. Conformidade
    Tratamento de dados alinhado aos princípios da Lei Geral de Proteção de Dados (LGPD Lei nº 13.709/2018).
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
        <div style="background: white; color: #1e293b; padding: 35px 45px; border-radius: 16px; box-shadow: 0 20px 25px 5px rgba(0, 0, 0, 0.3); text-align: center; max-width: 400px; width: 90%;">
            <div style="border: 4px solid #f3f3f3; border-top: 4px solid #16a34a; border-radius: 50%; width: 45px; height: 45px; animation: spin 1s linear infinite; margin: 0 auto 20px auto;"></div>
            <h3 style="margin: 0 0 10px 0; font-size: 19px; font-weight: 700; color: #1e293b;">Processando dados...</h3>
            <p style="margin: 0; font-size: 14px; color: #64748b; line-height: 1.4;">Analisando parâmetros regulatórios e estruturando documento jurídico.</p>
        </div>
    </div>
    <style>
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
    """, unsafe_allow_html=True)
    time.sleep(1.5)
    st.session_state.etapa = st.session_state.target_etapa
    scroll_to_top()
    st.rerun()

elif st.session_state.etapa == 1:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 35px; border-radius: 16px; color: white; margin-bottom: 20px;">
        <span style="background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); font-weight: 600; padding: 5px 12px; border-radius: 20px; text-transform: uppercase; display: inline-flex; align-items: center; gap: 6px; font-size: 11px;">
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
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### Seus Dados Cadastrais")
    nome = st.text_input("Nome Completo:", placeholder="Digite seu nome completo", value=st.session_state.get('nome', ''))
    email = st.text_input("E-mail para envio da Petição:", placeholder="seu@email.com", value=st.session_state.get('email', ''))
    
    index_cia = None
    if 'cia_simples' in st.session_state and st.session_state.cia_simples in CIAS_SIMPLES:
        index_cia = CIAS_SIMPLES.index(st.session_state.cia_simples)
        
    cia_selecionada = st.selectbox("Companhia Aérea Responsável:", CIAS_SIMPLES, index=index_cia, placeholder="Selecione a companhia aérea...")
    
    st.markdown("")
    if st.button("Descubra o quanto pode ganhar ➔", type="primary", use_container_width=True):
        if len(nome.strip().split()) < 2:
            st.error("Por favor, insira seu nome completo (Nome e Sobrenome).")
        elif not email or "@" not in email or "." not in email:
            st.error("Por favor, insira um e-mail válido.")
        elif not cia_selecionada:
            st.error("Por favor, selecione a companhia aérea responsável.")
        else:
            st.session_state.problema = problema_escolhido
            st.session_state.nome = nome.strip()
            st.session_state.primeiro_nome = nome.strip().split()[0]
            st.session_state.email = email.strip()
            st.session_state.cia_simples = cia_selecionada
            st.session_state.cia_completa = CIAS_MAPPING[cia_selecionada]
            ir_para_etapa(2)

elif st.session_state.etapa == 2:
    primeiro_nome = st.session_state.get('primeiro_nome', 'Visitante')
    st.title(f"Agora, {primeiro_nome}, precisamos dos detalhes da sua rota")
    
    endereco = st.text_input("Endereço Residencial Completo:", placeholder="Rua, Número, Bairro, Cidade - UF, CEP", value=st.session_state.get('endereco', ''))
    cpf_input = st.text_input("CPF (Formato: 000.000.000-00):", max_chars=14, placeholder="000.000.000-00", value=st.session_state.get('cpf', ''))
    
    index_estado = None
    if 'uf' in st.session_state and st.session_state.uf in ESTADOS:
        index_estado = ESTADOS.index(st.session_state.uf)
    uf = st.selectbox("Selecione seu Estado (UF) para protocolo:", ESTADOS, index=index_estado, placeholder="Selecione o estado (UF)...")
    
    tipo_voo = st.radio("Tipo de Voo:", ["Nacional", "Internacional"], horizontal=True, index=0 if st.session_state.get('tipo_voo', 'Nacional') == 'Nacional' else 1)
    lista_aeroportos = AEROPORTOS_NACIONAIS if tipo_voo == "Nacional" else AEROPORTOS_INTERNACIONAIS
    
    col1, col2 = st.columns(2)
    with col1:
        index_origem = None
        if 'origem_sel' in st.session_state and st.session_state.get('origem_sel') in lista_aeroportos:
            index_origem = lista_aeroportos.index(st.session_state.get('origem_sel'))
        origem_sel = st.selectbox("Aeroporto Específico de Origem:", lista_aeroportos, index=index_origem, placeholder="Escolha o aeroporto de origem...")
        if origem_sel == "Outro / Não listado":
            origem = st.text_input("Digite a Origem (Cidade Sigla IATA):", placeholder="Ex: Ribeirão Preto SP (RAO)", value=st.session_state.get('origem_custom', ''))
        else:
            origem = origem_sel if origem_sel else ""
            
    with col2:
        index_destino = None
        if 'destino_sel' in st.session_state and st.session_state.get('destino_sel') in lista_aeroportos:
            index_destino = lista_aeroportos.index(st.session_state.get('destino_sel'))
        destino_sel = st.selectbox("Aeroporto Específico de Destino Final:", lista_aeroportos, index=index_destino, placeholder="Escolha o aeroporto de destino...")
        if destino_sel == "Outro / Não listado":
            destino = st.text_input("Digite o Destino (Cidade Sigla IATA):", placeholder="Ex: Joinville SC (JOI)", value=st.session_state.get('destino_custom', ''))
        else:
            destino = destino_sel if destino_sel else ""

    if 'checked_nao_lembro' not in st.session_state:
        st.session_state.checked_nao_lembro = False
        
  
