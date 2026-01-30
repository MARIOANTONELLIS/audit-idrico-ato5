import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import os

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="Audit Idrico ATO5", page_icon="icon.png", layout="wide")

# --- 2. CSS PER PULIZIA (Header visibile per Sidebar Mobile) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    .stTable {margin-left: auto; margin-right: auto;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE TARIFFE ---
UI_TOT = 0.0329 
DB_ATO = {
    2024: { "f_acq_res": 48.2423, "f_acq_nres": 122.2138, "f_fog": 8.8766, "f_dep": 30.8751, "v_fog": 0.4239, "v_dep": 1.2824, "p_res": [1.2010, 1.5014, 2.4021, 4.8042, 7.2062], "p_nres": [1.5014, 2.4021, 4.8042, 7.2062] },
    2025: { "f_acq_res": 54.2996, "f_acq_nres": 137.5589, "f_fog": 9.9911, "f_dep": 34.7517, "v_fog": 0.4772, "v_dep": 1.4434, "p_res": [1.3518, 1.6899, 2.7037, 5.4074, 8.1110], "p_nres": [1.6899, 2.7037, 5.4074, 8.1110] },
    2026: { "f_acq_res": 57.0145, "f_acq_nres": 144.4368, "f_fog": 10.4907, "f_dep": 36.4893, "v_fog": 0.5010, "v_dep": 1.5156, "p_res": [1.4194, 1.7744, 2.8389, 5.6777, 8.5166], "p_nres": [1.7744, 2.8389, 5.6777, 8.5166] }
}
SOGLIE_DATA = {
    "Resid. Nucleo 1": [19, 72, 126, 180], "Resid. Nucleo 2": [37, 90, 144, 198],
    "Resid. Nucleo 3": [55, 108, 162, 216], "Resid. Nucleo 4": [73, 126, 180, 234],
    "Resid. Nucleo 5": [92, 145, 199, 253], "Resid. Nucleo 6": [110, 163, 217, 271],
    "Resid. Nucleo 7": [128, 181, 235, 289], "Resid. Nucleo 8": [146, 199, 253, 307],
    "Condominiale": [55, 108, 162, 216], "Non Residenziale": [108, 162, 216]
}
DATA_SOC = { "f_acq": 12.84, "f_fog": 0.5243, "f_dep": 0.6848, "scaglioni": [60, 90, 155], "p_acq": [0.75585, 0.94481, 1.17154, 1.22825], "p_fog": 0.09384, "p_dep": 0.12476 }
CATEGORIE = list(SOGLIE_DATA.keys()) + ["Tariffa Sociale (TS)"]

def calc_v(mc, s, p):
    v, tm = [], mc
    for i in range(len(s)):
        l = s[i] if i==0 else s[i]-s[i-1]
        pr = min(tm, l); v.append(pr * p[i]); tm -= pr
    if tm > 0: v.append(tm * p[-1])
    return sum(v)

if 'res' not in st.session_state: st.session_state.res = None
def reset_res(): st.session_state.res = None

# --- 4. SIDEBAR ---
with st.sidebar:
    if os.path.exists("icon.png"): st.image("icon.png", use_container_width=True)
    
    st.header("⚙️ Parametri Calcolo")
    # Categoria principale per il calcolo
    c_s = st.selectbox("CATEGORIA UTENZA", CATEGORIE, index=2, on_change=reset_res)
    sw_fog = st.toggle("Fognatura", value=True, on_change=reset_res)
    sw_dep = st.toggle("Depurazione", value=True, on_change=reset_res)
    iva_calc = st.toggle("Applica IVA 10%", value=True, on_change=reset_res)
    
    st.markdown("---")
    
    # SEZIONE INFOTARIFFE INDIPENDENTE
    with st.expander("🔍 INFOTARIFFE (Consultazione)", expanded=False):
        # Questi due selettori NON resettano il calcolo e NON sono legati a c_s
        sel_y_inf = st.selectbox("Anno Rif.", [2024, 2025, 2026], index=2, key="y_info")
        sel_c_inf = st.selectbox("Cat. Rif.", CATEGORIE, index=CATEGORIE.index(c_s), key="c_info")
        
        if "Sociale" in sel_c_inf:
            st.write(f"**Quota Fissa:** € {DATA_SOC['f_acq']:.2f}")
            st.table(pd.DataFrame({"Volume": [f"fino a {s} mc" for s in DATA_SOC['scaglioni']] + ["eccedenza"], "€/mc": DATA_SOC['p_acq']}))
        else:
            db_inf = DB_ATO[sel_y_inf]
            f_a_inf = db_inf["f_acq_nres"] if sel_c_inf == "Non Residenziale" else db_inf["f_acq_res"]
            st.write(f"**Fisse:** Acq {f_a_inf:.2f} | Fog {db_inf['f_fog']:.2f} | Dep {db_inf['f_dep']:.2f}")
            s_inf, p_inf = SOGLIE_DATA[sel_c_inf], (db_inf["p_res"] if sel_c_inf != "Non Residenziale" else db_inf["p_nres"])
            st.table(pd.DataFrame({"Fascia": [f"fino a {s}" for s in s_inf] + [">"+str(s_inf[-1])], "€/mc": p_inf}))

# --- 5. MAIN ---
st.title("💧 AUDIT IDRICO ATO5")
ci1, ci2 = st.columns(2)
with ci1:
    d1_in = st.date_input("Inizio Periodo:", date(2024, 1, 1), on_change=reset_res)
    l1 = st.number_input("Lettura Iniziale:", value=230.0, on_change=reset_res)
with ci2:
    d2_in = st.date_input("Fine Periodo:", date(2026, 12, 31), on_change=reset_res)
    l2 = st.number_input("Lettura Finale:", value=800.0, on_change=reset_res)

if st.button("ESEGUI ELABORAZIONE AUDIT", type="primary", use_container_width=True):
    d1, d2 = datetime.combine(d1_in, datetime.min.time()), datetime.combine(d2_in, datetime.min.time())
    mc_t, gg_t = l2-l1, (d2-d1).days + 1
    iva = 1.10 if iva_calc else 1.0
    mf, md = (1 if sw_fog else 0), (1 if sw_dep else 0)
    r_a = {"af":0,"av":0,"ff":0,"fv":0,"df":0,"dv":0}; det = []
    
    for y in [2024, 2025, 2026]:
        ei, ef = max(d1, datetime(y,1,1)), min(d2, datetime(y,12,31))
        if ei <= ef:
            gg = (ef-ei).days+1; mc_y = mc_t*(gg/gg_t); db = DB_ATO[y]
            f_a = db["f_acq_nres"] if c_s == "Non Residenziale" else db["f_acq_res"]
            s, p = ([] if "Sociale" in c_s else SOGLIE_DATA[c_s]), (db["p_nres"] if c_s == "Non Residenziale" else db["p_res"])
            c_af, c_av = f_a * (gg/365), calc_v(mc_y, s, p)
            c_ff, c_fv = db["f_fog"]*(gg/365)*mf, mc_y*db["v_fog"]*mf
            c_df, c_dv = db["f_dep"]*(gg/365)*md, mc_y*db["v_dep"]*md
            c_up = mc_y * UI_TOT
            # Importo totale lordo di periodo per la tabella pro-rata
            tot_y = (c_af + c_av + c_ff + c_fv + c_df + c_dv + c_up) * iva
            r_a["af"]+=c_af; r_a["av"]+=c_av; r_a["ff"]+=c_ff; r_a["fv"]+=c_fv; r_a["df"]+=c_df; r_a["dv"]+=c_dv
            det.append({"Anno": y, "Giorni": gg, "MC": round(mc_y, 1), "Importo t. €": round(tot_y, 2)})

    up_tot = mc_t * UI_TOT
    r_ts = {"af":DATA_SOC["f_acq"]*(gg_t/365), "av":calc_v(mc_t,DATA_SOC["scaglioni"],DATA_SOC["p_acq"]), "ff":DATA_SOC["f_fog"]*(gg_t/365)*mf, "fv":mc_t*DATA_SOC["p_fog"]*mf, "df":DATA_SOC["f_dep"]*(gg_t/365)*md, "dv":mc_t*DATA_SOC["p_dep"]*md}
    st.session_state.res = {"t_ato": (sum(r_a.values())+up_tot)*iva, "t_ts": (sum(r_ts.values())+up_tot)*iva, "r_a": r_a, "r_ts": r_ts, "up": up_tot, "det": det, "mc": mc_t, "gg": gg_t, "cat": c_s}

if st.session_state.res:
    res = st.session_state.res
    st.markdown("---")
    
    k1, k2, k3 = st.columns(3)
    k1.metric("Volume", f"{res['mc']:.1f} mc")
    k2.metric("Giorni", f"{res['gg']} gg")
    k3.metric("Totale ATO5", f"€ {res['t_ato']:.2f}")

    st.subheader("⚖️ Analisi Comparativa")
    df_comp = pd.DataFrame({
        "ATO5 (€)": [res['r_a']['af']+res['r_a']['av'], res['r_a']['ff']+res['r_a']['fv'], res['r_a']['df']+res['r_a']['dv'], res['up'], res['t_ato']],
        "Sociale (€)": [res['r_ts']['af']+res['r_ts']['av'], res['r_ts']['ff']+res['r_ts']['fv'], res['r_ts']['df']+res['r_ts']['dv'], res['up'], res['t_ts']]
    }, index=["Acquedotto", "Fognatura", "Depurazione", "Perequazione (UI)", "TOTALE LORDO"])
    st.table(df_comp.style.format("{:.2f}"))

    st.markdown




