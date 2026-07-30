import streamlit as st
import re
import streamlit.components.v1 as components

# Configuração da página
st.set_page_config(
    page_title="Resolfix - Notificação Extrajudicial de Voo",
    page_icon="✈️",
    layout="centered"
)

# --- ESTILIZAÇÃO CSS (Item 4: Mobile & Botões Flutuantes Compactos) ---
st.markdown("""
<style>
    /* Item 4: Ajuste de espaçamento específico para telas mobile */
    @media (max-width: 768px) {
        .hero-container {
            margin-bottom: 0px !important;
            padding-bottom: 5px !important;
        }
        .hero-title {
            font-size: 24px !important;
            line-height: 1.2 !important;
        }
    }

    /* Botão Flutuante: Voltar ao Topo (Compacto - Esquerda) */
    .back-to-top {
        position: fixed;
        bottom: 15px;
        left: 15px;
        z-index: 999;
        background-color: #1E3A8A;
        color: white;
        padding: 6px 10px;
        border-radius: 20px;
        text-decoration: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        font-size: 11px;
        font-weight: bold;
    }
    .back-to-top:hover {
        background-color: #2563EB;
        color: white;
    }

    /* Botão Flutuante: WhatsApp (Compacto - Direita) */
    .whatsapp-float {
        position: fixed;
        bottom: 15px;
        right: 15px;
        z-index: 999;
        background-color: #25D366;
        color: white;
        padding: 6px 10px;
        border-radius: 20px;
        text-decoration: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        font-size: 11px;
        font-weight: bold;
    }
    .whatsapp-float:hover {
        background-color: #20ba5a;
        color: white;
    }
</style>

<!-- Âncora do Topo -->
<div id="top-anchor"></div>
""", unsafe_allow_html=True)

# Função para rolar para o topo automaticamente
def scroll_to_top():
    components.html(
        """
        <script>
            window.parent.scrollTo({top: 0, behavior: 'smooth'});
        </script>
        """,
        height=0,
    )

# Inicialização do controle de etapas
if 'step' not in st.session_state:
    st.session_state.step = 1

# --- HERO SECTION (Com ajuste mobile - Item 4) ---
st.markdown("""
<div class="hero-container" style="background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%); padding: 30px; border-radius: 12px; color: white; margin-bottom: 25px;">
    <div style="background-color: rgba(16, 185, 129, 0.2); color: #34D399; padding: 4px 12px; border-radius: 20px; font-size: 12px; display: inline-block; font-weight: bold; margin-bottom: 12px;">
        VERIFICAÇÃO RÁPIDA E SEM RISCOS
    </div>
    <h1 class="hero-title" style="font-size: 28px; font-weight: bold; margin-bottom: 5px;">Voo atrasado ou cancelado?</h1>
    <div style="font-size: 24px; font-weight: bold; color: #60A5FA; margin-bottom: 12px;">Receba até R$ 10.000!</div>
    <p style="font-size: 14px; color: #E2E8F0; margin: 0;">Você tem direitos garantidos por lei. Nós cuidamos de toda a burocracia para você ser compensado de forma rápida.</p>
</div>
""", unsafe_allow_html=True)

# --- ETAPA 1: O PROBLEMA E CONEXÕES (Itens 5 e 6) ---
if st.session_state.step == 1:
    st.subheader("O que deu errado com o seu voo?")
    
    # Item 5: Alinhamento regulatório ANAC (4h)
    tipo_problema = st.radio(
        "Selecione o principal problema:",
        [
            "Voo Atrasado (mais de 4h ou perda de compromisso)",
            "Voo Cancelado",
            "Perda de Conexão / Outros"
        ],
        key="selected_problema"
    )

    st.markdown("---")
    
    # Item 6: Conexões dinâmicas
    st.subheader("Informações de Rota")
    teve_conexao = st.checkbox("O voo continha conexões ou escalas?")
    
    conexoes_lista = []
    if teve_conexao:
        st.info("Adicione os trechos das conexões abaixo:")
        num_conexoes = st.number_input("Quantas conexões/escalas houve?", min_value=1, max_value=4, value=1, step=1)
        
        for i in range(num_conexoes):
            col1, col2 = st.columns(2)
            with col1:
                origem_con = st.text_input(f"Origem/Escala {i+1}", key=f"orig_{i}")
            with col2:
                destino_con = st.text_input(f"Destino da Conexão {i+1}", key=f"dest_{i}")
            conexoes_lista.append({"trecho": i+1, "origem": origem_con, "destino": destino_con})

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Avançar para Dados do Voo ➔", type="primary", use_container_width=True):
        st.session_state.step = 2
        scroll_to_top()
        st.rerun()

# --- ETAPA 2: DADOS PESSOAIS E CPF (Item 2) ---
elif st.session_state.step == 2:
    st.subheader("Seus Dados Cadastrais")
    
    nome = st.text_input("Nome Completo do Passageiro")
    
    # Tratamento de CPF (Item 2)
    cpf_input = st.text_input("CPF (Apenas números)", max_chars=14, value=st.session_state.get('cpf_val', ''))
    
    numbers_only = re.sub(r'\D', '', cpf_input)[:11]
    if len(numbers_only) > 9:
        formatted_cpf = f"{numbers_only[:3]}.{numbers_only[3:6]}.{numbers_only[6:9]}-{numbers_only[9:]}"
    elif len(numbers_only) > 6:
        formatted_cpf = f"{numbers_only[:3]}.{numbers_only[3:6]}-{numbers_only[6:]}"
    elif len(numbers_only) > 3:
        formatted_cpf = f"{numbers_only[:3]}-{numbers_only[3:]}"
    else:
        formatted_cpf = numbers_only
        
    st.session_state.cpf_val = formatted_cpf

    # Aviso LGPD
    st.caption("🔒 Dados protegidos conforme a Lei Geral de Proteção de Dados (LGPD). Uso estrito para elaboração da notificação.")

    email = st.text_input("E-mail para receber a Notificação Pronta")
    whatsapp = st.text_input("WhatsApp com DDD")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Voltar", use_container_width=True):
            st.session_state.step = 1
            scroll_to_top()
            st.rerun()
    with col2:
        if st.button("Avançar para Relato ➔", type="primary", use_container_width=True):
            st.session_state.step = 3
            scroll_to_top()
            st.rerun()

# --- ETAPA 3: RELATO DE DANOS COM IA CONSULTIVA (Item 3) ---
elif st.session_state.step == 3:
    st.subheader("Conte os detalhes do que aconteceu")
    st.markdown("Descreva brevemente o que houve. Nossa **IA atua como advogada**, completando automaticamente o embasamento legal necessário.")

    relato = st.text_area("Relato livre:", placeholder="Ex: Fiquei mais de 5 horas esperando no aeroporto sem receber assistência e perdi minha reunião...")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Voltar", use_container_width=True):
            st.session_state.step = 2
            scroll_to_top()
            st.rerun()
    with col2:
        if st.button("Revisar e Pagar ➔", type="primary", use_container_width=True):
            st.session_state.step = 4
            scroll_to_top()
            st.rerun()

# --- ETAPA 4: PAGAMENTO MERCADO PAGO (Item 1) ---
elif st.session_state.step == 4:
    st.subheader("Resumo e Pagamento Seguro")
    
    st.markdown("""
    <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <h4 style="margin-top:0; color: #1E3A8A;">Elaboração de Notificação Extrajudicial de Voo - Resolfix</h4>
        <p style="margin-bottom: 5px; font-size: 14px; color: #475569;">Documento jurídico robusto formatado com base nas diretrizes da ANAC e jurisprudência nacional.</p>
        <hr style="border:0; border-top: 1px solid #E2E8F0; margin: 12px 0;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: bold; color: #334155;">Valor total:</span>
            <span style="font-size: 22px; font-weight: bold; color: #059669;">R$ 56,90</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Finalizar com Mercado Pago")
    st.info("Clique no botão abaixo para gerar o ambiente de pagamento seguro via Mercado Pago.")

    if st.button("Pagar R$ 56,90 com Mercado Pago", type="primary", use_container_width=True):
        st.success("Redirecionando para o ambiente seguro do Mercado Pago...")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Voltar e Editar Dados", use_container_width=True):
        st.session_state.step = 3
        scroll_to_top()
        st.rerun()

# --- BOTÕES FLUTUANTES (WhatsApp e Topo) ---
st.markdown("""
<a href="#top-anchor" class="back-to-top">⬆ Topo</a>
<a href="https://wa.me/5500000000000" target="_blank" class="whatsapp-float">💬 Suporte</a>
""", unsafe_allow_html=True)
