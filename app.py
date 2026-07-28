import base64
from datetime import datetime
import io
from fpdf import FPDF
import streamlit as st
import streamlit.components.v1 as components

# Configuração da página
st.set_page_config(
    page_title="Indenização por Voo Atrasado ou Cancelado",
    page_icon="✈️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Injeção de CSS personalizado para correções visuais e mobile
st.markdown(
    """
    <style>
    /* Ocultar o texto em inglês 'Press Enter to apply' dos inputs */
    div[data-testid="InputInstructions"] {
        display: none !important;
    }
    
    /* Ajustes responsivos para fontes de títulos no mobile */
    @media (max-width: 768px) {
        h1 {
            font-size: 1.75rem !important;
            line-height: 1.2 !important;
        }
        h2 {
            font-size: 1.4rem !important;
            line-height: 1.2 !important;
        }
        h3 {
            font-size: 1.15rem !important;
        }
    }

    /* Correção de contraste e legibilidade nos cards de aviso claros */
    .card-aviso-claro {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2563eb;
        color: #1e293b !important;
    }
    .card-aviso-claro p, .card-aviso-claro li, .card-aviso-claro span {
        color: #1e293b !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# Função para rolar a página para o topo automaticamente a cada mudança de etapa
def scroll_to_top():
    components.html(
        """
        <script>
            window.parent.window.scrollTo({top: 0, behavior: 'instant'});
        </script>
        """,
        height=0,
    )


# Inicialização do estado de navegação
if "step" not in st.session_state:
    st.session_state.step = 1

# Disparar rolagem ao mudar de etapa
scroll_to_top()


# Função para gerar o PDF da Petição
def gerar_pdf(dados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Configuração de fonte padrão (compatível com FPDF básico)
    pdf.set_font("Times", "B", 14)

    # Cabeçalho da Petição
    uf = dados.get("uf", "SP")
    pdf.multi_cell(
        0,
        8,
        f"EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DO JUIZADO ESPECIAL CÍVEL DA COMARCA DO ESTADO DO(A) {uf}",
        align="C",
    )
    pdf.ln(10)

    pdf.set_font("Times", "", 12)
    requerente = f"REQUERENTE: {dados.get('nome', '')}, portador(a) do CPF nº {dados.get('cpf', '')}, residente e domiciliado(a) em {dados.get('endereco', '')}. E-mail: {dados.get('email', '')}."
    pdf.multi_cell(0, 6, requerente)
    pdf.ln(5)

    pdf.set_font("Times", "B", 12)
    pdf.multi_cell(0, 6, "AÇÃO DE INDENIZAÇÃO POR DANOS MATERIAIS E MORAIS", align="C")
    pdf.ln(10)

    pdf.set_font("Times", "", 12)
    corpo = (
        f"O(A) Requerente vem, respeitosamente, perante Vossa Excelência, propor a presente AÇÃO DE "
        f"INDENIZAÇÃO em face de EMPRESA AÉREA, com base no Código de Defesa do Consumidor e na "
        f"Resolução nº 400 da ANAC, em decorrência de falha na prestação de serviço de transporte aéreo "
        f"referente ao voo com localizador (PNR): {dados.get('pnr', '')} na rota {dados.get('origem', '')} para {dados.get('destino', '')}."
    )
    pdf.multi_cell(0, 6, corpo)
    pdf.ln(10)

    # Fechamento
    pdf.multi_cell(
        0,
        6,
        "Termos em que,\nPede e espera deferimento.\n\nLocal e Data, ____/____/________.",
    )
    pdf.ln(15)
    pdf.cell(0, 6, "_" * 40, ln=True, align="C")
    pdf.cell(0, 6, "Assinatura do Requerente", align="C")

    return pdf.output(dest="S").encode("latin1")


# ==========================================
# ETAPA 1: APRESENTAÇÃO E DADOS BÁSICOS
# ==========================================
if st.session_state.step == 1:
    # Hero section corrigida sem espaçamento desnecessário
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 25px; border-radius: 15px; color: white; margin-bottom: 20px;">
            <div style="background-color: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; padding: 5px 12px; border-radius: 20px; display: inline-block; font-size: 0.8rem; margin-bottom: 12px; color: #34d399; font-weight: 600;">
                VERIFICAÇÃO RÁPIDA E SEM RISCOS
            </div>
            <h1 style="color: white; font-size: 1.8rem; margin-bottom: 8px;">Voo atrasado ou cancelado?</h1>
            <h2 style="color: #93c5fd; font-size: 1.4rem; margin-top: 0px; margin-bottom: 12px;">Receba até R$ 10.000!</h2>
            <p style="color: #cbd5e1; font-size: 0.95rem; margin: 0;">Você tem direitos garantidos por lei. Nós cuidamos de toda a burocracia para você ser compensado de forma rápida.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("O que deu errado com o seu voo?")
    problema = st.radio(
        "Selecione o problema:",
        [
            "Voo Atrasado (mais de 3h)",
            "Voo Cancelado",
            "Perda de Conexão / Outros",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.subheader("Seus Dados Cadastrais")

    nome = st.text_input("Nome Completo:", placeholder="Seu nome completo")
    cpf = st.text_input(
        "CPF (Formato: 000.000.000-00):", placeholder="000.000.000-00"
    )
    email = st.text_input(
        "E-mail para envio da Petição:", placeholder="seu@email.com"
    )

    col1, col2 = st.columns([1, 1])
    with col2:
        if st.button("Avançar ➔", type="primary", use_container_width=True):
            if not nome or not cpf or not email:
                st.error("Por favor, preencha todos os campos obrigatórios.")
            else:
                st.session_state.dados = {
                    "problema": problema,
                    "nome": nome,
                    "cpf": cpf,
                    "email": email,
                }
                st.session_state.step = 2
                st.rerun()

# ==========================================
# ETAPA 2: DETALHES DA ROTA E DO VOO
# ==========================================
elif st.session_state.step == 2:
    st.header("Detalhes da Rota e do Voo")

    endereco = st.text_input(
        "Endereço Residencial Completo:",
        placeholder="Rua, Número, Bairro, Cidade - CEP",
    )
    uf = st.selectbox(
        "Selecione seu Estado (UF) para protocolo:",
        [
            "AC",
            "AL",
            "AP",
            "AM",
            "BA",
            "CE",
            "DF",
            "ES",
            "GO",
            "MA",
            "MT",
            "MS",
            "MG",
            "PA",
            "PB",
            "PR",
            "PE",
            "PI",
            "RJ",
            "RN",
            "RS",
            "RO",
            "RR",
            "SC",
            "SP",
            "SE",
            "TO",
        ],
    )

    tipo_voo = st.radio(
        "Tipo de Voo:", ["Nacional", "Internacional"], horizontal=True
    )

    origem = st.text_input(
        "Aeroporto Específico de Origem:",
        placeholder="Ex: São Paulo - Congonhas (CGH)",
    )
    destino = st.text_input(
        "Aeroporto Específico de Destino Final:",
        placeholder="Ex: São Paulo - Guarulhos (GRU)",
    )

    conexoes = st.radio(
        "O voo foi direto ou teve conexões?",
        ["Sim, foi um voo direto", "Não, teve no mínimo 1 conexão"],
    )

    pnr = st.text_input(
        "Código Localizador (PNR):", placeholder="Ex: ABC123ou 6 caracteres"
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅ Voltar", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("Gerar Pré-visualização ➔", type="primary", use_container_width=True):
            if not endereco or not origem or not destino or not pnr:
                st.error("Preencha todos os campos da rota e o localizador.")
            else:
                st.session_state.dados.update(
                    {
                        "endereco": endereco,
                        "uf": uf,
                        "tipo_voo": tipo_voo,
                        "origem": origem,
                        "destino": destino,
                        "conexoes": conexoes,
                        "pnr": pnr,
                    }
                )
                st.session_state.step = 3
                st.rerun()

# ==========================================
# ETAPA 3: PRÉ-VISUALIZAÇÃO DA PETIÇÃO
# ==========================================
elif st.session_state.step == 3:
    st.header("Pré-visualização da sua Petição")

    st.markdown(
        """
        <div class="card-aviso-claro">
            <b>Confira os dados estruturados abaixo.</b> A fundamentação legal completa será liberada na finalização.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # Exibição simulada do documento formatado
    dados = st.session_state.dados
    texto_preview = f"""
    ### EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DO JUIZADO ESPECIAL CÍVEL DA COMARCA DO ESTADO DO(A) {dados.get('uf')}

    **REQUERENTE:** {dados.get('nome')}, portador(a) do CPF nº {dados.get('cpf')}, residente e domiciliado(a) em {dados.get('endereco')}. E-mail: {dados.get('email')}.

    **AÇÃO DE INDENIZAÇÃO POR DANOS MATERIAIS E MORAIS** em face de EMPRESA AÉREA, referente ao voo (PNR: {dados.get('pnr')}) na rota {dados.get('origem')} para {dados.get('destino')}.
    """
    st.info(texto_preview)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅ Corrigir Dados", use_container_width=True):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("Prosseguir para Liberação ➔", type="primary", use_container_width=True):
            st.session_state.step = 4
            st.rerun()

# ==========================================
# ETAPA 4: LIBERAÇÃO DO DOCUMENTO (PAGAMENTO)
# ==========================================
elif st.session_state.step == 4:
    st.header("Liberação do seu Documento")

    # Card com contraste corrigido para legibilidade perfeita
    st.markdown(
        """
        <div class="card-aviso-claro">
            <span style="font-size: 1.3rem;">⚠️</span> <b>Não gaste 30% da sua indenização com terceiros!</b><br><br>
            Advogados convencionais ou plataformas intermediárias cobram até 1/3 do valor que você ganhar no tribunal.<br><br>
            Por um valor fixo, você baixa a sua petição pronta e recebe o roteiro exato para exigir seus direitos sozinho.<br><br>
            <h3 style="color: #2563eb; margin-top: 10px; margin-bottom: 0;">Apenas R$ 56,90</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅ Voltar para Visualização", use_container_width=True):
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("Liberar Documento por R$ 56,90", type="primary", use_container_width=True):
            st.session_state.step = 5
            st.rerun()

# ==========================================
# ETAPA 5: DOWNLOAD DO PDF
# ==========================================
elif st.session_state.step == 5:
    st.header("Documento Pronto para Download!")

    st.success(
        "Pagamento simulado/confirmado com sucesso! Sua petição personalizada foi gerada com base na legislação vigente."
    )

    pdf_bytes = gerar_pdf(st.session_state.dados)

    st.download_button(
        label="📥 Baixar Petição Inicial em PDF",
        data=pdf_bytes,
        file_name=f"peticao_indenizacao_{st.session_state.dados.get('cpf', 'cliente')}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Criar Nova Petição", use_container_width=True):
        st.session_state.clear()
        st.session_state.step = 1
        st.rerun()
