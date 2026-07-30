if 'etapa' not in st.session_state:
    st.session_state.etapa = 1
if 'target_etapa' not in st.session_state:
    st.session_state.target_etapa = 1

def ir_para_etapa(destino):
    st.session_state.target_etapa = destino
    st.session_state.etapa = "loading"
    st.rerun()

# Item 4: Popup de Aviso de Pendência
@st.dialog("⚠️ Atenção: Informação Pendente")
def aviso_pendencia():
    st.error("Você deixou o Código Localizador (PNR) como pendente.")
    st.write("Recomendamos que você retorne e preencha essa informação antes de prosseguir para o pagamento, pois a petição ficará incompleta e o juizado pode exigir esse dado posteriormente.")
    if st.button("Voltar e Preencher (Recomendado)", type="primary", use_container_width=True):
        ir_para_etapa(2)

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
    time.sleep(1.5)
    st.session_state.etapa = st.session_state.target_etapa
    st.markdown("<script>window.scrollTo({top: 0, behavior: 'smooth'});</script>", unsafe_allow_html=True)
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
                Direitos garantidos por lei para atrasos superiores a 4h ou cancelamentos. Nós cuidamos da burocracia.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### O que deu errado com o seu voo?")
    problema_escolhido = st.radio(
        "Selecione o incidente principal:",
        ["Voo Atrasado (mais de 4h)", "Voo Cancelado", "Perda de Conexão / Outros"],
        index=0 if st.session_state.get('problema') in [None, "Voo Atrasado (mais de 4h)"] else 0,
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
    if st.button("Descubra o quanto pode ganhar ➡️", type="primary", use_container_width=True):
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

    endereco = st.text_input("Endereço Residencial Completo:", placeholder="Rua, Número, Bairro, Cidade - CEP", value=st.session_state.get('endereco', ''))
    
    # Item 2: Restrito a 11 caracteres para o CPF
    cpf_input = st.text_input("CPF (Apenas os números):", max_chars=11, placeholder="00000000000", value=st.session_state.get('cpf', ''))
    
    st.markdown("<p style='font-size: 14px; color: #64748b; margin-top: -10px; margin-bottom: 15px;'><span style='color: #16a34a;'>🔒</span> Dados protegidos pela LGPD (Lei nº 13.709/18) e utilizados exclusivamente para esta petição.</p>", unsafe_allow_html=True)

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
        st.info(f"💡 Tudo bem, {primeiro_nome}! Você poderá atualizar esse dado posteriormente com o suporte ou na petição.")

    st.markdown("### Relato do Ocorrido")
    relato_danos = st.text_area(
        "Descreva brevemente o que aconteceu e os prejuízos sofridos (nossa IA completará o enquadramento jurídico padrão):",
        placeholder="Ex: Fiquei mais de 5 horas aguardando no aeroporto sem receber voucher de alimentação ou hotel...",
        value=st.session_state.get('relato_danos', '')
    )

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
                st.error("Por favor, preencha o endereço completo e um CPF válido com 11 dígitos numéricos.")
            elif not uf:
                st.error("Por favor, selecione o Estado (UF) para protocolo.")
            elif not origem_sel:
                st.error("Por favor, selecione o aeroporto de origem.")
            elif not destino_sel:
                st.error("Por favor, selecione o aeroporto de destino final.")
            elif not st.session_state.checked_nao_lembro and len(pnr) != 6:
                st.error("Preencha o Código Localizador (PNR) com exatamente 6 dígitos, ou marque a opção de que não possui o código em mãos.")
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
                st.session_state.nao_lembro_dados = st.session_state.checked_nao_lembro
                st.session_state.pnr = pnr
                st.session_state.num_voo = num_voo.strip()
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
                st.session_state.relato_danos = relato_danos
                ir_para_etapa(3)

elif st.session_state.etapa == 3:
    if st.button("⬅️ Corrigir Dados"):
        ir_para_etapa(2)

    primeiro_nome = st.session_state.get('primeiro_nome', 'Visitante')
    st.title("Pré-visualização da sua Petição")
    st.info(f"{primeiro_nome}, confira os dados estruturados abaixo. A fundamentação legal completa será liberada na finalização.")

    uf_extenso_preview = ESTADOS_TEXTO.get(st.session_state.uf, f"DO ESTADO DE {st.session_state.uf}")
    pnr_val = st.session_state.pnr
    pnr_html = f'<span style="color: red;">{pnr_val}</span>' if pnr_val == "PENDENTE_USUARIO" else pnr_val
    num_voo_val = st.session_state.get('num_voo', '')
    num_voo_html = f" (Voo {num_voo_val})" if num_voo_val else ""

    st.markdown(f"""
    <div class="doc-container">
        <div class="doc-header">
            EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DO JUIZADO ESPECIAL CÍVEL DA COMARCA {uf_extenso_preview}
        </div>
        <p><b>REQUERENTE:</b> {st.session_state.nome.upper()}, portador(a) do CPF nº {st.session_state.cpf}, residente e domiciliado(a) em {st.session_state.endereco}. E-mail: {st.session_state.email}.</p>
        <p align="center"><b>AÇÃO DE INDENIZAÇÃO POR DANOS MORAIS E MATERIAIS</b></p>
        <p><b>REQUERIDO:</b> {st.session_state.cia_completa.upper()}, pessoa jurídica de direito privado...</p>
        <p><b>I - DOS FATOS</b><br>
        O(A) requerente adquiriu bilhetes aéreos sob o código localizador {pnr_html}{num_voo_html}, para o trecho entre {st.session_state.trecho} ({st.session_state.tipo_voo}), com data marcada para {st.session_state.data_voo_br}. Incidente registrado: {st.session_state.problema}. Ocorre que a empresa falhou gravemente na prestação do serviço...</p>
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
            if st.session_state.pnr == "PENDENTE_USUARIO":
                aviso_pendencia()
            else:
                ir_para_etapa(4)

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
            <p style="margin: 0; font-size: 14px; line-height: 1.5;">Advogados cobram até 30% do que você ganha. Com a petição pronta elaborada para o caso, você mesmo protocola em minutos e coloca todo o valor no bolso.</p>
        </div>
        """, unsafe_allow_html=True)

        st.link_button(
            "Elaboração de Notificação Extrajudicial de Voo - Resolfix (R$ 56,90)", 
            "https://www.mercadopago.com.br/checkout/v1/redirect?pref_id=TOKEN_MERCADO_PAGO_EXEMPLO", 
            type="primary", 
            use_container_width=True
        )

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
            st.session_state.get('num_voo', ''),
            st.session_state.trecho, 
            st.session_state.data_voo_br, 
            st.session_state.tipo_voo,
            st.session_state.problema,
            st.session_state.get('relato_danos', ''),
            st.session_state.get('conexoes_info', '')
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