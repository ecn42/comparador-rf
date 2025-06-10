import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def default_tax_rate(tax_rate_old, investment_type):
    if investment_type == 'Tributável':
        tax_rate_old = tax_rate_old
        tax_rate_new = 0.175  # New tax rate for comparison
    elif investment_type == 'Isento':
        tax_rate_old = 0.0
        tax_rate_new = 0.05
    return tax_rate_old, tax_rate_new

def calculate_compound_return(rate, days):
    """Calculate compound return for given rate and period"""
    return ((1 + rate/100) ** (days/365)) - 1

def format_currency(value):
    """Format value as Brazilian currency"""
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# Page configuration
st.set_page_config(
    page_title="Comparador Renda Fixa",
    page_icon="💰",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">💰 Comparador Renda Fixa</h1>', 
            unsafe_allow_html=True)

# Main tabs
tab1, tab2 = st.tabs(["📊 Análise Individual", "🔄 Comparar Múltiplos Cenários"])

with tab1:
    # Input section with better organization
    st.markdown("## 📊 Configurações do Investimento")

    col1, col2, col3 = st.columns(3)

    with col1:
        investment_type_input_selector = st.radio(
            "🏛️ Tipo de Investimento",
            ('Tributável', 'Isento'),
            key='investment_type_input_selector'
        )

    with col2:
        return_type_input_selector = st.radio(
            "📈 Tipo de Retorno",
            ('% CDI', 'Pré-fixado'),
            key='return_type_input_selector'
        )

    with col3:
        initial_investment = st.number_input(
            "💵 Valor do Investimento (R$)",
            value=10000.0,
            min_value=100.0,
            step=100.0,
            format="%.2f",
            key='initial_investment'
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        cdi_value_input = st.number_input(
            "📊 CDI Atual (% ao ano)",
            value=14.65,
            min_value=0.0,
            step=0.01,
            format="%.2f",
            key='cdi_value_input'
        )

    with col5:
        if return_type_input_selector == '% CDI':
            investment_return_input = st.number_input(
                "📊 Retorno (% do CDI)",
                value=100.0,
                min_value=0.0,
                step=0.01,
                format="%.2f",
                key='investment_return_input'
            )
        else:
            investment_return_input = st.number_input(
                "📊 Taxa Pré-fixada (%)",
                value=14.0,
                min_value=0.0,
                step=0.01,
                format="%.2f",
                key='investment_return_input'
            )

    with col6:
        term_input = st.number_input(
            "⏰ Prazo (dias)",
            value=30,
            min_value=1,
            step=1,
            format="%d",
            key='investment_term_input'
        )

    # Tax calculation
    if term_input >= 720:
        tax_rate_old = 0.15
    elif term_input >= 360:
        tax_rate_old = 0.175
    elif term_input >= 180:
        tax_rate_old = 0.2
    else:
        tax_rate_old = 0.225

    tax_rate_old, tax_rate_new = default_tax_rate(tax_rate_old, investment_type_input_selector)

    # Calculations
    if return_type_input_selector == '% CDI':
        cdi_percentage = investment_return_input
        total_rate_gross = (investment_return_input / 100) * cdi_value_input
    else:
        total_rate_gross = investment_return_input
        cdi_percentage = (investment_return_input / cdi_value_input) * 100

    # Calculate compound returns
    gross_return_period = calculate_compound_return(total_rate_gross, term_input)
    net_return_old_period = gross_return_period * (1 - tax_rate_old)
    net_return_new_period = gross_return_period * (1 - tax_rate_new)

    # Calculate final amounts
    final_amount_gross = initial_investment * (1 + gross_return_period)
    final_amount_net_old = initial_investment * (1 + net_return_old_period)
    final_amount_net_new = initial_investment * (1 + net_return_new_period)

    # Calculate net annual rates
    total_rate_net_old = total_rate_gross * (1 - tax_rate_old)
    total_rate_net_new = total_rate_gross * (1 - tax_rate_new)

    # Tax information using Streamlit components
    st.markdown("## 🏛️ Informações Tributárias")
    col_tax1, col_tax2 = st.columns(2)

    with col_tax1:
        st.info("📋 **Regime Atual**")
        st.write(f"**Taxa de IR:** {tax_rate_old * 100:.2f}%")
        st.write(f"**Prazo:** {term_input} dias")
        
        # Tax bracket explanation
        if investment_type_input_selector == 'Tributável':
            if term_input >= 720:
                st.write("**Faixa:** Acima de 720 dias")
            elif term_input >= 360:
                st.write("**Faixa:** 361 a 720 dias")
            elif term_input >= 180:
                st.write("**Faixa:** 181 a 360 dias")
            else:
                st.write("**Faixa:** Até 180 dias")

    with col_tax2:
        st.success("🆕 **Regime Proposto**")
        st.write(f"**Taxa de IR:** {tax_rate_new * 100:.2f}%")
        st.write(f"**Tipo:** {investment_type_input_selector}")
        
        if investment_type_input_selector == 'Tributável':
            st.write("**Nova regra:** Taxa fixa de 17,5%")
        else:
            st.write("**Nova regra:** Taxa de 5% para isentos")

    # Results section
    st.markdown("## 📈 Resultados da Análise")

    # Key metrics in columns
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)

    with col_m1:
        st.metric(
            "💰 Valor Bruto Final",
            format_currency(final_amount_gross),
            f"+{format_currency(final_amount_gross - initial_investment)}"
        )

    with col_m2:
        st.metric(
            "💵 Líquido (Atual)",
            format_currency(final_amount_net_old),
            f"+{format_currency(final_amount_net_old - initial_investment)}"
        )

    with col_m3:
        st.metric(
            "💸 Líquido (Novo)",
            format_currency(final_amount_net_new),
            f"+{format_currency(final_amount_net_new - initial_investment)}"
        )

    with col_m4:
        difference = final_amount_net_new - final_amount_net_old
        st.metric(
            "⚖️ Diferença",
            format_currency(difference),
            f"{'Melhor' if difference > 0 else 'Pior'} em {(final_amount_net_new - final_amount_net_old) / final_amount_net_old * 100:.2f}%",
            delta_color="inverse" if difference < 0 else "normal"
        )

    # Detailed comparison table
    st.markdown("### 📊 Comparação Detalhada")

    comparison_data = {
        'Métrica': [
            '% do CDI',
            'Taxa Anual Bruta (%)',
            'Retorno Bruto no Período (%)',
            'Taxa Anual Líquida - Atual (%)',
            'Retorno Líquido no Período - Atual (%)',
            'Taxa Anual Líquida - Nova (%)',
            'Retorno Líquido no Período - Nova (%)',
            'Imposto Pago - Atual (R$)',
            'Imposto Pago - Novo (R$)',
            'Economia/Perda de Imposto (R$)'
        ],
        'Valor': [
            f"{cdi_percentage:.2f}%",
            f"{total_rate_gross:.2f}%",
            f"{gross_return_period * 100:.2f}%",
            f"{total_rate_net_old:.2f}%",
            f"{net_return_old_period * 100:.2f}%",
            f"{total_rate_net_new:.2f}%",
            f"{net_return_new_period * 100:.2f}%",
            format_currency((final_amount_gross - initial_investment) * tax_rate_old),
            format_currency((final_amount_gross - initial_investment) * tax_rate_new),
            format_currency((final_amount_gross - initial_investment) * (tax_rate_old - tax_rate_new))
        ]
    }

    results_df = pd.DataFrame(comparison_data)
    st.dataframe(results_df, use_container_width=False, hide_index=True)

    # Visualization
    st.markdown("### 📊 Visualização Comparativa")

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Valor Final do Investimento', 'Comparação de Impostos'),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )

    # Investment comparison chart
    fig.add_trace(
        go.Bar(
            name='Bruto',
            x=['Investimento'],
            y=[final_amount_gross],
            marker_color='lightblue',
            text=[format_currency(final_amount_gross)],
            textposition='auto'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(
            name='Líquido (Atual)',
            x=['Investimento'],
            y=[final_amount_net_old],
            marker_color='orange',
            text=[format_currency(final_amount_net_old)],
            textposition='auto'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(
            name='Líquido (Novo)',
            x=['Investimento'],
            y=[final_amount_net_new],
            marker_color='green',
            text=[format_currency(final_amount_net_new)],
            textposition='auto'
        ),
        row=1, col=1
    )

    # Tax comparison chart
    tax_old = (final_amount_gross - initial_investment) * tax_rate_old
    tax_new = (final_amount_gross - initial_investment) * tax_rate_new

    fig.add_trace(
        go.Bar(
            name='Imposto Atual',
            x=['Imposto'],
            y=[tax_old],
            marker_color='red',
            text=[format_currency(tax_old)],
            textposition='auto',
            showlegend=False
        ),
        row=1, col=2
    )

    fig.add_trace(
        go.Bar(
            name='Imposto Novo',
            x=['Imposto'],
            y=[tax_new],
            marker_color='darkred',
            text=[format_currency(tax_new)],
            textposition='auto',
            showlegend=False
        ),
        row=1, col=2
    )

    fig.update_layout(height=500, showlegend=True)
    fig.update_yaxes(title_text="Valor (R$)")

    st.plotly_chart(fig, use_container_width=True)

    # Summary conclusion using Streamlit components
    st.markdown("## 🎯 Resumo Executivo")

    if final_amount_net_new > final_amount_net_old:
        conclusion_type = "success"
        conclusion_text = "vantajoso"
        emoji = "✅"
    else:
        conclusion_type = "error"
        conclusion_text = "desvantajoso"
        emoji = "❌"

    percentage_diff = abs((final_amount_net_new - final_amount_net_old) / final_amount_net_old * 100)
    absolute_diff = abs(final_amount_net_new - final_amount_net_old)
    tax_diff_absolute = abs(tax_old - tax_new)
    tax_diff_percentage = abs((tax_new - tax_old) / tax_old * 100) if tax_old > 0 else 0

    # Calculate percentage points difference in tax rates
    tax_rate_diff_pp = abs(tax_rate_new - tax_rate_old) * 100

    # Use appropriate Streamlit alert component
    if conclusion_type == "success":
        st.success(f"""
        {emoji} **Conclusão**
        
        O novo regime tributário será **{conclusion_text}** para este investimento, 
        resultando em uma diferença de **{percentage_diff:.2f}%** no retorno líquido.
        
        **📊 Impacto no Retorno:**
        - Diferença absoluta: **{format_currency(absolute_diff)}**
        - Diferença percentual: **{percentage_diff:.2f}%** a mais no retorno líquido
        
        **💰 Impacto nos Impostos:**
        - Economia absoluta: **{format_currency(tax_diff_absolute)}**
        - Economia percentual: **{tax_diff_percentage:.2f}%** menos imposto
        - Redução de **{tax_rate_diff_pp:.2f} pontos percentuais** na alíquota
        """)
    else:
        st.error(f"""
        {emoji} **Conclusão**
        
        O novo regime tributário será **{conclusion_text}** para este investimento, 
        resultando em uma diferença de **{percentage_diff:.2f}%** no retorno líquido.
        
        **📊 Impacto no Retorno:**
        - Diferença absoluta: **{format_currency(absolute_diff)}**
        - Diferença percentual: **{percentage_diff:.2f}%** a menos no retorno líquido
        
        **💰 Impacto nos Impostos:**
        - Custo adicional absoluto: **{format_currency(tax_diff_absolute)}**
        - Custo adicional percentual: **{tax_diff_percentage:.2f}%** mais imposto
        - Aumento de **{tax_rate_diff_pp:.2f} pontos percentuais** na alíquota
        """)

    # Additional insights with more detailed breakdown
    st.info(f"""
    📊 **Análise Detalhada:**

    **Retornos no Período ({term_input} dias):**
    - Rendimento bruto: **{gross_return_period * 100:.2f}%**
    - Rendimento líquido atual: **{net_return_old_period * 100:.2f}%**
    - Rendimento líquido novo: **{net_return_new_period * 100:.2f}%**

    **Comparação de Alíquotas:**
    - Taxa atual: **{tax_rate_old * 100:.2f}%**
    - Taxa nova: **{tax_rate_new * 100:.2f}%**
    - Diferença: **{tax_rate_diff_pp:.2f} pontos percentuais**

    **Equivalência CDI:**
    - Investimento equivale a **{cdi_percentage:.2f}%** do CDI
    - CDI líquido atual: **{(total_rate_net_old / cdi_value_input) * 100:.2f}%** do CDI
    - CDI líquido novo: **{(total_rate_net_new / cdi_value_input) * 100:.2f}%** do CDI
    """)

    # Add a warning for very short-term investments
    if term_input <= 30:
        st.warning(f"""
        ⚠️ **Atenção - Investimento de Curto Prazo:**
        
        Para investimentos de até 30 dias, a diferença tributária é mais significativa devido à alta alíquota atual de **{tax_rate_old * 100:.2f}%**.
        
        **Impacto da mudança:** A nova alíquota de **{tax_rate_new * 100:.2f}%** representa uma {'redução' if tax_rate_new < tax_rate_old else 'aumento'} de **{tax_rate_diff_pp:.2f} pontos percentuais**.
        """)

with tab2:
    st.markdown("## 🔄 Análise de Múltiplos Cenários")
    
    # Configuration for scenarios
    col_config1, col_config2, col_config3 = st.columns(3)
    
    with col_config1:
        scenario_investment_type = st.radio(
            "🏛️ Tipo de Investimento",
            ('Tributável', 'Isento'),
            key='scenario_investment_type'
        )
    
    with col_config2:
        scenario_return_type = st.radio(
            "📈 Tipo de Retorno",
            ('% CDI', 'Pré-fixado'),
            key='scenario_return_type'
        )
    
    with col_config3:
        scenario_initial_investment = st.number_input(
            "💵 Valor do Investimento (R$)",
            value=10000.0,
            min_value=100.0,
            step=100.0,
            format="%.2f",
            key='scenario_initial_investment'
        )
    
    col_config4, col_config5, col_config6 = st.columns(3)
    
    with col_config4:
        scenario_cdi_value = st.number_input(
            "📊 CDI Atual (% ao ano)",
            value=14.65,
            min_value=0.0,
            step=0.01,
            format="%.2f",
            key='scenario_cdi_value'
        )
    
    with col_config5:
        if scenario_return_type == '% CDI':
            scenario_investment_return = st.number_input(
                "📊 Retorno (% do CDI)",
                value=100.0,
                min_value=0.0,
                step=0.01,
                format="%.2f",
                key='scenario_investment_return'
            )
        else:
            scenario_investment_return = st.number_input(
                "📊 Taxa Pré-fixada (%)",
                value=14.0,
                min_value=0.0,
                step=0.01,
                format="%.2f",
                key='scenario_investment_return'
            )
    
    with col_config6:
        scenario_type = st.radio(
            "Tipo de Análise",
            ["Prazos Padrão", "Prazos Personalizados"],
            help="Escolha entre prazos pré-definidos ou configure seus próprios prazos"
        )
    
    # Calculate scenario parameters
    if scenario_return_type == '% CDI':
        scenario_cdi_percentage = scenario_investment_return
        scenario_total_rate_gross = (scenario_investment_return / 100) * scenario_cdi_value
    else:
        scenario_total_rate_gross = scenario_investment_return
        scenario_cdi_percentage = (scenario_investment_return / scenario_cdi_value) * 100
    
    # Define scenarios based on selection
    if scenario_type == "Prazos Padrão":
        scenarios_days = [30, 90, 180, 365, 720, 1080]
        scenario_labels = ["1 mês", "3 meses", "6 meses", "1 ano", "2 anos", "3 anos"]
    else:
        st.markdown("**Configure até 6 prazos personalizados:**")
        custom_days = []
        custom_labels = []
        
        cols = st.columns(3)
        for i in range(6):
            with cols[i % 3]:
                days = st.number_input(
                    f"Prazo {i+1} (dias)", 
                    min_value=1, 
                    max_value=3650, 
                    value=[30, 90, 180, 365, 720, 1080][i] if i < 6 else 30,
                    key=f"custom_days_{i}"
                )
                if days > 0:
                    custom_days.append(days)
                    if days < 30:
                        custom_labels.append(f"{days}d")
                    elif days < 365:
                        custom_labels.append(f"{days//30}m")
                    else:
                        custom_labels.append(f"{days//365}a{(days%365)//30}m" if days%365 > 0 else f"{days//365}a")
        
        scenarios_days = custom_days[:6]  # Limit to 6 scenarios
        scenario_labels = custom_labels[:6]
    
    if scenarios_days:
        # Calculate scenarios
        scenarios_data = []
        
        for i, days in enumerate(scenarios_days):
            # Determine tax rate for current regime
            if days >= 720:
                current_tax_rate = 0.15
            elif days >= 360:
                current_tax_rate = 0.175
            elif days >= 180:
                current_tax_rate = 0.2
            else:
                current_tax_rate = 0.225
            
            # Apply investment type logic
            if scenario_investment_type == 'Tributável':
                tax_old = current_tax_rate
                tax_new = 0.175
            else:  # Isento
                tax_old = 0.0
                tax_new = 0.05
            
            # Calculate returns
            gross_return_period = calculate_compound_return(scenario_total_rate_gross, days)
            net_return_old_period = gross_return_period * (1 - tax_old)
            net_return_new_period = gross_return_period * (1 - tax_new)
            
            # Calculate annual rates
            gross_annual_rate = scenario_total_rate_gross
            net_annual_old = gross_annual_rate * (1 - tax_old)
            net_annual_new = gross_annual_rate * (1 - tax_new)
            
            # Calculate % CDI equivalents
            cdi_gross = (gross_annual_rate / scenario_cdi_value) * 100
            cdi_net_old = (net_annual_old / scenario_cdi_value) * 100
            cdi_net_new = (net_annual_new / scenario_cdi_value) * 100
            
            # Calculate final amounts
            final_gross = scenario_initial_investment * (1 + gross_return_period)
            final_net_old = scenario_initial_investment * (1 + net_return_old_period)
            final_net_new = scenario_initial_investment * (1 + net_return_new_period)
            
            # Calculate difference
            difference = final_net_new - final_net_old
            difference_pct = (difference / final_net_old) * 100 if final_net_old > 0 else 0
            
            scenarios_data.append({
                'Prazo': scenario_labels[i] if i < len(scenario_labels) else f"{days}d",
                'Dias': days,
                'IR Atual (%)': f"{tax_old*100:.1f}%",
                'IR Novo (%)': f"{tax_new*100:.1f}%",
                
                # Period Returns
                'Retorno Bruto Período': f"{gross_return_period*100:.2f}%",
                'Retorno Líq. Atual Período': f"{net_return_old_period*100:.2f}%",
                'Retorno Líq. Novo Período': f"{net_return_new_period*100:.2f}%",
                
                # Annual Returns
                'Taxa Bruta Anual': f"{gross_annual_rate:.2f}%",
                'Taxa Líq. Atual Anual': f"{net_annual_old:.2f}%",
                'Taxa Líq. Nova Anual': f"{net_annual_new:.2f}%",
                
                # CDI Equivalents
                '% CDI Bruto': f"{cdi_gross:.1f}%",
                '% CDI Líq. Atual': f"{cdi_net_old:.1f}%",
                '% CDI Líq. Novo': f"{cdi_net_new:.1f}%",
                
                # Final Values
                'Valor Final Bruto': final_gross,
                'Valor Final Atual': final_net_old,
                'Valor Final Novo': final_net_new,
                'Diferença (R$)': difference,
                'Diferença (%)': difference_pct,
                
                # Formatted values for display
                'Valor Final Bruto (fmt)': format_currency(final_gross),
                'Valor Final Atual (fmt)': format_currency(final_net_old),
                'Valor Final Novo (fmt)': format_currency(final_net_new),
                'Diferença (fmt)': format_currency(difference),
            })
        
        scenarios_df = pd.DataFrame(scenarios_data)
        
        # Display options
        st.markdown("### 📊 Selecione as Métricas para Visualizar")
        
        col_display1, col_display2, col_display3 = st.columns(3)
        
        with col_display1:
            show_returns = st.checkbox("📈 Retornos", value=True, key="show_returns_scenarios")
            show_period = st.checkbox("⏱️ Retornos do Período", value=True, key="show_period_scenarios")
            
        with col_display2:
            show_annual = st.checkbox("📅 Retornos Anuais", value=True, key="show_annual_scenarios")
            show_cdi = st.checkbox("📊 % CDI", value=True, key="show_cdi_scenarios")
            
        with col_display3:
            show_values = st.checkbox("💰 Valores Finais", value=True, key="show_values_scenarios")
            show_taxes = st.checkbox("🏛️ Alíquotas IR", value=False, key="show_taxes_scenarios")
        
        # Create display dataframe based on selections
        display_columns = ['Prazo']
        
        if show_taxes:
            display_columns.extend(['IR Atual (%)', 'IR Novo (%)'])
        
        if show_returns and show_period:
            display_columns.extend([
                'Retorno Bruto Período', 
                'Retorno Líq. Atual Período', 
                'Retorno Líq. Novo Período'
            ])
        
        if show_returns and show_annual:
            display_columns.extend([
                'Taxa Bruta Anual', 
                'Taxa Líq. Atual Anual', 
                'Taxa Líq. Nova Anual'
            ])
        
        if show_cdi:
            display_columns.extend([
                '% CDI Bruto', 
                '% CDI Líq. Atual', 
                '% CDI Líq. Novo'
            ])
        
        if show_values:
            display_columns.extend([
                'Valor Final Atual (fmt)', 
                'Valor Final Novo (fmt)', 
                'Diferença (fmt)'
            ])
        
        # Display the table
        display_df = scenarios_df[display_columns].copy()
        
        # Rename columns for better display
        column_renames = {
            'Valor Final Atual (fmt)': 'Valor Final Atual',
            'Valor Final Novo (fmt)': 'Valor Final Novo',
            'Diferença (fmt)': 'Diferença'
        }
        display_df = display_df.rename(columns=column_renames)
        
        st.dataframe(
            display_df, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Diferença": st.column_config.TextColumn(
                    help="Diferença entre regime novo e atual"
                )
            }
        )
        
        # Charts section
        if len(scenarios_data) > 1:
            st.markdown("### 📈 Visualizações Comparativas")
            
            chart_tabs = st.tabs([
                "💰 Valores Finais", 
                "📊 Retornos (%)", 
                "🎯 % CDI", 
                "⚖️ Diferenças"
            ])
            
            with chart_tabs[0]:
                # Values comparison chart
                fig_values = go.Figure()
                
                fig_values.add_trace(go.Scatter(
                    x=scenario_labels[:len(scenarios_data)],
                    y=[d['Valor Final Atual'] for d in scenarios_data],
                    mode='lines+markers',
                    name='Regime Atual',
                    line=dict(color='orange', width=3),
                    marker=dict(size=8)
                ))
                
                fig_values.add_trace(go.Scatter(
                    x=scenario_labels[:len(scenarios_data)],
                    y=[d['Valor Final Novo'] for d in scenarios_data],
                    mode='lines+markers',
                    name='Regime Novo',
                    line=dict(color='green', width=3),
                    marker=dict(size=8)
                ))
                
                fig_values.add_trace(go.Scatter(
                    x=scenario_labels[:len(scenarios_data)],
                    y=[d['Valor Final Bruto'] for d in scenarios_data],
                    mode='lines+markers',
                    name='Valor Bruto',
                    line=dict(color='lightblue', width=2, dash='dash'),
                    marker=dict(size=6)
                ))
                
                fig_values.update_layout(
                    title="Evolução do Valor Final por Prazo",
                    xaxis_title="Prazo do Investimento",
                    yaxis_title="Valor Final (R$)",
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig_values, use_container_width=True)
            
            with chart_tabs[1]:
                # Returns comparison chart
                fig_returns = make_subplots(
                    rows=1, cols=2,
                    subplot_titles=('Retornos do Período', 'Retornos Anuais'),
                    specs=[[{"secondary_y": False}, {"secondary_y": False}]]
                )
                
                # Period returns
                fig_returns.add_trace(
                    go.Bar(
                        x=scenario_labels[:len(scenarios_data)],
                        y=[float(d['Retorno Líq. Atual Período'].rstrip('%')) for d in scenarios_data],
                        name='Atual - Período',
                        marker_color='orange',
                        opacity=0.7
                    ),
                    row=1, col=1
                )
                
                fig_returns.add_trace(
                    go.Bar(
                        x=scenario_labels[:len(scenarios_data)],
                        y=[float(d['Retorno Líq. Novo Período'].rstrip('%')) for d in scenarios_data],
                        name='Novo - Período',
                        marker_color='green',
                        opacity=0.7
                    ),
                    row=1, col=1
                )
                
                # Annual returns
                fig_returns.add_trace(
                    go.Bar(
                        x=scenario_labels[:len(scenarios_data)],
                        y=[float(d['Taxa Líq. Atual Anual'].rstrip('%')) for d in scenarios_data],
                        name='Atual - Anual',
                        marker_color='darkorange',
                        opacity=0.7,
                        showlegend=False
                    ),
                    row=1, col=2
                )
                
                fig_returns.add_trace(
                    go.Bar(
                        x=scenario_labels[:len(scenarios_data)],
                        y=[float(d['Taxa Líq. Nova Anual'].rstrip('%')) for d in scenarios_data],
                        name='Novo - Anual',
                        marker_color='darkgreen',
                        opacity=0.7,
                        showlegend=False
                    ),
                    row=1, col=2
                )
                
                fig_returns.update_layout(
                    height=400,
                    barmode='group'
                )
                fig_returns.update_yaxes(title_text="Retorno (%)", row=1, col=1)
                fig_returns.update_yaxes(title_text="Taxa Anual (%)", row=1, col=2)
                
                st.plotly_chart(fig_returns, use_container_width=True)
            
            with chart_tabs[2]:
                # CDI comparison chart
                fig_cdi = go.Figure()
                
                fig_cdi.add_trace(go.Scatter(
                    x=scenario_labels[:len(scenarios_data)],
                    y=[float(d['% CDI Líq. Atual'].rstrip('%')) for d in scenarios_data],
                    mode='lines+markers',
                    name='% CDI Atual',
                    line=dict(color='orange', width=3),
                    marker=dict(size=8)
                ))
                
                fig_cdi.add_trace(go.Scatter(
                    x=scenario_labels[:len(scenarios_data)],
                    y=[float(d['% CDI Líq. Novo'].rstrip('%')) for d in scenarios_data],
                    mode='lines+markers',
                    name='% CDI Novo',
                    line=dict(color='green', width=3),
                    marker=dict(size=8)
                ))
                
                # Add reference line at 100% CDI
                fig_cdi.add_hline(
                    y=100, 
                    line_dash="dash", 
                    line_color="gray",
                    annotation_text="100% CDI"
                )
                
                fig_cdi.update_layout(
                    title="Equivalência em % do CDI por Prazo",
                    xaxis_title="Prazo do Investimento",
                    yaxis_title="% do CDI",
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig_cdi, use_container_width=True)
            
            with chart_tabs[3]:
                # Differences chart
                fig_diff = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=('Diferença Absoluta (R$)', 'Diferença Percentual (%)'),
                    vertical_spacing=0.12
                )
                
                # Absolute difference
                colors = ['green' if d['Diferença (R$)'] >= 0 else 'red' for d in scenarios_data]
                
                fig_diff.add_trace(
                    go.Bar(
                        x=scenario_labels[:len(scenarios_data)],
                        y=[d['Diferença (R$)'] for d in scenarios_data],
                        marker_color=colors,
                        name='Diferença Absoluta',
                        text=[format_currency(d['Diferença (R$)']) for d in scenarios_data],
                        textposition='auto'
                    ),
                    row=1, col=1
                )
                
                # Percentage difference
                colors_pct = ['green' if d['Diferença (%)'] >= 0 else 'red' for d in scenarios_data]
                
                fig_diff.add_trace(
                    go.Bar(
                        x=scenario_labels[:len(scenarios_data)],
                        y=[d['Diferença (%)'] for d in scenarios_data],
                        marker_color=colors_pct,
                        name='Diferença Percentual',
                        text=[f"{d['Diferença (%)']:.2f}%" for d in scenarios_data],
                        textposition='auto',
                        showlegend=False
                    ),
                    row=2, col=1
                )
                
                fig_diff.update_layout(height=500)
                fig_diff.update_yaxes(title_text="Diferença (R$)", row=1, col=1)
                fig_diff.update_yaxes(title_text="Diferença (%)", row=2, col=1)
                
                st.plotly_chart(fig_diff, use_container_width=True)
        
        # Summary insights
        st.markdown("### 🎯 Insights da Análise")
        
        # Find best and worst scenarios
        best_scenario = max(scenarios_data, key=lambda x: x['Diferença (R$)'])
        worst_scenario = min(scenarios_data, key=lambda x: x['Diferença (R$)'])
        
        col_insight1, col_insight2 = st.columns(2)
        
        with col_insight1:
            if best_scenario['Diferença (R$)'] > 0:
                st.success(f"""
                ✅ **Melhor Cenário: {best_scenario['Prazo']}**
                - Economia: {format_currency(best_scenario['Diferença (R$)'])}
                - Diferença: {best_scenario['Diferença (%)']:.2f}%
                - CDI Líquido: {best_scenario['% CDI Líq. Novo']} vs {best_scenario['% CDI Líq. Atual']}
                """)
            else:
                st.info(f"""
                📊 **Menor Perda: {best_scenario['Prazo']}**
                - Diferença: {format_currency(best_scenario['Diferença (R$)'])}
                - Impacto: {best_scenario['Diferença (%)']:.2f}%
                """)
        
        with col_insight2:
            if worst_scenario['Diferença (R$)'] < 0:
                st.error(f"""
                ❌ **Pior Cenário: {worst_scenario['Prazo']}**
                - Perda: {format_currency(abs(worst_scenario['Diferença (R$)']))}
                - Diferença: {worst_scenario['Diferença (%)']:.2f}%
                - CDI Líquido: {worst_scenario['% CDI Líq. Novo']} vs {worst_scenario['% CDI Líq. Atual']}
                """)
            else:
                st.info(f"""
                📊 **Menor Ganho: {worst_scenario['Prazo']}**
                - Economia: {format_currency(worst_scenario['Diferença (R$)'])}
                - Diferença: {worst_scenario['Diferença (%)']:.2f}%
                """)
