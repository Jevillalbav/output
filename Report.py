import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="IRR Forecast")
st.title("Real Estate Report")

st.sidebar.markdown("------")
st.sidebar.title("Top Submarkets")

#3 hacer dos columns para las primeras tablas y depsues hacer una row para las graficas

# Load data
cashflows = pd.read_csv("cashflows.csv", index_col=0)
analises = pd.read_csv("analises.csv", index_col=0)
analises['State'] = analises["Market"].str.split(" - ").str[1]
analises['Market'] = analises["Market"].str.split(" - ").str[0]
summaries = pd.read_csv("summaries.csv", index_col=0)
summaries['State'] = summaries["Market"].str.split(" - ").str[1]
summaries['Market'] = summaries["Market"].str.split(" - ").str[0]

st.session_state.top_better = 3
top = st.sidebar.slider("Top Better", 5, 25, 10, 5)
st.session_state.top_better = top

st.session_state.filter_population = "All"
filter_population = st.sidebar.selectbox("Population Filter", ["All","> 8M","> 4M" ,"> 2M", "> 1M", "> 500K", "< 500K"], index=0)
st.session_state.filter_population = filter_population


st.sidebar.markdown("------")
st.sidebar.title("Submarket Analysis")


state = st.sidebar.selectbox("State", analises["State"].sort_values().unique() ,  index=0)
market = st.sidebar.selectbox("Market", analises[analises["State"] == state]["Market"].unique(), index=0)
submarket = st.sidebar.selectbox("Submarket", analises[analises["Market"] == market]["Submarket"].unique(), index=0)

st.session_state.geo = analises.loc[(analises["Market"] == market) & (analises["Submarket"] == submarket)].index[0]


def show_summary():
    st.subheader("Summary")
  
    if st.session_state.filter_population == "All":
        a = analises.copy()
    elif st.session_state.filter_population == "> 8M":
        a = analises[analises["Population"] > 8000000].copy()
    elif st.session_state.filter_population == "> 4M":
        a = analises[analises["Population"] > 4000000].copy()
    elif st.session_state.filter_population == "> 2M":
        a = analises[analises["Population"] > 2000000].copy()
    elif st.session_state.filter_population == "> 1M":
        a = analises[analises["Population"] > 1000000].copy()
    elif st.session_state.filter_population == "> 500K":
        a = analises[(analises["Population"] > 500000)].copy()
    elif st.session_state.filter_population == "< 500K":
        a = analises[analises["Population"] < 500000].copy()
        
    x = a.sort_values("XIRR", ascending=False).head(st.session_state.top_better)
    x.index.name = "Submarket"
    x['CAGR'] = x['CAGR'].map("{:.2%}".format)
    x['NOI Cap Rate Comp.'] = x['NOI Cap Rate Comp.'].map("{:.2%}".format)
    x['Fixed Interest Rate'] = x['Fixed Interest Rate'].map("{:.2%}".format)
    x['Opt. Cash Flow'] = x['Opt. Cash Flow'].map("${:,.2%}".format)
    x['XIRR'] = x['XIRR'].map("{:.2%}".format)
    x['Equity Multiple'] = x['Equity Multiple'].map("{:.2f}".format) + "x"

    return st.dataframe(x.drop(columns=["Period", 'Years']).reset_index(drop=True)[['State','Market', 'Population', 'Submarket'
                                                                                     , 'CAGR', 'NOI Cap Rate Comp.', 'Fixed Interest Rate',
                                                                                        'Opt. Cash Flow', 'Mkt Cap Rate Apr. bp', 
                                                                                        'XIRR', 'Equity Multiple']]
                  , height= 38 + (35 * st.session_state.top_better), width= 1250, 
                  )             
    
st.subheader("Best Submarkets")
show_summary()
    
st.markdown("------")
st.subheader("Submarket Analysis")
st.write(f"Selected: {market} - {submarket}")

def show_cashflow():
    b = cashflows[(cashflows["geography_name"] == st.session_state.geo)].copy().sort_values("date")
    c = b.copy()
    irr = b['irr'].iloc[-1]
    b = b[['date','price', 'equity', 'debt', 'revenue', 'debt_service', 'pay_off', 'valuation','cashflow']]
    b['date'] = pd.to_datetime(b['date'])
    b = b.sort_values("date", ascending=True)
    b['date'] = b['date'].dt.strftime("%Y-%m")

    b = b.set_index("date")
    b['price'] = b['price'].map("${:,.0f}".format)
    b['equity'] = b['equity'].map("${:,.0f}".format)
    b['debt'] = b['debt'].map("${:,.0f}".format)
    b['revenue'] = b['revenue'].map("${:,.0f}".format)
    b['debt_service'] = b['debt_service'].map("${:,.0f}".format)
    b['pay_off'] = b['pay_off'].map("${:,.0f}".format)
    b['valuation'] = b['valuation'].map("${:,.0f}".format)
    b['cashflow'] = b['cashflow'].map("${:,.0f}".format)

    b.columns = [ 'House Price', 'Equity', 'Debt', 'Revenue', 'Debt Service', 'Pay Off', 'Valuation', 'Total Cash Flow']

    fig = go.Figure()
    price = b['House Price'].str.replace("$","").str.replace(",","").astype(float)
    price_ret = price.pct_change().fillna(0).add(1).cumprod().sub(1)
    rent = b['Revenue'].str.replace("$","").str.replace(",","").astype(float)
    rent_ret = rent.pct_change().fillna(0).add(1).cumprod().sub(1)
    cash = b['Total Cash Flow'].str.replace("$","").str.replace(",","").astype(float)

    fig.update_layout(
        width=1200,
        height=600,
        #title = "Cash Flows",
        xaxis_title="Date",
        xaxis_domain=[0.1, 0.85],
        xaxis_dtick='M6',
        xaxis_tickformat='%Y-%m',
        xaxis_tickangle=-45,
        yaxis = dict(
            title = "Amount",
            tickprefix = "$",
            range=[ cash.min() * 2, cash.max() * 2],
            position=0.1,
            showgrid=False

        ),
        yaxis2 = dict(
            title = "Price",
            tickprefix = "$",
            overlaying='y1',
            side='right',
            position=0.85,
            showgrid=False,
            range=[ price.min() * 0.5, price.max() * 1.5],
            visible = False
        ),

        yaxis3 = dict(
            title = "Rent",
            tickprefix = "$",
            overlaying='y1',
            position=0.93,
            side='right',
            showgrid=False,
            range = [rent.min() * 0.5, rent.max() * 1.8],
            visible = False

        ),


        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x',
        showlegend=False,

    )

    cash_color = ["green" if x > 0 else "red" for x in cash]

    fig.add_trace(go.Bar(x=b.index, y=cash, 
                          name="Cash", yaxis='y', marker_color= cash_color, hoverinfo='skip',
                            text=b['Total Cash Flow'], textposition='outside', textfont=dict(color='white', size=12)))
    fig.add_trace(go.Scatter(x=b.index, y=price, name="Price",
                              yaxis='y2', mode='lines', marker=dict(color='lightblue'),
                                text= price_ret.map("{:.2%}".format),
                                hoverinfo= 'name+y+text',))
    fig.add_trace(go.Scatter(x=b.iloc[1:].index, y=rent.iloc[1:], name="Rent",
                                yaxis='y3', mode='lines', marker=dict(color='lightgreen'),
                                    #text= rent_ret.iloc[1:].map("{:.2%}".format),
                                    hoverinfo= 'name+y',))

    return b , fig , irr
x = show_cashflow()
st.metric('IRR expected:',format(x[2], ".2%"))

# with tab2:
col1, col2 = st.columns(2)


def show_cashflow_2():
    b = cashflows[(cashflows["geography_name"] == st.session_state.geo)].copy().sort_values("date")

    c = b[['date', 'price', 'mo_rent']].set_index("date").copy()
    c.index = pd.to_datetime(c.index)
    c = c.round(0).resample("M").last().interpolate(method='pchip')
    
    c_ret = c.pct_change().fillna(0).add(1).cumprod().sub(1)
    c_ret = c_ret.applymap("{:.2%}".format)

    a = analises.loc[st.session_state.geo,:].drop(index=["Market", "State", "Population", "Submarket"]).copy()
    a.loc["CAGR"] = format(a.loc["CAGR"], ".2%")
    a.loc["NOI Cap Rate Comp."] = format(a.loc["NOI Cap Rate Comp."], ".2%")
    a.loc["Fixed Interest Rate"] = format(a.loc["Fixed Interest Rate"], ".2%")
    a.loc["Opt. Cash Flow"] = format(a.loc["Opt. Cash Flow"], ".2%")
    a.loc["XIRR"] = format(a.loc["XIRR"], ".2%")
    a.loc["Equity Multiple"] = format(a.loc["Equity Multiple"], ".2f") + "x"

    s = summaries.loc[st.session_state.geo].copy()
    s = s.drop(index=["Market", "State", "Population", "Submarket"])
    s.loc["LTV"] = format(s.loc["LTV"], ".2%")
    s.loc["Price"] = "$" + format(s.loc["Price"], ",.0f")
    s.loc["Loan"] = "$" + format(s.loc["Loan"], ",.0f")
    s.loc["Equity"] = "$" + format(s.loc["Equity"], ",.0f")
    s.loc["SOFR"] = format(s.loc["SOFR"], ".2%")
    s.loc["Spread"] = format(s.loc["Spread"], ".2%")
    s.loc["Net_Rate"] = format(s.loc["Net_Rate"], ".2%")

    return c, c_ret , a , s

with col1:
    st.subheader("Summary")
    st.dataframe(show_cashflow_2()[3])

with col2:
    st.subheader("Metrics")
    st.dataframe(show_cashflow_2()[2] )


st.subheader("Cash Flows")
st.plotly_chart(x[1])
st.dataframe(x[0], height= 38 + (35 * 6), width= 1200, )
    





