"""Parcl Buyer Intelligence Platform — premium Streamlit dashboard.
Run from project root: streamlit run app/Real_Estate_Buyer_Intelligence_Dashboard.py
"""
from pathlib import Path
import sys
import json
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "src"))

st.set_page_config(page_title="Parcl | Buyer Intelligence", page_icon="🏙️", layout="wide", initial_sidebar_state="expanded")

# -----------------------------------------------------------------------------
# PREMIUM THEME
# -----------------------------------------------------------------------------
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{--bg:#06101f;--panel:#0b1930;--panel2:#0d203d;--line:#173963;--text:#f4f8ff;--muted:#91a6c5;--blue:#4f7cff;--cyan:#20d9ff;--green:#20d3a2;--orange:#ffb340;--purple:#a875ff;--pink:#f05cff}
html,body,[class*="css"]{font-family:'Inter',sans-serif}
.stApp{background:radial-gradient(circle at 78% 0%,rgba(55,99,255,.13),transparent 28%),linear-gradient(135deg,#040b16 0%,#071426 55%,#06101f 100%);color:var(--text)}
[data-testid="stHeader"]{background:transparent}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#061225 0%,#08182f 100%);border-right:1px solid #15345c}
[data-testid="stSidebar"] *{color:#edf4ff!important}
[data-testid="stSidebar"] .stCaption{color:#7f96b8!important}
.block-container{padding-top:1.25rem;padding-bottom:2rem;max-width:1600px}
.brand{padding:8px 4px 18px;border-bottom:1px solid #173252;margin-bottom:14px}
.brand-mark{display:flex;align-items:center;gap:10px}.brand-icon{width:38px;height:38px;border-radius:12px;background:linear-gradient(135deg,#6246ff,#18cfff);display:flex;align-items:center;justify-content:center;font-size:21px;box-shadow:0 8px 24px rgba(79,124,255,.3)}
.brand-name{font-size:23px;font-weight:800;letter-spacing:-.8px}.brand-sub{font-size:10px;color:#8da4c6!important;text-transform:uppercase;letter-spacing:1.2px;margin-top:2px}
.side-label{font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:#7189aa!important;margin:18px 0 8px}
div[data-testid="stRadio"] label{padding:8px 10px;border-radius:10px;font-size:13px}
.hero{position:relative;overflow:hidden;border:1px solid #1c4779;border-radius:22px;padding:24px 28px;margin:0 0 18px;background:linear-gradient(115deg,rgba(13,35,66,.98),rgba(9,25,49,.94));box-shadow:0 20px 60px rgba(0,0,0,.22)}
.hero:after{content:'';position:absolute;width:320px;height:320px;right:-80px;top:-150px;background:radial-gradient(circle,rgba(32,217,255,.22),transparent 66%);pointer-events:none}
.kicker{font-size:10px;text-transform:uppercase;letter-spacing:2px;color:#6edbff;font-weight:700}.hero h1{font-size:34px;line-height:1.08;margin:7px 0;color:#fff;letter-spacing:-1.4px}.hero p{margin:0;color:#a9bbd5;font-size:13px}.hero-chip{display:inline-block;margin-top:14px;padding:6px 10px;border-radius:999px;background:#0b2b4a;border:1px solid #1d527f;color:#8fdfff;font-size:11px}
.kpi{height:126px;border:1px solid #17436f;border-radius:17px;background:linear-gradient(145deg,#0d2342,#091a32);padding:16px 17px;box-shadow:inset 0 1px rgba(255,255,255,.03),0 12px 30px rgba(0,0,0,.13);position:relative;overflow:hidden}.kpi:after{content:'';position:absolute;right:-30px;bottom:-45px;width:120px;height:120px;border-radius:50%;background:rgba(79,124,255,.08)}.kpi-label{font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#8299bb}.kpi-value{font-size:27px;font-weight:800;color:#fff;margin-top:10px}.kpi-note{font-size:10px;color:#8ca4c5;margin-top:4px}.kpi-accent{font-size:11px;color:#54e6c0;font-weight:700}
.panel{border:1px solid #173e69;border-radius:17px;background:linear-gradient(145deg,rgba(11,28,52,.98),rgba(7,21,39,.98));padding:16px 17px;box-shadow:0 12px 34px rgba(0,0,0,.13);margin-bottom:16px}.panel-title{font-size:15px;font-weight:750;color:#f5f8ff}.panel-sub{font-size:10px;color:#7890b2;margin-top:3px}.insight{border:1px solid #1a426d;background:linear-gradient(90deg,#0c2340,#0a1c34);border-radius:13px;padding:11px 13px;margin:8px 0;color:#c8d6e9;font-size:11px}.insight b{color:#fff}.tag{display:inline-block;padding:4px 7px;border-radius:999px;background:#102d4f;border:1px solid #1d4c78;color:#8fcfff;font-size:9px;margin:2px}
.stButton button,.stDownloadButton button{background:#0d2748!important;color:#eef6ff!important;border:1px solid #24527f!important;border-radius:10px!important;font-weight:650!important}.stButton button:hover,.stDownloadButton button:hover{border-color:#4f7cff!important;background:#12345b!important}
[data-testid="stDataFrame"]{border:1px solid #173e69;border-radius:12px;overflow:hidden}
[data-testid="stMetric"]{background:#0c203b;border:1px solid #173e69;border-radius:13px}
div[data-baseweb="select"]>div{background:#0b203b;border-color:#20466e;color:white}
hr{border-color:#17365a!important}
.footer{border-top:1px solid #17365a;margin-top:25px;padding-top:12px;color:#667f9f;font-size:10px;display:flex;justify-content:space-between}
.empty{padding:45px;text-align:center;border:1px dashed #28527d;border-radius:16px;color:#8ea5c3;background:#091a30}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DATA
# -----------------------------------------------------------------------------
@st.cache_data
def _load_data():
    p = BASE / "data" / "processed" / "Buyer_Segmentation_Results.csv"
    if not p.exists():
        raise FileNotFoundError(f"Missing processed dataset: {p}")
    df = pd.read_csv(p)
    for c in ["age","satisfaction_score","loan_flag","investment_flag","is_company","total_purchases","total_spend","avg_purchase_price","avg_floor_area","n_towers","pct_apartment"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

@st.cache_resource
def _load_meta():
    p = BASE / "models" / "Buyer_Segmentation_Model_Metadata.pkl"
    return joblib.load(p) if p.exists() else {}

df = _load_data(); meta = _load_meta()
ROBUSTNESS_PATH = BASE / "outputs" / "tables" / "11_Model_Robustness_Summary.json"
robustness = json.loads(ROBUSTNESS_PATH.read_text(encoding="utf-8")) if ROBUSTNESS_PATH.exists() else {}

REQUIRED = ["client_id","client_type","country","region","acquisition_purpose","satisfaction_score","loan_applied","referral_channel","age","loan_flag","investment_flag","is_company","total_purchases","total_spend","avg_purchase_price","avg_floor_area","n_towers","pct_apartment","segment_name"]
missing = [c for c in REQUIRED if c not in df.columns]
if missing:
    st.error("Dataset is missing: " + ", ".join(missing)); st.stop()

SEGMENTS = df["segment_name"].value_counts().index.tolist()
SEGMENT_COLORS = {"Value-Conscious Home Buyers":"#4f7cff","High-Volume / Frequent Buyers":"#20d3a2","Premium / High-Value Buyers":"#ffb340","Corporate Buyers":"#a875ff"}
PLOT_TEMPLATE = "plotly_dark"
# Plotly's locationmode="country names" resolves full names reliably but is
# inconsistent with abbreviations like "USA"/"UK" across versions - map to
# explicit ISO-3 codes instead so the choropleth never silently drops a country.
ISO3 = {"USA":"USA","Canada":"CAN","Germany":"DEU","Belgium":"BEL","Mexico":"MEX",
        "Russia":"RUS","UK":"GBR","Denmark":"DNK","France":"FRA","Australia":"AUS"}

def money(v):
    v=float(v or 0)
    if abs(v)>=1e9:return f"${v/1e9:.2f}B"
    if abs(v)>=1e6:return f"${v/1e6:.1f}M"
    if abs(v)>=1e3:return f"${v/1e3:.0f}K"
    return f"${v:,.0f}"

def pct(v): return f"{100*float(v):.1f}%"

def chart(fig, height=300):
    fig.update_layout(template=PLOT_TEMPLATE,height=height,margin=dict(l=8,r=8,t=34,b=8),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(family="Inter",size=10,color="#b8c9df"),legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(size=10)),hoverlabel=dict(bgcolor="#0a1b32",font_color="#fff"))
    fig.update_xaxes(showgrid=False,zeroline=False,linecolor="#1b3b60")
    fig.update_yaxes(gridcolor="#163453",zeroline=False,linecolor="#1b3b60")
    return fig

def panel_title(title, sub=""):
    st.markdown(f'<div class="panel-title">{title}</div>' + (f'<div class="panel-sub">{sub}</div>' if sub else ""), unsafe_allow_html=True)

def kpi(label, value, note, accent=""):
    st.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-note"><span class="kpi-accent">{accent}</span> {note}</div></div>', unsafe_allow_html=True)

def segment_profile(view):
    return view.groupby("segment_name").agg(Buyers=("client_id","count"),Avg_Age=("age","mean"),Avg_Spend=("total_spend","mean"),Investment_Rate=("investment_flag","mean"),Loan_Rate=("loan_flag","mean"),Satisfaction=("satisfaction_score","mean"),Total_Spend=("total_spend","sum")).reset_index()

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
st.sidebar.markdown('<div class="brand"><div class="brand-mark"><div class="brand-icon">⌂</div><div><div class="brand-name">Parcl</div><div class="brand-sub">Buyer Intelligence Platform</div></div></div></div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="side-label">Workspace</div>', unsafe_allow_html=True)
pages=["Executive Overview","Buyer Segmentation","Geographic Intelligence","Investment Profiling","Segment Insights","Customer Explorer","Model Information"]
page=st.sidebar.radio("Navigation",pages,label_visibility="collapsed")
st.sidebar.markdown('<div class="side-label">Filters</div>', unsafe_allow_html=True)

def opts(col): return sorted(df[col].dropna().astype(str).unique().tolist())
country=st.sidebar.multiselect("Country",opts("country"),placeholder="All countries")
region=st.sidebar.multiselect("Region",opts("region"),placeholder="All regions")
purpose=st.sidebar.multiselect("Acquisition Purpose",opts("acquisition_purpose"),placeholder="All purposes")
ctype=st.sidebar.multiselect("Client Type",opts("client_type"),placeholder="All client types")
segment=st.sidebar.multiselect("Buyer Segment",SEGMENTS,placeholder="All segments")

view=df.copy()
for col, vals in [("country",country),("region",region),("acquisition_purpose",purpose),("client_type",ctype),("segment_name",segment)]:
    if vals: view=view[view[col].astype(str).isin(vals)]

st.sidebar.markdown("<hr>",unsafe_allow_html=True)
st.sidebar.markdown(f'<div class="side-label">Dataset Status</div><div class="tag">● CONNECTED</div><div style="font-size:11px;color:#8ca4c5!important;margin-top:8px">{len(view):,} buyers in current view<br>{len(df):,} buyers in source dataset<br>10,000 property transactions</div>',unsafe_allow_html=True)

if view.empty:
    st.markdown('<div class="empty"><h3>No buyers match the selected filters.</h3><p>Clear one or more filters to restore the dashboard.</p></div>',unsafe_allow_html=True); st.stop()

# -----------------------------------------------------------------------------
# COMMON HEADER
# -----------------------------------------------------------------------------
st.markdown(f'<div class="hero"><div class="kicker">REAL ESTATE MARKET INTELLIGENCE</div><h1>{page}</h1><p>AI-assisted buyer segmentation, investment profiling and market intelligence — built from the project dataset.</p><span class="hero-chip">◉ {len(view):,} buyers in current view</span> <span class="hero-chip">◈ {view["segment_name"].nunique()} segments</span></div>',unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# EXECUTIVE OVERVIEW
# -----------------------------------------------------------------------------
if page=="Executive Overview":
    prof=segment_profile(view); invest=view.investment_flag.mean(); loan=view.loan_flag.mean(); spend=view.total_spend.sum(); sat=view.satisfaction_score.mean()
    cols=st.columns(6)
    vals=[("Total Buyers",f"{len(view):,}","Filtered buyer population",""),("Buyer Segments",f"{view.segment_name.nunique()}","Segments represented",""),("Investment Buyers",pct(invest),f"{int(view.investment_flag.sum()):,} buyers",""),("Loan Applicants",pct(loan),f"{int(view.loan_flag.sum()):,} buyers",""),("Total Spend",money(spend),"Aggregated purchase value",""),("Avg Satisfaction",f"{sat:.2f} / 5","Customer satisfaction","High" if sat>=3 else "")]
    for c,(a,b,n,ac) in zip(cols,vals):
        with c:kpi(a,b,n,ac)
    st.write("")
    a,b,c=st.columns([1.15,1.1,1.15])
    with a:
        st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Buyer Segment Distribution","Current filtered population")
        fig=px.pie(prof,names="segment_name",values="Buyers",hole=.64,color="segment_name",color_discrete_map=SEGMENT_COLORS)
        fig.update_traces(textinfo="percent",textfont_size=11,marker=dict(line=dict(color="#08172a",width=3)))
        fig.add_annotation(text=f"<b>{len(view):,}</b><br><span style='font-size:10px'>BUYERS</span>",showarrow=False,font=dict(size=17,color="#fff"))
        st.plotly_chart(chart(fig,280),width='stretch',config={"displayModeBar":False})
        st.markdown('</div>',unsafe_allow_html=True)
    with b:
        st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Total Spend by Segment","Portfolio contribution")
        s=prof.sort_values("Total_Spend",ascending=True)
        fig=px.bar(s,x="Total_Spend",y="segment_name",orientation="h",color="segment_name",color_discrete_map=SEGMENT_COLORS,text="Total_Spend")
        fig.update_traces(texttemplate="$%{text:.3s}",textposition="outside",cliponaxis=False)
        fig.update_layout(showlegend=False,xaxis_title=None,yaxis_title=None)
        st.plotly_chart(chart(fig,280),width='stretch',config={"displayModeBar":False})
        st.markdown('</div>',unsafe_allow_html=True)
    with c:
        st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Global Buyer Distribution","Country concentration")
        geo=view.groupby("country").agg(Buyers=("client_id","count"),Spend=("total_spend","sum"),Investment=("investment_flag","mean")).reset_index().sort_values("Buyers",ascending=False).head(10)
        geo["iso3"]=geo["country"].map(ISO3)
        fig=px.choropleth(geo,locations="iso3",locationmode="ISO-3",color="Buyers",color_continuous_scale="Blues",hover_name="country",hover_data={"Buyers":":,","Spend":":.3s","Investment":":.1%","iso3":False})
        fig.update_layout(coloraxis_showscale=False,geo=dict(bgcolor="rgba(0,0,0,0)",showframe=False,showcoastlines=False,projection_type="natural earth"))
        st.plotly_chart(chart(fig,280),width='stretch',config={"displayModeBar":False})
        st.markdown('</div>',unsafe_allow_html=True)

    left,right=st.columns([1.65,1])
    with left:
        st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Buyer Segment Overview","Decision-ready segment profile")
        t=prof.copy(); t["Avg_Age"]=t.Avg_Age.round(1); t["Avg_Spend"]=t.Avg_Spend.map(money); t["Investment_Rate"]=t.Investment_Rate.map(pct); t["Loan_Rate"]=t.Loan_Rate.map(pct); t["Satisfaction"]=t.Satisfaction.round(2); t["Total_Spend"]=t.Total_Spend.map(money)
        t.columns=["Segment","Buyers","Avg Age","Avg Spend","Investment %","Loan %","Satisfaction","Total Spend"]
        st.dataframe(t,width='stretch',hide_index=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Key Insights","Automatically derived from the current view")
        top_spend=prof.loc[prof.Avg_Spend.idxmax()]; largest=prof.loc[prof.Buyers.idxmax()]; inv=prof.loc[prof.Investment_Rate.idxmax()]
        for txt in [f"<b>{top_spend.segment_name}</b> has the highest average spend at <b>{money(top_spend.Avg_Spend)}</b>.",f"<b>{largest.segment_name}</b> is the largest segment with <b>{int(largest.Buyers):,}</b> buyers ({pct(largest.Buyers/len(view))}).",f"<b>{inv.segment_name}</b> shows the highest investment rate at <b>{pct(inv.Investment_Rate)}</b>.",f"The filtered portfolio contains <b>{money(spend)}</b> in aggregated spend and an average satisfaction of <b>{sat:.2f}/5</b>."]:
            st.markdown(f'<div class="insight">✦ {txt}</div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

    a,b,c=st.columns(3)
    with a:
        st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Age Distribution")
        bins=[0,25,35,45,55,65,200]; labels=["<25","25–34","35–44","45–54","55–64","65+"]
        age=view.copy(); age["Age Group"]=pd.cut(age.age,bins=bins,labels=labels,right=False)
        ad=age.groupby("Age Group",observed=False).size().reset_index(name="Buyers")
        fig=px.bar(ad,x="Age Group",y="Buyers",text="Buyers")
        fig.update_traces(marker_color="#4f7cff",textposition="outside")
        st.plotly_chart(chart(fig,250),width='stretch',config={"displayModeBar":False}); st.markdown('</div>',unsafe_allow_html=True)
    with b:
        st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Investment vs End Use")
        invn=int(view.investment_flag.sum()); endn=len(view)-invn
        fig=go.Figure(go.Pie(labels=["Investment","End Use"],values=[invn,endn],hole=.68,marker=dict(colors=["#20d3a2","#25456e"]),textinfo="percent")); fig.add_annotation(text=f"<b>{pct(invest)}</b><br><span style='font-size:10px'>INVESTMENT</span>",showarrow=False,font=dict(size=16,color="#fff"))
        st.plotly_chart(chart(fig,250),width='stretch',config={"displayModeBar":False}); st.markdown('</div>',unsafe_allow_html=True)
    with c:
        st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Loan Applicants by Segment")
        lr=prof.sort_values("Loan_Rate")
        fig=px.bar(lr,x="Loan_Rate",y="segment_name",orientation="h",color="segment_name",color_discrete_map=SEGMENT_COLORS,text="Loan_Rate")
        fig.update_traces(texttemplate="%{text:.0%}",textposition="outside"); fig.update_layout(showlegend=False,xaxis_tickformat=".0%",xaxis_title=None,yaxis_title=None)
        st.plotly_chart(chart(fig,250),width='stretch',config={"displayModeBar":False}); st.markdown('</div>',unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BUYER SEGMENTATION
# -----------------------------------------------------------------------------
elif page=="Buyer Segmentation":
    focus=st.selectbox("Focus on a segment",["All"]+SEGMENTS)
    segview=view if focus=="All" else view[view.segment_name==focus]
    p=segment_profile(segview)
    a,b=st.columns([1.25,1])
    with a:
        st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Segment Landscape","Size, spend and investment behavior")
        q=p.sort_values("Buyers",ascending=True)
        fig=go.Figure()
        fig.add_trace(go.Bar(y=q.segment_name,x=q.Buyers,name="Buyers",orientation="h",marker_color="#4f7cff"))
        fig.add_trace(go.Bar(y=q.segment_name,x=q.Total_Spend/q.Total_Spend.max()*q.Buyers.max(),name="Relative spend",orientation="h",marker_color="#20d3a2",opacity=.65))
        fig.update_layout(barmode="overlay",xaxis_title=None,yaxis_title=None,legend=dict(orientation="h",y=1.12,x=0))
        st.plotly_chart(chart(fig,330),width='stretch',config={"displayModeBar":False}); st.markdown('</div>',unsafe_allow_html=True)
    with b:
        st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Segment Signal Matrix","Higher is stronger")
        m=p.set_index("segment_name")[["Investment_Rate","Loan_Rate","Satisfaction"]]
        m.columns=["Investment","Loan","Satisfaction"]
        fig=px.imshow(m,aspect="auto",color_continuous_scale="Blues",text_auto=".0%")
        fig.update_layout(coloraxis_showscale=False,xaxis_title=None,yaxis_title=None)
        st.plotly_chart(chart(fig,330),width='stretch',config={"displayModeBar":False}); st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Segment Comparison","Actual metrics from the current filtered data")
    display=p.copy(); display["Avg Spend"]=display.Avg_Spend.map(money); display["Total Spend"]=display.Total_Spend.map(money); display["Investment Rate"]=display.Investment_Rate.map(pct); display["Loan Rate"]=display.Loan_Rate.map(pct); display["Avg Age"]=display.Avg_Age.round(1); display["Satisfaction"]=display.Satisfaction.round(2); display=display[["segment_name","Buyers","Avg Age","Avg Spend","Investment Rate","Loan Rate","Satisfaction","Total Spend"]]; display.columns=["Segment","Buyers","Avg Age","Avg Spend","Investment %","Loan %","Satisfaction","Total Spend"]
    st.dataframe(display,width='stretch',hide_index=True); st.markdown('</div>',unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# GEOGRAPHIC INTELLIGENCE
# -----------------------------------------------------------------------------
elif page=="Geographic Intelligence":
    metric=st.radio("Map metric",["Client count","Investment rate","Avg total spend"],horizontal=True)
    geo=view.groupby("country").agg(Buyers=("client_id","count"),Investment=("investment_flag","mean"),AvgSpend=("total_spend","mean"),TotalSpend=("total_spend","sum")).reset_index()
    geo["iso3"]=geo["country"].map(ISO3)
    val={"Client count":"Buyers","Investment rate":"Investment","Avg total spend":"AvgSpend"}[metric]
    a,b=st.columns([1.45,.85])
    with a:
        st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Global Buyer Distribution",metric)
        fig=px.choropleth(geo,locations="iso3",locationmode="ISO-3",color=val,color_continuous_scale="Turbo",hover_name="country",hover_data={"Buyers":":,","Investment":":.1%","AvgSpend":":.2s","iso3":False})
        fig.update_layout(coloraxis_colorbar=dict(thickness=10,len=.55,title=None),geo=dict(bgcolor="rgba(0,0,0,0)",showframe=False,showcoastlines=False,landcolor="#102643"))
        st.plotly_chart(chart(fig,420),width='stretch',config={"displayModeBar":False}); st.markdown('</div>',unsafe_allow_html=True)
    with b:
        st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Country Leaders","Top markets in current view")
        top=geo.sort_values(val,ascending=False).head(10).copy(); top["Investment"]=top.Investment.map(pct); top["AvgSpend"]=top.AvgSpend.map(money); top["TotalSpend"]=top.TotalSpend.map(money)
        st.dataframe(top.rename(columns={"country":"Country","Buyers":"Buyers","Investment":"Investment %","AvgSpend":"Avg Spend","TotalSpend":"Total Spend"})[["Country","Buyers","Investment %","Avg Spend","Total Spend"]],width='stretch',hide_index=True); st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Regional Concentration","Buyer count by region")
    reg=view.groupby("region").size().reset_index(name="Buyers").sort_values("Buyers",ascending=False).head(15)
    fig=px.bar(reg.sort_values("Buyers"),x="Buyers",y="region",orientation="h",text="Buyers",color="Buyers",color_continuous_scale="Blues"); fig.update_layout(coloraxis_showscale=False,xaxis_title=None,yaxis_title=None); fig.update_traces(textposition="outside")
    st.plotly_chart(chart(fig,380),width='stretch',config={"displayModeBar":False}); st.markdown('</div>',unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# INVESTMENT PROFILING
# -----------------------------------------------------------------------------
elif page=="Investment Profiling":
    a,b,c=st.columns(3)
    inv=view[view.investment_flag==1]; end=view[view.investment_flag==0]
    with a:kpi("Investment Buyers",f"{len(inv):,}",f"{pct(len(inv)/len(view))} of current view")
    with b:kpi("Avg Investment Spend",money(inv.total_spend.mean() if len(inv) else 0),"Average aggregated spend")
    with c:kpi("Investment Satisfaction",f"{inv.satisfaction_score.mean():.2f}/5" if len(inv) else "—","Average satisfaction")
    x,y=st.columns([1.1,1])
    with x:
        st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Investment Rate by Segment")
        p=segment_profile(view).sort_values("Investment_Rate")
        fig=px.bar(p,x="Investment_Rate",y="segment_name",orientation="h",color="segment_name",color_discrete_map=SEGMENT_COLORS,text="Investment_Rate"); fig.update_traces(texttemplate="%{text:.0%}",textposition="outside"); fig.update_layout(showlegend=False,xaxis_tickformat=".0%",xaxis_title=None,yaxis_title=None)
        st.plotly_chart(chart(fig,320),width='stretch',config={"displayModeBar":False}); st.markdown('</div>',unsafe_allow_html=True)
    with y:
        st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Investment vs End-Use Spend","Aggregated spend comparison")
        cmp=pd.DataFrame({"Purpose":["Investment","End Use"],"Spend":[inv.total_spend.sum(),end.total_spend.sum()]})
        fig=px.bar(cmp,x="Purpose",y="Spend",text="Spend"); fig.update_traces(marker_color=["#20d3a2","#4f7cff"],texttemplate="$%{text:.3s}",textposition="outside"); fig.update_layout(xaxis_title=None,yaxis_title=None)
        st.plotly_chart(chart(fig,320),width='stretch',config={"displayModeBar":False}); st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Financing Behavior","Loan application rate by acquisition purpose and client type")
    q=view.groupby(["acquisition_purpose","client_type"]).agg(Buyers=("client_id","count"),LoanRate=("loan_flag","mean"),AvgSpend=("total_spend","mean")).reset_index(); q["Loan Rate"]=q.LoanRate.map(pct); q["Avg Spend"]=q.AvgSpend.map(money); st.dataframe(q.rename(columns={"acquisition_purpose":"Purpose","client_type":"Client Type","Buyers":"Buyers"})[["Purpose","Client Type","Buyers","Loan Rate","Avg Spend"]],width='stretch',hide_index=True); st.markdown('</div>',unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SEGMENT INSIGHTS
# -----------------------------------------------------------------------------
elif page=="Segment Insights":
    choices=SEGMENTS
    selected=st.selectbox("Select a segment",choices)
    sv=view[view.segment_name==selected]
    full=df[df.segment_name==selected]
    if len(sv)==0:
        st.markdown(f'<div class="empty"><h3>No {selected} buyers match the current filters.</h3><p>{len(full):,} exist in the full segment - adjust filters to see them.</p></div>',unsafe_allow_html=True)
        st.stop()
    if len(sv)<len(full): st.info(f"Insights below use the active filters: {len(sv):,} of {len(full):,} buyers in this segment.")
    a,b,c,d=st.columns(4)
    with a:kpi("Segment Size",f"{len(sv):,}",f"{pct(len(sv)/len(view))} of current view")
    with b:kpi("Avg Spend",money(sv.total_spend.mean()),"Average aggregated spend")
    with c:kpi("Investment Rate",pct(sv.investment_flag.mean()),"Share flagged investment")
    with d:kpi("Satisfaction",f"{sv.satisfaction_score.mean():.2f}/5","Average score")
    a,b=st.columns([1.1,1])
    with a:
        st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Buyer Profile","Behavioral distribution")
        metrics={"Avg Age":sv.age.mean(),"Avg Purchases":sv.total_purchases.mean(),"Avg Floor Area":sv.avg_floor_area.mean(),"Avg Purchase Price":sv.avg_purchase_price.mean(),"Avg Towers":sv.n_towers.mean()}
        st.dataframe(pd.DataFrame({"Metric":metrics.keys(),"Value":[f"{v:,.1f}" if k not in ["Avg Purchase Price"] else money(v) for k,v in metrics.items()]}),width='stretch',hide_index=True); st.markdown('</div>',unsafe_allow_html=True)
    with b:
        st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Top Countries","Where this segment is concentrated")
        q=sv.country.value_counts().head(8).sort_values(); fig=px.bar(q,x=q.values,y=q.index,orientation="h",text=q.values); fig.update_traces(marker_color=SEGMENT_COLORS.get(selected,"#4f7cff"),textposition="outside"); fig.update_layout(xaxis_title=None,yaxis_title=None); st.plotly_chart(chart(fig,270),width='stretch',config={"displayModeBar":False}); st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("What This Segment Tells Us")
    bullets=[f"The segment contains {len(sv):,} buyers with an average age of {sv.age.mean():.1f} years.",f"Average aggregated spend is {money(sv.total_spend.mean())}; total segment spend is {money(sv.total_spend.sum())}.",f"{pct(sv.investment_flag.mean())} are flagged for investment and {pct(sv.loan_flag.mean())} have a loan application flag.",f"Average satisfaction is {sv.satisfaction_score.mean():.2f}/5, indicating the segment's observed customer experience level."]
    for x in bullets: st.markdown(f'<div class="insight">◆ {x}</div>',unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)

    ACTIONS = {
        "Value-Conscious Home Buyers": (
            "Recommended Business Action",
            "Test affordability-focused messaging, financing calculators, and entry-level inventory. "
            "Treat this as a targeting hypothesis rather than a proven ROI result."
        ),
        "High-Volume / Frequent Buyers": (
            "Recommended Business Action",
            "Test loyalty, portfolio incentives, and early access to new listings because this segment has the highest purchase frequency and total spend. "
            "ROI is not validated because campaign-response data is unavailable."
        ),
        "Premium / High-Value Buyers": (
            "Recommended Business Action",
            "Test premium inventory, exclusivity, and higher-touch service positioning because this segment has the highest average purchase price. "
            "These are data-informed hypotheses, not measured campaign outcomes."
        ),
        "Corporate Buyers": (
            "Recommended Business Action",
            "Test a dedicated B2B sales workflow, multi-unit packages, and financing support because this cluster is overwhelmingly company-based and has the highest loan-application rate. "
            "The dataset does not contain conversion or ROI data."
        ),
    }
    title, action = ACTIONS.get(selected, ("Recommended Business Action", "Use the segment profile as a targeting hypothesis and validate it with campaign-response data."))
    st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title(title, "Data-informed hypothesis — validate with campaign results")
    st.markdown(f'<div class="insight">◆ {action}</div>',unsafe_allow_html=True); st.markdown('</div>',unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# CUSTOMER EXPLORER
# -----------------------------------------------------------------------------
elif page=="Customer Explorer":
    search=st.text_input("Search client ID",placeholder="e.g. client_00123")
    q=view.copy()
    if search:q=q[q.client_id.astype(str).str.contains(search,case=False,na=False)]
    st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Customer Explorer",f"{len(q):,} records available")
    cols=[c for c in ["client_id","client_type","country","region","acquisition_purpose","age","total_purchases","total_spend","avg_purchase_price","loan_flag","investment_flag","satisfaction_score","segment_name"] if c in q.columns]
    out=q[cols].copy(); out=out.rename(columns={"client_id":"Client ID","client_type":"Client Type","country":"Country","region":"Region","acquisition_purpose":"Purpose","age":"Age","total_purchases":"Purchases","total_spend":"Total Spend","avg_purchase_price":"Avg Purchase Price","loan_flag":"Loan","investment_flag":"Investment","satisfaction_score":"Satisfaction","segment_name":"Segment"})
    for c in ["Total Spend","Avg Purchase Price"]: out[c]=out[c].map(money)
    st.dataframe(out,width='stretch',hide_index=True,height=500)
    st.download_button("Download filtered customers (CSV)",q.to_csv(index=False).encode("utf-8"),"filtered_customers.csv","text/csv")
    st.markdown('</div>',unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MODEL INFORMATION
# -----------------------------------------------------------------------------
elif page=="Model Information":
    k=meta.get("k",4); sil=meta.get("silhouette",np.nan); ari=meta.get("ari_vs_hierarchical",np.nan)
    a,b,c,d=st.columns(4)
    with a:kpi("Algorithm","K-Means",f"Final k = {k}")
    with b:kpi("Silhouette",f"{sil:.3f}" if pd.notna(sil) else "—","Cluster separation")
    with c:kpi("Hierarchical ARI",f"{ari:.3f}" if pd.notna(ari) else "—","Cross-method agreement")
    with d:kpi("Features",str(len(meta.get("feature_names",[]))),"Behavioral + numeric")
    left,right=st.columns([1.1,1])
    with left:
        st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Model Design","Transparent methodology")
        for t in ["Raw client and property data are cleaned and joined at client level.","Purchase behavior is aggregated into spend, frequency, price, floor-area and property-mix features.","Numeric and binary behavioral features are standardized before clustering.","K values 2–10 are evaluated using inertia and silhouette; final k is selected with business interpretability and model diagnostics.","Hierarchical Ward clustering is used as an independent validation signal."]:
            st.markdown(f'<div class="insight">✓ {t}</div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Features Used")
        feats=meta.get("feature_names",[]); st.dataframe(pd.DataFrame({"Feature":feats}),width='stretch',hide_index=True); st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Segment Definitions","Post-hoc business labels from cluster profiles")
    mapping=meta.get("segment_names",{}); rows=[]
    for cluster,name in mapping.items(): rows.append({"Cluster":cluster,"Business Segment":name})
    st.dataframe(pd.DataFrame(rows),width='stretch',hide_index=True)
    st.caption("The silhouette score is intentionally shown rather than hidden: the segmentation is useful for business profiling, but cluster separation is modest and should be interpreted with that limitation in mind.")
    st.markdown('</div>',unsafe_allow_html=True)

    st.markdown('<div class="panel">',unsafe_allow_html=True); panel_title("Robustness & Stability","Reproducibility checks — not score optimization")
    if robustness:
        r1,r2,r3,r4=st.columns(4)
        with r1:kpi("Seed Stability",f"{robustness.get('seed_stability_mean_ari',np.nan):.3f}","Mean pairwise ARI")
        with r2:kpi("Min Seed ARI",f"{robustness.get('seed_stability_min_ari',np.nan):.3f}","Across tested seeds")
        with r3:kpi("Resample Stability",f"{robustness.get('bootstrap_mean_ari',np.nan):.3f}","Mean 80% sample ARI")
        with r4:kpi("Best Tested",f"{robustness.get('best_silhouette_over_tested_strategies',np.nan):.3f}","Across feature strategies")
        st.markdown(f'<div class="insight">✓ Tested three feature strategies, six random seeds and ten 80% resamples. The production k=4 model is retained because it preserves the distinct corporate-buyer signal and four actionable business profiles; the higher-scoring alternatives are documented rather than silently substituted.</div>',unsafe_allow_html=True)
    else:
        st.info("Run src/04_Model_Robustness_Validation.py to generate robustness diagnostics.")
    st.markdown('</div>',unsafe_allow_html=True)

st.markdown(f'<div class="footer"><span>© 2026 Parcl • Buyer Intelligence Platform</span><span>Analytical dashboard • Not investment advice • {len(view):,} buyers in view</span></div>',unsafe_allow_html=True)
