"""
Aplicação Streamlit para Precificação de Títulos Públicos
Similar à ferramenta ANBIMA
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

from api_tesouro import TesouroAPI
from calculadora import CalculadoraInvestimentos


# Configuração da página
st.set_page_config(
    page_title="Calculadora de Renda Fixa",

    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS customizado
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)  # Cache por 1 hora
def carregar_dados_titulos():
    """Carrega dados dos títulos públicos"""
    api = TesouroAPI()
    return api.buscar_titulos_tesouro_direto()


@st.cache_data(ttl=3600)  # Cache por 1 hora
def carregar_projecao_ipca():
    """Carrega projeção de IPCA do Banco Central"""
    api = TesouroAPI()
    return api.buscar_projecao_ipca()


def formatar_moeda(valor):
    """Formata valor como moeda brasileira"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main():
    # Cabeçalho
    st.markdown('<h1 class="main-header">Calculadora de Renda Fixa</h1>', unsafe_allow_html=True)
    st.markdown("### Simule e Compare Investimentos em Renda Fixa")
    st.markdown("---")
    
    # Inicializa objetos
    calc = CalculadoraInvestimentos()
    
    # Carrega dados dos títulos
    with st.spinner("Carregando dados dos títulos públicos..."):
        df_titulos = carregar_dados_titulos()
    
    # Carrega projeção de IPCA
    ipca_projetado = carregar_projecao_ipca()
    
    # Verifica se os dados foram carregados com sucesso
    if df_titulos.empty:
        st.error(" Não foi possível carregar os dados dos títulos públicos do Tesouro Direto.")
        st.info(
            "**Possíveis causas:**\n\n"
            "• Problema temporário na API do Tesouro Transparente\n"
            "• Sem conexão com a internet\n"
            "• Manutenção no sistema do governo\n\n"
            "**Solução:** Aguarde alguns minutos e recarregue a página (F5)."
        )
        st.stop()
    
    # Menu lateral
    st.sidebar.header("Configurações")
    
    opcao_menu = st.sidebar.radio(
        "Escolha a funcionalidade:",
        ["Simulador de Investimento", "Comparar Investimentos", "Visualizar Títulos Disponíveis", "Investimento Periódico"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "**Fonte de Dados:**\n"
        "Tesouro Direto - API Pública\n\n"
        "**Atualização:**\n"
        f"{datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        "**Projeção IPCA (BCB Focus):**\n"
        f"{ipca_projetado:.2f}% a.a."
    )
    
    st.sidebar.warning(
        "**Limitações da API:**\n\n"
        "• **Arredondamento:** As taxas são arredondadas (2 casas decimais)\n\n"
        "• **Defasagem:** Dados atualizados com **1 dia de atraso**\n\n"
        "• **Fonte oficial:** [Tesouro Transparente]"
        "(https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/precotaxatesourodireto.csv)"
    )
    
    # ===== FUNCIONALIDADE 1: SIMULADOR DE INVESTIMENTO =====
    if opcao_menu == "Simulador de Investimento":
        st.header("Simulador de Investimento em Títulos Públicos")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Dados do Investimento")
            
            # Seleção do título
            if not df_titulos.empty:
                nome_titulo = st.selectbox(
                    "Selecione o Título:",
                    options=df_titulos['nome'].tolist(),
                    help="Escolha o título público para investir"
                )
                
                # Obtém informações do título selecionado
                api = TesouroAPI()
                info_titulo = api.obter_titulo_por_nome(df_titulos, nome_titulo)
                
                # Exibe informações do título
                st.info(
                    f"**Tipo:** {info_titulo.get('tipo', 'N/A')}\n\n"
                    f"**Vencimento:** {info_titulo.get('vencimento', 'N/A')}\n\n"
                    f"**Taxa:** {info_titulo.get('taxa_compra', 0):.2f}% ao ano\n\n"
                    f"**Preço Unitário:** {formatar_moeda(info_titulo.get('preco_compra', 0))}\n\n"
                    f"**Investimento Mínimo:** {formatar_moeda(info_titulo.get('investimento_minimo', 0))}"
                )
                
                # Valor a investir
                valor_investir = st.number_input(
                    "Valor a Investir (R$):",
                    min_value=float(info_titulo.get('investimento_minimo', 30.0)),
                    value=1000.0,
                    step=10.0,
                    help="Digite o valor que deseja investir (mínimo: fração de 0,01 título)"
                )
                
                # Data de compra
                data_compra = st.date_input(
                    "Data de Compra:",
                    value=datetime.now(),
                    help="Data em que você fará o investimento"
                )
                
                # Data de vencimento (extraída do título)
                vencimento_str = info_titulo.get('vencimento', '01/01/2027')
                try:
                    if '/' in vencimento_str:
                        data_vencimento = datetime.strptime(vencimento_str, '%d/%m/%Y')
                    else:
                        data_vencimento = datetime.now() + timedelta(days=365)
                except:
                    data_vencimento = datetime.now() + timedelta(days=365)
                
                st.info(f"**Data de Vencimento:** {data_vencimento.strftime('%d/%m/%Y')}")
                
                # Opção de resgate antecipado
                resgate_antecipado = st.checkbox(
                    "Resgate Antecipado",
                    value=False,
                    help="Marque se deseja simular um resgate antes do vencimento"
                )
                
                # Se resgate antecipado, permite escolher a data
                if resgate_antecipado:
                    data_resgate = st.date_input(
                        "Data de Resgate:",
                        value=datetime.now() + timedelta(days=60),
                        min_value=data_compra + timedelta(days=1),
                        max_value=data_vencimento.date() if hasattr(data_vencimento, 'date') else data_vencimento,
                        help="Data em que você pretende resgatar o investimento"
                    )
                    # Converte para datetime
                    data_final = datetime.combine(data_resgate, datetime.min.time())
                    
                    # Alerta de IOF se menos de 30 dias
                    dias_ate_resgate = (data_resgate - data_compra).days
                    if dias_ate_resgate < 30:
                        st.warning(f"IOF aplicável! Resgate em {dias_ate_resgate} dias sofrerá IOF regressivo.")
                else:
                    data_final = data_vencimento
                
                # Calcula quantidade de títulos
                quantidade, valor_real = calc.calcular_quantidade_titulos(
                    valor_investir,
                    info_titulo.get('preco_compra', 1000)
                )
                
                if quantidade > 0:
                    st.success(
                        f"**Você poderá comprar:** {quantidade:.2f} título(s)\n\n"
                        f"**Equivalente a:** {quantidade * 100:.0f}% de {1 if quantidade < 1 else int(quantidade)} título(s)\n\n"
                        f"**Valor total investido:** {formatar_moeda(valor_real)}"
                    )
                else:
                    st.error(
                        f"⚠️ Valor insuficiente! O investimento mínimo é {formatar_moeda(info_titulo.get('investimento_minimo', 0))}"
                    )
                
                # Info sobre cálculo automático da taxa Selic
                if 'Selic' in info_titulo.get('tipo', ''):
                    st.info(
                        "ℹ️ **Taxa com Selic em tempo real:** A rentabilidade exibida já inclui "
                        "automaticamente a taxa Selic atual (obtida do Banco Central) somada ao "
                        "spread do título informado pelo Tesouro Direto."
                    )
                
                # Botão de calcular
                if st.button("Calcular Retorno", type="primary", use_container_width=True):
                    # Calcula o valor futuro
                    resultado = calc.calcular_valor_futuro(
                        valor_investido=valor_real,
                        taxa_anual=info_titulo.get('taxa_compra', 10),
                        data_compra=datetime.combine(data_compra, datetime.min.time()),
                        data_vencimento=data_final,
                        tipo_titulo=info_titulo.get('tipo', 'prefixado'),
                        ipca_projetado=ipca_projetado
                    )
                    
                    # Armazena resultado e informações do título na sessão
                    st.session_state['resultado'] = resultado
                    st.session_state['tipo_titulo'] = info_titulo.get('tipo', '')
                    st.session_state['taxa_original'] = info_titulo.get('taxa_compra', 0)
        
        with col2:
            st.subheader("Resultado da Simulação")
            
            if 'resultado' in st.session_state:
                resultado = st.session_state['resultado']
                
                # Métricas principais
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.metric(
                        "Valor Investido",
                        formatar_moeda(resultado['valor_investido'])
                    )
                    st.metric(
                        "Valor Futuro Bruto",
                        formatar_moeda(resultado['valor_futuro_bruto']),
                        delta=f"+{resultado['rentabilidade_bruta']:.2f}%"
                    )
                
                with col_b:
                    st.metric(
                        "Impostos e Taxas",
                        formatar_moeda(resultado['imposto_renda'] + resultado['iof'] + resultado['custodia_b3'])
                    )
                    st.metric(
                        "Valor Final Líquido",
                        formatar_moeda(resultado['valor_futuro_liquido']),
                        delta=f"+{resultado['rentabilidade_liquida']:.2f}%"
                    )
                
                # Tabela detalhada
                st.markdown("### Detalhamento")
                tabela_resultado = pd.DataFrame({
                    'Descrição': [
                        'Valor Investido',
                        'Valor Futuro Bruto',
                        'Imposto de Renda',
                        'IOF',
                        'Custódia B3',
                        'Valor Final Líquido',
                        'Lucro Líquido',
                        'Rentabilidade Bruta',
                        'Rentabilidade Líquida',
                        'Período (dias)',
                        'Período (anos)',
                        'Taxa Anual'
                    ],
                    'Valor': [
                        formatar_moeda(resultado['valor_investido']),
                        formatar_moeda(resultado['valor_futuro_bruto']),
                        formatar_moeda(resultado['imposto_renda']),
                        formatar_moeda(resultado['iof']),
                        formatar_moeda(resultado['custodia_b3']),
                        formatar_moeda(resultado['valor_futuro_liquido']),
                        formatar_moeda(resultado['valor_futuro_liquido'] - resultado['valor_investido']),
                        f"{resultado['rentabilidade_bruta']:.2f}%",
                        f"{resultado['rentabilidade_liquida']:.2f}%",
                        f"{resultado['dias_corridos']} dias",
                        f"{resultado['anos']:.2f} anos",
                        f"{resultado['taxa_anual']:.2f}% a.a."
                    ]
                })
                st.dataframe(tabela_resultado, use_container_width=True, hide_index=True)
                
                # Gráfico de pizza
                fig = go.Figure(data=[go.Pie(
                    labels=['Valor Investido', 'Lucro Líquido', 'Imposto de Renda', 'IOF', 'Custódia B3'],
                    values=[
                        resultado['valor_investido'],
                        resultado['valor_futuro_liquido'] - resultado['valor_investido'],
                        resultado['imposto_renda'],
                        resultado['iof'],
                        resultado['custodia_b3']
                    ],
                    hole=0.4,
                    marker_colors=['#636EFA', '#00CC96', '#EF553B', '#FFA15A', '#AB63FA']
                )])
                fig.update_layout(
                    title="Composição do Investimento",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            else:
                st.info("Preencha os dados e clique em 'Calcular Retorno' para ver os resultados")
    
    # ===== FUNCIONALIDADE 2: COMPARAR INVESTIMENTOS =====
    elif opcao_menu == "Comparar Investimentos":
        st.header("Comparador de Investimentos em Renda Fixa")
        st.markdown("Compare o rendimento entre diferentes tipos de investimento")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Configurações")
            
            # Valor a investir
            valor_investir = st.number_input(
                "Valor a Investir (R$):",
                min_value=100.0,
                value=1000.0,
                step=100.0,
                help="Quanto você pretende investir"
            )
            
            # Período
            periodo_meses = st.selectbox(
                "Vencimento:",
                options=[6, 12, 24, 36, 60],
                index=1,
                format_func=lambda x: f"{x} meses" if x < 12 else f"{x//12} ano{'s' if x > 12 else ''}"
            )
            
            # Aportes mensais
            aporte_mensal = st.number_input(
                "Aporte Mensal (R$):",
                min_value=0.0,
                value=0.0,
                step=50.0,
                help="Valor adicional que você investirá todo mês"
            )
            
            st.markdown("---")
            st.markdown("**Taxas de Referência:**")
            
            # Taxa CDI
            cdi_atual = st.number_input(
                "CDI (% a.a.):",
                min_value=0.0,
                max_value=30.0,
                value=14.9,
                step=0.1,
                help="Taxa CDI atual (referência de mercado)"
            )
            
            # CDB
            percentual_cdb = st.slider(
                "CDB (% do CDI):",
                min_value=80,
                max_value=130,
                value=100,
                step=5,
                help="Percentual do CDI oferecido pelo CDB"
            )
            
            # LCI/LCA
            percentual_lci = st.slider(
                "LCI/LCA (% do CDI):",
                min_value=70,
                max_value=110,
                value=90,
                step=5,
                help="Percentual do CDI oferecido pela LCI/LCA (isento de IR)"
            )
            
            # Tesouro Direto
            taxa_tesouro = st.number_input(
                "Tesouro Direto (% a.a.):",
                min_value=0.0,
                max_value=30.0,
                value=14.0,
                step=0.5,
                help="Taxa do título do Tesouro Direto"
            )
            
            # Botão calcular
            calcular_comparacao = st.button("Comparar Investimentos", type="primary", use_container_width=True)
        
        with col2:
            st.subheader("Resultados da Comparação")
            
            if calcular_comparacao or 'comparacao' in st.session_state:
                if calcular_comparacao:
                    # Calcula comparação
                    comparacao = calc.comparar_investimentos(
                        valor_investido=valor_investir,
                        meses=periodo_meses,
                        cdi_atual=cdi_atual,
                        percentual_cdb=percentual_cdb,
                        percentual_lci=percentual_lci,
                        taxa_tesouro=taxa_tesouro
                    )
                    st.session_state['comparacao'] = comparacao
                
                comparacao = st.session_state['comparacao']
                
                # Cards de resultados
                st.markdown("### Valor Final de Cada Investimento")
                
                # Cria 4 colunas para os cards
                col_a, col_b, col_c, col_d = st.columns(4)
                
                produtos = [
                    ('poupanca', 'Poupança', '#FFD93D', col_a),
                    ('cdb', 'CDB', '#6BCB77', col_b),
                    ('lci', 'LCI/LCA', '#4D96FF', col_c),
                    ('tesouro', 'Tesouro Direto', '#9D84B7', col_d)
                ]
                
                for key, nome, cor, coluna in produtos:
                    with coluna:
                        valor_final = comparacao[key]['valor_final']
                        rentabilidade = comparacao[key]['rentabilidade']
                        
                        st.markdown(f"""
                        <div style='
                            background-color: {cor}25;
                            border-left: 4px solid {cor};
                            padding: 15px;
                            border-radius: 5px;
                            margin-bottom: 10px;
                        '>
                            <h4 style='margin: 0; color: #333;'>{nome}</h4>
                            <h2 style='margin: 10px 0; color: {cor};'>{formatar_moeda(valor_final)}</h2>
                            <p style='margin: 0; color: #666; font-size: 14px;'>
                                <strong>+{rentabilidade:.2f}%</strong>
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Tabela comparativa detalhada
                st.markdown("### Detalhamento Completo")
                
                df_comparacao = pd.DataFrame({
                    'Investimento': ['Poupança', 'CDB', 'LCI/LCA', 'Tesouro Direto'],
                    'Valor Final': [
                        formatar_moeda(comparacao['poupanca']['valor_final']),
                        formatar_moeda(comparacao['cdb']['valor_final']),
                        formatar_moeda(comparacao['lci']['valor_final']),
                        formatar_moeda(comparacao['tesouro']['valor_final'])
                    ],
                    'Rentabilidade': [
                        f"+{comparacao['poupanca']['rentabilidade']:.2f}%",
                        f"+{comparacao['cdb']['rentabilidade']:.2f}%",
                        f"+{comparacao['lci']['rentabilidade']:.2f}%",
                        f"+{comparacao['tesouro']['rentabilidade']:.2f}%"
                    ],
                    'Lucro Líquido': [
                        formatar_moeda(comparacao['poupanca']['lucro']),
                        formatar_moeda(comparacao['cdb']['lucro']),
                        formatar_moeda(comparacao['lci']['lucro']),
                        formatar_moeda(comparacao['tesouro']['lucro'])
                    ],
                    'IR': [
                        formatar_moeda(comparacao['poupanca']['ir']),
                        formatar_moeda(comparacao['cdb']['ir']),
                        formatar_moeda(comparacao['lci']['ir']),
                        formatar_moeda(comparacao['tesouro']['ir'])
                    ],
                    'Taxa': [
                        f"{comparacao['poupanca']['taxa']:.2f}% a.a.",
                        f"{comparacao['cdb']['taxa']:.2f}% a.a. ({percentual_cdb}% CDI)",
                        f"{comparacao['lci']['taxa']:.2f}% a.a. ({percentual_lci}% CDI)",
                        f"{comparacao['tesouro']['taxa']:.2f}% a.a."
                    ]
                })
                
                st.dataframe(df_comparacao, use_container_width=True, hide_index=True)
                
                # Gráfico de barras comparativo
                st.markdown("### Comparação Visual")
                
                fig = go.Figure()
                
                investimentos = ['Poupança', 'CDB', 'LCI/LCA', 'Tesouro Direto']
                valores_finais = [
                    comparacao['poupanca']['valor_final'],
                    comparacao['cdb']['valor_final'],
                    comparacao['lci']['valor_final'],
                    comparacao['tesouro']['valor_final']
                ]
                cores = ['#FFD93D', '#6BCB77', '#4D96FF', '#9D84B7']
                
                fig.add_trace(go.Bar(
                    x=investimentos,
                    y=valores_finais,
                    marker_color=cores,
                    text=[formatar_moeda(v) for v in valores_finais],
                    textposition='outside'
                ))
                
                fig.update_layout(
                    title=f'Valor Final após {periodo_meses} meses',
                    xaxis_title='Tipo de Investimento',
                    yaxis_title='Valor (R$)',
                    height=400,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Destaque do melhor investimento
                melhor_investimento = max(comparacao.items(), key=lambda x: x[1]['valor_final'] if isinstance(x[1], dict) and 'valor_final' in x[1] else 0)
                nome_melhor = {
                    'poupanca': 'Poupança',
                    'cdb': 'CDB',
                    'lci': 'LCI/LCA',
                    'tesouro': 'Tesouro Direto'
                }.get(melhor_investimento[0], '')
                
                st.success(f"**Melhor opção:** {nome_melhor} com rentabilidade de **{melhor_investimento[1]['rentabilidade']:.2f}%**")
                
            else:
                st.info("Configure os parâmetros e clique em 'Comparar Investimentos' para ver os resultados")
    
    # ===== FUNCIONALIDADE 3: VISUALIZAR TÍTULOS =====
    elif opcao_menu == "Visualizar Títulos Disponíveis":
        st.header("Títulos Públicos Disponíveis")
        
        if not df_titulos.empty:
            # Filtros
            col1, col2 = st.columns(2)
            
            with col1:
                tipos_disponiveis = df_titulos['tipo'].unique().tolist()
                tipo_filtro = st.multiselect(
                    "Filtrar por Tipo:",
                    options=tipos_disponiveis,
                    default=tipos_disponiveis
                )
            
            with col2:
                ordenar_por = st.selectbox(
                    "Ordenar por:",
                    options=['taxa_compra', 'vencimento', 'nome', 'preco_compra'],
                    format_func=lambda x: {
                        'taxa_compra': 'Taxa',
                        'vencimento': 'Vencimento',
                        'nome': 'Nome',
                        'preco_compra': 'Preço'
                    }[x]
                )
            
            # Aplica filtros
            df_filtrado = df_titulos[df_titulos['tipo'].isin(tipo_filtro)]
            
            # Aplica ordenação
            df_filtrado = df_filtrado.sort_values(by=ordenar_por, ascending=(ordenar_por != 'taxa_compra'))
            
            # Formata DataFrame para exibição
            df_exibicao = df_filtrado.copy()
            df_exibicao['preco_compra'] = df_exibicao['preco_compra'].apply(
                lambda x: formatar_moeda(x) if pd.notnull(x) else 'N/A'
            )
            df_exibicao['taxa_compra'] = df_exibicao['taxa_compra'].apply(
                lambda x: f"{x:.2f}%" if pd.notnull(x) else 'N/A'
            )
            df_exibicao['investimento_minimo'] = df_exibicao['investimento_minimo'].apply(
                lambda x: formatar_moeda(x) if pd.notnull(x) else 'N/A'
            )
            
            # Renomeia colunas
            df_exibicao = df_exibicao.rename(columns={
                'nome': 'Título',
                'tipo': 'Tipo',
                'vencimento': 'Vencimento',
                'taxa_compra': 'Taxa',
                'preco_compra': 'Preço',
                'investimento_minimo': 'Investimento Mínimo'
            })
            
            # Exibe tabela
            st.dataframe(
                df_exibicao[['Título', 'Tipo', 'Vencimento', 'Taxa', 'Preço', 'Investimento Mínimo']],
                use_container_width=True,
                hide_index=True
            )
            
            # Gráfico de taxas
            st.subheader("Comparação de Taxas por Título")
            df_grafico = df_filtrado[df_filtrado['taxa_compra'].notnull()].copy()
            
            if not df_grafico.empty:
                fig = px.bar(
                    df_grafico,
                    x='nome',
                    y='taxa_compra',
                    color='tipo',
                    title='Taxas dos Títulos Públicos',
                    labels={'nome': 'Título', 'taxa_compra': 'Taxa (% a.a.)', 'tipo': 'Tipo'},
                    height=500
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Nenhum título disponível no momento.")
    
    # ===== FUNCIONALIDADE 4: INVESTIMENTO PERIÓDICO =====
    elif opcao_menu == "Investimento Periódico":
        st.header("Simulador de Investimento Periódico")
        st.markdown("Simule aportes mensais em títulos públicos")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Configurações")
            
            # Valor mensal
            valor_mensal = st.number_input(
                "Valor do Aporte Mensal (R$):",
                min_value=30.0,
                value=1000.0,
                step=100.0
            )
            
            # Período
            periodo_meses = st.slider(
                "Período (meses):",
                min_value=6,
                max_value=360,
                value=60,
                step=6
            )
            
            # Taxa
            taxa_anual = st.number_input(
                "Taxa Anual Estimada (%):",
                min_value=0.0,
                max_value=30.0,
                value=13.0,
                step=0.5
            )
            
            if st.button("Calcular Projeção", type="primary", use_container_width=True):
                # Calcula projeção
                projecao = calc.projetar_investimento_periodico(
                    valor_mensal=valor_mensal,
                    taxa_anual=taxa_anual,
                    meses=periodo_meses
                )
                
                st.session_state['projecao'] = projecao
        
        with col2:
            st.subheader("Resultado da Projeção")
            
            if 'projecao' in st.session_state:
                projecao = st.session_state['projecao']
                
                # Métricas
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.metric(
                        "Total Investido",
                        formatar_moeda(projecao['total_investido'])
                    )
                
                with col_b:
                    st.metric(
                        "Valor Final",
                        formatar_moeda(projecao['valor_futuro']),
                        delta=formatar_moeda(projecao['lucro'])
                    )
                
                st.metric(
                    "Rentabilidade Total",
                    f"{projecao['rentabilidade']:.2f}%"
                )
                
                # Gráfico de evolução
                meses = list(range(1, periodo_meses + 1))
                valores = []
                investido_acumulado = []
                
                taxa_mensal = calc.calcular_rentabilidade_mensal(taxa_anual) / 100
                valor_acum = 0
                invest_acum = 0
                
                for mes in meses:
                    invest_acum += valor_mensal
                    valor_acum = (valor_acum + valor_mensal) * (1 + taxa_mensal)
                    valores.append(valor_acum)
                    investido_acumulado.append(invest_acum)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=meses,
                    y=investido_acumulado,
                    name='Total Investido',
                    line=dict(color='#636EFA', width=2)
                ))
                fig.add_trace(go.Scatter(
                    x=meses,
                    y=valores,
                    name='Valor com Rendimento',
                    line=dict(color='#00CC96', width=2),
                    fill='tonexty'
                ))
                
                fig.update_layout(
                    title='Evolução do Investimento',
                    xaxis_title='Meses',
                    yaxis_title='Valor (R$)',
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Configure os parâmetros e clique em 'Calcular Projeção'")
    
    # Rodapé
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        <small>
        Ferramenta desenvolvida para fins educacionais<br>
        Os valores são simulações e podem variar conforme condições de mercado<br>
        Rentabilidade passada não é garantia de rentabilidade futura
        </small>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
