import streamlit as st
import time
import re
from datetime import date
from fpdf import FPDF

# Configuração da página e remoção do espaço em branco superior
st.set_page_config(page_title="Indenização de Voos", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Remove o cabeçalho nativo e ajusta o topo para eliminar o espaço em branco */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 750px;
    }
    
    /* Força os botões primários do Streamlit para Azul Corporativo */
    div.stButton > button[kind="primary"] {
        background-color: #2563eb !important;
        border-color: #2563eb !important;
        color: white !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #1d4ed8 !important;
        border-color: #1d4ed8 !important;
    }

    /* Animação de pulso mais evidente */
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
        border-left: 5px solid #2563eb;
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .whatsapp-float {
        position: fixed;
        bottom: 25px;
        right: 25px;
        background-color: #25d366;
        color: white !important;
        padding: 12px 20px;
        border-radius: 50px;
        text-align: center;
        font-size: 14px;
        font-weight: bold;
        box-shadow: 2px 4px 10px rgba(0,0,0,0.25);
        z-index: 99999;
        text-decoration: none !important;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .whatsapp-float:hover {
        background-color: #128c7e !important;
        color: white !important;
        text-decoration: none !important;
    }
    </style>

    <a href="https://wa.me/556281096811?text=Ol%C3%A1,%20estou%20no%20site%20e%20preciso%20de%20ajuda%20com%20a%20minha%20peti%C3%A7%C3%A3o%20de%20voo." target="_blank" class="whatsapp-float">
        Suporte WhatsApp
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

CIAS_MAPPING = {
    "LATAM": "LATAM Airlines Brasil",
    "GOL": "GOL Linhas Aéreas S.A.",
    "Azul": "Azul Linhas Aéreas Brasileiras S.A.",
    "Voepass": "Voepass Linhas Aéreas",
    "TAP": "TAP Air Portugal",
    "American Airlines": "American Airlines Inc.",
    "United Airlines": "United Airlines Inc.",
    "Delta": "Delta Air Lines Inc.",
    "Copa Airlines": "Compañía Panameña de Aviación S.A.",
    "Air France": "Air France",
    "KLM": "KLM Royal Dutch Airlines",
    "Aerolíneas Argentinas": "Aerolíneas Argentinas S.A.",
    "Emirates": "Emirates Airlines",
    "Qatar": "Qatar Airways",
    "Outra": "Outra"
}
CIAS_SIMPLES = list(CIAS_MAPPING.keys())

AEROPORTOS_NACIONAIS = [
    "São Paulo - Congonhas (CGH)",
    "São Paulo - Guarulhos (GRU)",
    "São Paulo - Viracopos / Campinas (VCP)",
    "Rio de Janeiro - Santos Dumont (SDU)",
    "Rio de Janeiro - Galeão (GIG)",
    "Belo Horizonte - Confins (CNF)",
    "Brasília - Presidente Juscelino Kubitschek (BSB)",
    "Salvador - Deputado Luís Eduardo Magalhães (SSA)",
    "Fortaleza - Pinto Martins (FOR)",
    "Recife - Guararapes (REC)",
    "Curitiba - Afonso Pena (CWB)",
    "Porto Alegre - Salgado Filho (POA)",
    "Goiânia - Santa Genoveva (GYN)",
    "Florianópolis - Hercílio Luz (FLN)",
    "Vitória - Eurico de Aguiar Salles (VIX)",
    "Manaus - Eduardo Gomes (MAO)",
    "Belém - Val-de-Cans (BEL)",
    "Cuiabá - Marechal Rondon (CGB)",
    "Campo Grande (CGR)",
    "Maceió - Zumbi dos Palmares (MCZ)",
    "Aracaju - Santa Maria (AJU)",
    "Natal - Governador Aluízio Alves (NAT)",
    "João Pessoa - Presidente Castro Pinto (JPA)",
    "São Luís - Marechal Cunha Machado (SLZ)",
    "Teresina - Senador Petrônio Portella (THE)",
    "Palmas - Lysias Rodrigues (PMW)",
    "Porto Velho - Governador Jorge Teixeira (PVH)",
    "Rio Branco - Plácido de Castro (RBR)",
    "Macapá - Alberto Alcolumbre (MCP)",
    "Boa Vista - Atlas Brasil Cantanhede (BVB)",
    "Outro / Não listado"
]

AEROPORTOS_INTERNACIONAIS = AEROPORTOS_NACIONAIS[:-1] + [
    "Portugal - Lisboa (LIS)",
    "Portugal - Porto (OPO)",
    "Estados Unidos - Miami (MIA)",
    "Estados Unidos - Nova York (JFK)",
    "Estados Unidos - Orlando (MCO)",
    "Argentina - Buenos Aires (EZE)",
    "França - Paris (CDG)",
    "Espanha - Madri (MAD)",
    "Chile - Santiago (SCL)",
    "Itália - Roma (FCO)",
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

    pdf.set_font("Arial", 'B', 12)
    pdf.multi_cell(0, 6, txt(f"EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DO JUIZADO ESPECIAL CÍVEL DA COMARCA DO ESTADO DO(A) {uf}"), align="C")
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
    st.title("Processando...")
    status = st.empty()
    barra = st.progress(0)
    mensagens = ["Analisando elegibilidade do voo...", "Verificando parâmetros regulatórios...", "Estruturando documentação jurídica..."]
    for i in range(3):
        status.write(mensagens[i])
        barra.progress((i + 1) * 33)
        time.sleep(0.4)
    st.session_state.etapa = st.session_state.target_etapa
    st.rerun()

# --- ETAPA 1: CAPTAÇÃO BASEADA NA DOR (ESTILO PROFISSIONAL) ---
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
    
    col_n, col_c = st.columns(2)
    with col_n:
        nome = st.text_input("Nome Completo:", placeholder="Digite seu nome completo", value=st.session_state.get('nome', ''))
    with col_c:
        cpf_input = st.text_input("CPF (Formato: 000.000.000-00):", max_chars=14, placeholder="000.000.000-00", value=st.session_state.get('cpf', ''))
        
    email = st.text_input("E-mail para envio da Petição:", placeholder="seu@email.com", value=st.session_state.get('email', ''))
    
    index_cia = 0
    if 'cia_simples' in st.session_state and st.session_state.cia_simples in CIAS_SIMPLES:
        index_cia = CIAS_SIMPLES.index(st.session_state.cia_simples)
    cia_selecionada = st.selectbox("Companhia Aérea Responsável:", CIAS_SIMPLES, index=index_cia)
    
    st.markdown("")
    if st.button("Descubra o quanto pode ganhar ➡️", type="primary", use_container_width=True):
        if len(nome.strip().split()) < 2:
            st.error("Por favor, insira seu nome completo (Nome e Sobrenome).")
        elif len(re.sub(r'\D', '', cpf_input)) != 11:
            st.error("Por favor, insira um CPF válido com 11 dígitos.")
        elif not email or "@" not in email or "." not in email:
            st.error("Por favor, insira um e-mail válido.")
        else:
            st.session_state.problema = problema_escolhido
            st.session_state.nome = nome.strip()
            st.session_state.cpf = formatar_cpf(cpf_input)
            st.session_state.email = email.strip()
            st.session_state.cia_simples = cia_selecionada
            st.session_state.cia_completa = CIAS_MAPPING[cia_selecionada]
            ir_para_etapa(2)

# --- ETAPA 2: ROTA, CONEXÕES E DADOS DO VOO ---
elif st.session_state.etapa == 2:
    st.title("Detalhes da Rota e do Voo")
    
    endereco = st.text_input("Endereço Residencial Completo:", placeholder="Rua, Número, Bairro, Cidade - CEP", value=st.session_state.get('endereco', ''))
    
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
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        pnr = st.text_input("Código Localizador (PNR):", max_chars=6, placeholder="Ex: XYZ123", value=st.session_state.get('pnr', '')).upper()
    with col_v2:
        num_voo = st.text_input("Número do Voo Principal:", placeholder="Ex: G3 1409", value=st.session_state.get('num_voo', ''))
        
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
            
            if not endereco or len(pnr) != 6 or not num_voo or not origem_valida or not destino_valida:
                st.error("Preencha todos os campos obrigatórios, incluindo os nomes dos aeroportos personalizados se selecionados.")
            elif origem_valida == destino_valida:
                st.error("A origem e o destino não podem ser iguais.")
            elif not prazo_valido:
                st.error(f"❌ Não é possível prosseguir. O prazo limite legal de {limite_texto} para requerer esta indenização já expirou.")
            else:
                st.session_state.endereco = endereco
                st.session_state.uf = uf
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
            
    st.title("Pré-visualização da sua Petição")
    st.info("Confira os dados estruturados abaixo. A fundamentação legal completa será liberada na finalização.")
    
    st.markdown(f"""
    <div class="doc-container">
        <div class="doc-header">
            EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DO JUIZADO ESPECIAL CÍVEL DA COMARCA DO ESTADO DO(A) {st.session_state.uf}
        </div>
        <p><b>REQUERENTE:</b> {st.session_state.nome.upper()}, portador(a) do CPF nº {st.session_state.cpf}, residente e domiciliado(a) em {st.session_state.endereco}. E-mail: {st.session_state.email}.</p>
        <p align="center"><b>AÇÃO DE INDENIZAÇÃO POR DANOS MORAIS E MATERIAIS</b></p>
        <p><b>REQUERIDO:</b> {st.session_state.cia_completa.upper()}, pessoa jurídica de direito privado...</p>
        <p><b>I - DOS FATOS</b><br>
        O(A) requerente adquiriu bilhetes aéreos sob o código localizador {st.session_state.pnr} (Voo {st.session_state.num_voo}), para o trecho entre {st.session_state.trecho} ({st.session_state.tipo_voo}), com data marcada para {st.session_state.data_voo_br}. Incidente registrado: {st.session_state.problema}. Ocorre que a empresa falhou gravemente na prestação do serviço...</p>
        <p><b>II - DO DIREITO (Conteúdo Bloqueado)</b></p>
        <p class="blur-text">
        A relação jurídica submete-se às regras do Código de Defesa do Consumidor. A responsabilidade da companhia aérea é objetiva nos termos do artigo 14 da Lei 8078/90. O dano moral ocorre in re ipsa configurando quebra das resoluções da ANAC aplicáveis à espécie e jurisprudência pacífica do STJ.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    aceitou_termos = st.checkbox("Confirmo que revisei meus dados e que as informações do voo estão corretas.")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("⬅️ Voltar para Edição", use_container_width=True):
            ir_para_etapa(2)
    with col_b2:
        if st.button("Continuar para Finalização", type="primary", use_container_width=True):
            if aceitou_termos:
                ir_para_etapa(4)
            else:
                st.warning("Você precisa confirmar a exatidão dos dados para avançar.")

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
            <h3>⚠️ Não gaste 30% da sua indenização com terceiros!</h3>
            <p>Advogados convencionais ou plataformas intermediárias cobram até 1/3 do valor que você ganhar no tribunal.</p>
            <p>Por um valor fixo, você baixa a sua petição pronta e recebe o roteiro exato para exigir seus direitos sozinho.</p>
            <h2 style='color: #2563eb;'>Apenas R$ 56,90</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.link_button("Liberar Documento por R$ 56,90", "https://link-do-mercado-pago.com", type="primary", use_container_width=True)
        
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