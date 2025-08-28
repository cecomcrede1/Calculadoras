import streamlit as st
import numpy as np
import pandas as pd

def calcular_proficiencia_na_escala(proficiencia, limite_inferior, limite_superior):
    """Converte a proficiência para uma escala de 0 a 10"""
    if proficiencia < limite_inferior:
        return 0
    elif proficiencia > limite_superior:
        return 10
    else:
        return ((proficiencia - limite_inferior) / (limite_superior - limite_inferior)) * 10

def calcular_fator_ajuste_alfabetizacao(perc_abaixo_basico, perc_basico, perc_proficiente, perc_avancado):
    """Calcula o fator de ajuste para universalização do aprendizado - Alfabetização"""
    fator = (0.25 * perc_abaixo_basico + 
             0.50 * perc_basico + 
             0.75 * perc_proficiente + 
             1.00 * perc_avancado) / 100
    return fator

def calcular_fator_ajuste_fundamental(perc_muito_critico, perc_critico, perc_intermediario, perc_adequado):
    """Calcula o fator de ajuste para universalização do aprendizado - 5º e 9º anos"""
    fator = (0.25 * perc_muito_critico + 
             0.50 * perc_critico + 
             0.75 * perc_intermediario + 
             1.00 * perc_adequado) / 100
    return fator

def classificar_nivel_alfa_lp(proficiencia_escala):
    """Classifica o nível de proficiência em Língua Portuguesa - Alfabetização"""
    if proficiencia_escala < 2.5:
        return "Não alfabetizado e Alfabetização Incompleta/Abaixo do Básico"
    elif proficiencia_escala < 5.0:
        return "Intermediário/Básico"
    elif proficiencia_escala < 7.5:
        return "Suficiente/Proficiente"
    else:
        return "Adequado/Avançado"

def classificar_nivel_alfa_mat(proficiencia_escala):
    """Classifica o nível de proficiência em Matemática - Alfabetização"""
    if proficiencia_escala < 2.5:
        return "Abaixo do Básico"
    elif proficiencia_escala < 5.0:
        return "Básico"
    elif proficiencia_escala < 7.5:
        return "Proficiente"
    else:
        return "Avançado"

def classificar_nivel_fundamental(proficiencia_escala):
    """Classifica o nível de proficiência para 5º e 9º anos"""
    if proficiencia_escala < 2.5:
        return "Muito Crítico"
    elif proficiencia_escala < 5.0:
        return "Crítico"
    elif proficiencia_escala < 7.5:
        return "Intermediário"
    else:
        return "Adequado"

def calcular_ide_componente(proficiencia_escala, taxa_participacao, fator_ajuste):
    """Calcula o IDE para um componente"""
    return proficiencia_escala * (taxa_participacao / 100) * fator_ajuste

# Configuração da página
st.set_page_config(
    page_title="Simulador IDE Completo - Ceará",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🎓 Simulador do Índice de Desempenho Escolar (IDE)")
st.markdown("**Sistema de Avaliação da Educação Básica do Estado do Ceará (SPAECE)**")

# Seleção do tipo de avaliação
tipo_avaliacao = st.selectbox(
    "📋 Selecione o tipo de avaliação:",
    ["IDE-Alfa (2º ano)", "IDE-5 (5º ano)", "IDE-9 (9º ano)"],
    index=0
)

# Informações sobre cada tipo de IDE
with st.expander("ℹ️ Sobre os tipos de IDE"):
    st.markdown("""
    ### 📖 IDE-Alfa (2º ano)
    Avalia o processo de alfabetização em Língua Portuguesa e Matemática.
    - **LP:** Escala 400-800 (Não alfabetizado → Adequado/Avançado)
    - **Mat:** Escala 300-700 (Abaixo do Básico → Avançado)
    
    ### 📚 IDE-5 (5º ano)
    Avalia competências em Língua Portuguesa e Matemática no final dos anos iniciais.
    - **LP:** Escala 75-275 (Muito Crítico → Adequado)
    - **Mat:** Escala 100-300 (Muito Crítico → Adequado)
    
    ### 🎯 IDE-9 (9º ano)
    Avalia competências em Língua Portuguesa e Matemática no final dos anos finais.
    - **LP:** Escala 150-350 (Muito Crítico → Adequado)
    - **Mat:** Escala 175-375 (Muito Crítico → Adequado)
    
    **Fórmula geral:** IDE = (IDE-LP + IDE-Mat) / 2
    """)

# Definir parâmetros baseados no tipo de avaliação
if tipo_avaliacao == "IDE-Alfa (2º ano)":
    limite_inf_lp, limite_sup_lp = 400, 800
    limite_inf_mat, limite_sup_mat = 300, 700
    valor_padrao_lp, valor_padrao_mat = 600, 550
    niveis = ["Abaixo do Básico", "Básico", "Proficiente", "Avançado"]
    usar_alfa = True
elif tipo_avaliacao == "IDE-5 (5º ano)":
    limite_inf_lp, limite_sup_lp = 75, 275
    limite_inf_mat, limite_sup_mat = 100, 300
    valor_padrao_lp, valor_padrao_mat = 200, 225
    niveis = ["Muito Crítico", "Crítico", "Intermediário", "Adequado"]
    usar_alfa = False
else:  # IDE-9 (9º ano)
    limite_inf_lp, limite_sup_lp = 150, 350
    limite_inf_mat, limite_sup_mat = 175, 375
    valor_padrao_lp, valor_padrao_mat = 275, 300
    niveis = ["Muito Crítico", "Crítico", "Intermediário", "Adequado"]
    usar_alfa = False

# Layout em duas colunas
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📖 Língua Portuguesa")
    
    # Dados de entrada - Língua Portuguesa
    st.subheader("Dados da Escola")
    prof_lp = st.number_input(
        "Proficiência Média em LP",
        min_value=float(limite_inf_lp - 100),
        max_value=float(limite_sup_lp + 100),
        value=float(valor_padrao_lp),
        step=10.0,
        help=f"Pontuação na escala do SPAECE ({limite_inf_lp}-{limite_sup_lp})"
    )
    
    alunos_matriculados_lp = st.number_input(
        "Alunos Matriculados (LP)",
        min_value=1,
        max_value=500,
        value=60,
        step=1
    )
    
    alunos_avaliados_lp = st.number_input(
        "Alunos Avaliados (LP)",
        min_value=1,
        max_value=alunos_matriculados_lp,
        value=min(58, alunos_matriculados_lp),
        step=1
    )
    
    st.subheader("Distribuição dos Alunos por Nível (%)")
    perc_nivel1_lp = st.slider(f"{niveis[0]}", 0, 100, 15, 1, key="nivel1_lp")
    perc_nivel2_lp = st.slider(f"{niveis[1]}", 0, 100-perc_nivel1_lp, 20, 1, key="nivel2_lp")
    perc_nivel3_lp = st.slider(f"{niveis[2]}", 0, 100-perc_nivel1_lp-perc_nivel2_lp, 25, 1, key="nivel3_lp")
    perc_nivel4_lp = 100 - perc_nivel1_lp - perc_nivel2_lp - perc_nivel3_lp
    st.write(f"**{niveis[3]}:** {perc_nivel4_lp}%")

with col2:
    st.header("🔢 Matemática")
    
    # Dados de entrada - Matemática
    st.subheader("Dados da Escola")
    prof_mat = st.number_input(
        "Proficiência Média em Mat",
        min_value=float(limite_inf_mat - 100),
        max_value=float(limite_sup_mat + 100),
        value=float(valor_padrao_mat),
        step=10.0,
        help=f"Pontuação na escala do SPAECE ({limite_inf_mat}-{limite_sup_mat})"
    )
    
    alunos_matriculados_mat = st.number_input(
        "Alunos Matriculados (Mat)",
        min_value=1,
        max_value=500,
        value=60,
        step=1
    )
    
    alunos_avaliados_mat = st.number_input(
        "Alunos Avaliados (Mat)",
        min_value=1,
        max_value=alunos_matriculados_mat,
        value=min(58, alunos_matriculados_mat),
        step=1
    )
    
    st.subheader("Distribuição dos Alunos por Nível (%)")
    perc_nivel1_mat = st.slider(f"{niveis[0]}", 0, 100, 20, 1, key="nivel1_mat")
    perc_nivel2_mat = st.slider(f"{niveis[1]}", 0, 100-perc_nivel1_mat, 25, 1, key="nivel2_mat")
    perc_nivel3_mat = st.slider(f"{niveis[2]}", 0, 100-perc_nivel1_mat-perc_nivel2_mat, 25, 1, key="nivel3_mat")
    perc_nivel4_mat = 100 - perc_nivel1_mat - perc_nivel2_mat - perc_nivel3_mat
    st.write(f"**{niveis[3]}:** {perc_nivel4_mat}%")

# Botão para calcular
if st.button(f"🧮 Calcular {tipo_avaliacao}", type="primary", use_container_width=True):
    
    # Cálculos para Língua Portuguesa
    prof_lp_escala = calcular_proficiencia_na_escala(prof_lp, limite_inf_lp, limite_sup_lp)
    taxa_part_lp = (alunos_avaliados_lp / alunos_matriculados_lp) * 100
    
    if usar_alfa:
        fator_ajuste_lp = calcular_fator_ajuste_alfabetizacao(perc_nivel1_lp, perc_nivel2_lp, perc_nivel3_lp, perc_nivel4_lp)
        classificacao_lp = classificar_nivel_alfa_lp(prof_lp_escala)
    else:
        fator_ajuste_lp = calcular_fator_ajuste_fundamental(perc_nivel1_lp, perc_nivel2_lp, perc_nivel3_lp, perc_nivel4_lp)
        classificacao_lp = classificar_nivel_fundamental(prof_lp_escala)
    
    ide_lp = calcular_ide_componente(prof_lp_escala, taxa_part_lp, fator_ajuste_lp)
    
    # Cálculos para Matemática
    prof_mat_escala = calcular_proficiencia_na_escala(prof_mat, limite_inf_mat, limite_sup_mat)
    taxa_part_mat = (alunos_avaliados_mat / alunos_matriculados_mat) * 100
    
    if usar_alfa:
        fator_ajuste_mat = calcular_fator_ajuste_alfabetizacao(perc_nivel1_mat, perc_nivel2_mat, perc_nivel3_mat, perc_nivel4_mat)
        classificacao_mat = classificar_nivel_alfa_mat(prof_mat_escala)
    else:
        fator_ajuste_mat = calcular_fator_ajuste_fundamental(perc_nivel1_mat, perc_nivel2_mat, perc_nivel3_mat, perc_nivel4_mat)
        classificacao_mat = classificar_nivel_fundamental(prof_mat_escala)
    
    ide_mat = calcular_ide_componente(prof_mat_escala, taxa_part_mat, fator_ajuste_mat)
    
    # IDE final
    ide_final = (ide_lp + ide_mat) / 2
    
    # Exibição dos resultados
    st.markdown("---")
    st.header("📊 Resultados")
    
    # Métricas principais
    col1, col2, col3 = st.columns(3)
    
    nome_ide = tipo_avaliacao.split()[0]  # IDE-Alfa, IDE-5, ou IDE-9
    
    with col1:
        st.metric(
            f"{nome_ide} Língua Portuguesa", 
            f"{ide_lp:.2f}",
            help=f"{nome_ide} calculado para Língua Portuguesa"
        )
    
    with col2:
        st.metric(
            f"{nome_ide} Matemática", 
            f"{ide_mat:.2f}",
            help=f"{nome_ide} calculado para Matemática"
        )
    
    with col3:
        st.metric(
            f"{nome_ide} Final", 
            f"{ide_final:.2f}",
            help=f"Média aritmética dos {nome_ide} de LP e Mat"
        )
    
    # Detalhamento dos cálculos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📖 Detalhes - Língua Portuguesa")
        st.write(f"**Proficiência Original:** {prof_lp:.1f}")
        st.write(f"**Escala de Referência:** {limite_inf_lp} - {limite_sup_lp}")
        st.write(f"**Proficiência na Escala 0-10:** {prof_lp_escala:.2f}")
        st.write(f"**Classificação:** {classificacao_lp}")
        st.write(f"**Taxa de Participação:** {taxa_part_lp:.1f}%")
        st.write(f"**Fator de Ajuste:** {fator_ajuste_lp:.3f}")
        
    with col2:
        st.subheader("🔢 Detalhes - Matemática")
        st.write(f"**Proficiência Original:** {prof_mat:.1f}")
        st.write(f"**Escala de Referência:** {limite_inf_mat} - {limite_sup_mat}")
        st.write(f"**Proficiência na Escala 0-10:** {prof_mat_escala:.2f}")
        st.write(f"**Classificação:** {classificacao_mat}")
        st.write(f"**Taxa de Participação:** {taxa_part_mat:.1f}%")
        st.write(f"**Fator de Ajuste:** {fator_ajuste_mat:.3f}")
    
    # Gráficos
    st.subheader("📈 Visualizações")
    
    # Gráfico de comparação IDE
    fig_comparacao = go.Figure()
    fig_comparacao.add_trace(go.Bar(
        x=['Língua Portuguesa', 'Matemática', f'{nome_ide} Final'],
        y=[ide_lp, ide_mat, ide_final],
        marker_color=['#1f77b4', '#ff7f0e', '#2ca02c'],
        text=[f'{ide_lp:.2f}', f'{ide_mat:.2f}', f'{ide_final:.2f}'],
        textposition='auto'
    ))
    fig_comparacao.update_layout(
        title=f"Comparação dos Resultados {nome_ide}",
        yaxis_title="Pontuação (0-10)",
        showlegend=False,
        yaxis=dict(range=[0, 10])
    )
    st.plotly_chart(fig_comparacao, use_container_width=True)
    
    # Gráficos de distribuição por níveis
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição LP
        valores_lp = [perc_nivel1_lp, perc_nivel2_lp, perc_nivel3_lp, perc_nivel4_lp]
        
        fig_lp = px.pie(
            values=valores_lp, 
            names=niveis, 
            title="Distribuição por Níveis - LP",
            color_discrete_sequence=['#ff4444', '#ffaa44', '#44aaff', '#44ff44']
        )
        st.plotly_chart(fig_lp, use_container_width=True)
    
    with col2:
        # Distribuição Matemática
        valores_mat = [perc_nivel1_mat, perc_nivel2_mat, perc_nivel3_mat, perc_nivel4_mat]
        
        fig_mat = px.pie(
            values=valores_mat, 
            names=niveis, 
            title="Distribuição por Níveis - Mat",
            color_discrete_sequence=['#ff4444', '#ffaa44', '#44aaff', '#44ff44']
        )
        st.plotly_chart(fig_mat, use_container_width=True)
    
    # Tabela resumo
    st.subheader("📋 Resumo dos Cálculos")
    
    dados_resumo = {
        'Componente': ['Língua Portuguesa', 'Matemática'],
        'Proficiência Original': [f'{prof_lp:.1f}', f'{prof_mat:.1f}'],
        'Escala Referência': [f'{limite_inf_lp}-{limite_sup_lp}', f'{limite_inf_mat}-{limite_sup_mat}'],
        'Proficiência (0-10)': [f'{prof_lp_escala:.2f}', f'{prof_mat_escala:.2f}'],
        'Taxa Participação': [f'{taxa_part_lp:.1f}%', f'{taxa_part_mat:.1f}%'],
        'Fator Ajuste': [f'{fator_ajuste_lp:.3f}', f'{fator_ajuste_mat:.3f}'],
        f'{nome_ide}': [f'{ide_lp:.2f}', f'{ide_mat:.2f}']
    }
    
    df_resumo = pd.DataFrame(dados_resumo)
    st.dataframe(df_resumo, use_container_width=True)
    
    # Interpretação do resultado
    st.subheader("🎯 Interpretação do Resultado")
    
    if ide_final >= 7.5:
        st.success(f"🎉 **Excelente!** A escola obteve {nome_ide} de {ide_final:.2f}, indicando um desempenho muito bom.")
        recomendacao = "Continue mantendo as boas práticas pedagógicas e busque manter a excelência."
    elif ide_final >= 5.0:
        st.warning(f"⚠️ **Bom!** A escola obteve {nome_ide} de {ide_final:.2f}, indicando um desempenho satisfatório, mas com espaço para melhorias.")
        recomendacao = "Foque em estratégias para elevar mais alunos aos níveis adequados/avançados."
    elif ide_final >= 2.5:
        st.warning(f"📈 **Regular!** A escola obteve {nome_ide} de {ide_final:.2f}, indicando necessidade de atenção especial.")
        recomendacao = "Implemente intervenções pedagógicas focadas nos alunos com maiores dificuldades."
    else:
        st.error(f"🚨 **Crítico!** A escola obteve {nome_ide} de {ide_final:.2f}, indicando necessidade urgente de intervenções.")
        recomendacao = "Requer ações imediatas e intensivas para melhorar os resultados de aprendizagem."
    
    st.info(f"**Recomendação:** {recomendacao}")
    
    # Análise comparativa se não for alfabetização
    if not usar_alfa:
        st.subheader("📊 Análise de Desempenho")
        
        if ide_lp > ide_mat:
            diferenca = ide_lp - ide_mat
            st.info(f"📖 **Língua Portuguesa** apresenta desempenho superior (+{diferenca:.2f} pontos)")
        elif ide_mat > ide_lp:
            diferenca = ide_mat - ide_lp
            st.info(f"🔢 **Matemática** apresenta desempenho superior (+{diferenca:.2f} pontos)")
        else:
            st.info("⚖️ **Desempenho equilibrado** entre as disciplinas")

# Comparador entre diferentes tipos de IDE
st.markdown("---")
st.header("🔍 Comparador entre IDEs")

with st.expander("📊 Compare diferentes tipos de IDE"):
    st.markdown("""
    **Dica:** Use esta seção para simular o desempenho da mesma escola em diferentes anos/níveis.
    Você pode salvar os resultados e comparar posteriormente para análise longitudinal.
    """)
    
    # Aqui poderia implementar uma funcionalidade para salvar e comparar diferentes simulações
    if st.button("💾 Salvar Simulação Atual"):
        st.success("Funcionalidade de salvamento pode ser implementada para comparações futuras!")

# Rodapé
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <small>
        🏛️ Sistema baseado no Decreto Nº36.585, de 06 de maio de 2025<br>
        Estado do Ceará - Secretaria da Educação<br>
        <strong>IDE-Alfa, IDE-5 e IDE-9</strong><br>
        <strong>CECOM CREDE 01</strong>
    </small>
</div>
""", unsafe_allow_html=True)
