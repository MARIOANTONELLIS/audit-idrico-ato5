with open("app.py", "w") as f:
    f.write("""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import os

st.set_page_config(page_title="Audit Idrico ATO5", layout="wide")

# --- DATABASE TARIFFE ---
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

# --- SIDEBAR ---
with st.sidebar:
    for logo_name in ["icon.jpg", "icon.png", "ico.png", "ICONA_APP.jpg"]:
        if os.path.exists(logo_name):
            st.image(logo_name, use_container_width=True)
            break
    st.subheader("⚙️ Configurazione")
    c_s = st.selectbox("CATEGORIA UTENZA", CATEGORIE, index=2, on_change=reset_res)
    sw_fog = st.toggle("Fognatura", value=True, on_change=reset_res)
    sw_dep = st.toggle("Depurazione", value=True, on_change=reset_res)
    iva_calc = st.toggle("Applica IVA 10%", value=True, on_change=reset_res)
    
    st.markdown("---")
    with st.expander("🔍 INFOTARIFFE (Dati Tecnici)"):
        sel_y = st.selectbox("Seleziona Anno", [2024, 2025, 2026], index=2)
        # NUOVO: SELETTORE CATEGORIA IN INFOTARIFFE
        sel_c = st.selectbox("Seleziona Categoria", CATEGORIE, index=CATEGORIE.index(c_s))
        
        if "Sociale" in sel_c: st.json(DATA_SOC)
        else:
            db = DB_ATO[sel_y]
            f_a = db["f_acq_nres"] if sel_c == "Non Residenziale" else db["f_acq_res"]
            st.markdown("**CANONI FISSI:**") 
            st.write(f"Acquedotto: € {f_a:.4f}")
            st.write(f"Fognatura: € {db['f_fog']:.4f}")
            st.write(f"Depurazione: € {db['f_dep']:.4f}")
            st.markdown("**QUOTE VARIABILI:**")
            st.write(f"Fognatura: € {db['v_fog']:.4f}")
            st.write(f"Depurazione: € {db['v_dep']:.4f}")
            st.write(f"Perequazione (UI): € {UI_TOT:.4f}")
            
            sogl, prezzi = SOGLIE_DATA[sel_c], (db["p_res"] if sel_c != "Non Residenziale" else db["p_nres"])
            fasce = []
            for i in range(len(prezzi)):
                rg = f"0-{sogl[0]}" if i==0 else (f"{sogl[i-1]+1}-{sogl[i]}" if i < len(sogl) else f">{sogl[-1]}")
                fasce.append({"Fascia": f"Fascia {i+1}", "Scaglioni mc": rg, "Tariffa €/mc": f"{prezzi[i]:.4f}"})
            st.table(pd.DataFrame(fasce))

# --- MAIN ---
st.title("💧 AUDIT IDRICO ATO5")
c_i1, c_i2 = st.columns(2)
with c_i1:
    d1_in = st.date_input("Inizio Periodo:", date(2024, 1, 1), on_change=reset_res)
    l1 = st.number_input("Lettura Iniziale (mc):", value=230.0, on_change=reset_res)
with c_i2:
    d2_in = st.date_input("Fine Periodo:", date(2026, 12, 31), on_change=reset_res)
    l2 = st.number_input("Lettura Finale (mc):", value=800.0, on_change=reset_res)

if l2 < l1: st.error("⚠️ Errore: Lettura finale inferiore alla iniziale.")
elif d2_in < d1_in: st.error("⚠️ Errore: Date invertite.")
else:
    if st.button("ESEGUI ELABORAZIONE AUDIT", type="primary", use_container_width=True):
        d1, d2 = datetime.combine(d1_in, datetime.min.time()), datetime.combine(d2_in, datetime.min.time())
        mc_t, gg_t = l2-l1, (d2-d1).days + 1
        mf, md, up = (1 if sw_fog else 0), (1 if sw_dep else 0), mc_t*UI_TOT
        
        # Calcolo Pro-Rata ATO5
        r_a = {"af":0,"av":0,"ff":0,"fv":0,"df":0,"dv":0}
        det = []
        for y in [2024, 2025, 2026]:
            ei, ef = max(d1, datetime(y,1,1)), min(d2, datetime(y,12,31))
            if ei <= ef:
                gg = (ef-ei).days+1; mc_y = mc_t*(gg/gg_t); db = DB_ATO[y]
                f = db["f_acq_nres"] if c_s == "Non Residenziale" else db["f_acq_res"]
                s = [] if "Sociale" in c_s else SOGLIE_DATA[c_s]
                p = db["p_nres"] if c_s == "Non Residenziale" else db["p_res"]
                c_af, c_av = f*(gg/365), calc_v(mc_y, s, p)
                r_a["af"]+=c_af; r_a["av"]+=c_av; r_a["ff"]+=db["f_fog"]*(gg/365)*mf; r_a["fv"]+=mc_y*db["v_fog"]*mf; r_a["df"]+=db["f_dep"]*(gg/365)*md; r_a["dv"]+=mc_y*db["v_dep"]*md
                det.append({"Anno": y, "Giorni": gg, "MC": f"{mc_y:.1f}", "€ Acq (Imp.)": f"{c_af+c_av:.2f}"})
        
        r_ts = {"af":DATA_SOC["f_acq"]*(gg_t/365), "av":calc_v(mc_t,DATA_SOC["scaglioni"],DATA_SOC["p_acq"]), "ff":DATA_SOC["f_fog"]*(gg_t/365)*mf, "fv":mc_t*DATA_SOC["p_fog"]*mf, "df":DATA_SOC["f_dep"]*(gg_t/365)*md, "dv":mc_t*DATA_SOC["p_dep"]*md}
        iva = 1.10 if iva_calc else 1.0
        st.session_state.res = {"t_ato": (sum(r_a.values())+up)*iva, "t_ts": (sum(r_ts.values())+up)*iva, "r_a": r_a, "r_ts": r_ts, "up": up, "det": det, "mc": mc_t, "gg": gg_t, "cat": c_s}

if st.session_state.res:
    res = st.session_state.res
    st.markdown("---")
    
    # KPIs
    k1, k2, k3 = st.columns(3)
    k1.metric("Metri Cubi Totali", f"{res['mc']:.1f} mc")
    k2.metric("Giorni Totali", f"{res['gg']} gg")
    k3.metric("Totale ATO5 (Lordo)", f"€ {res['t_ato']:.2f}")

    if "Sociale" in res['cat']:
        st.subheader("📋 Riepilogo Tariffa Sociale (TS)")
        df_ts = pd.DataFrame({"Costo (€)": [res['r_ts']['af']+res['r_ts']['av'], res['r_ts']['ff']+res['r_ts']['fv'], res['r_ts']['df']+res['r_ts']['dv'], res['up'], res['t_ts']]}, index=["Acquedotto", "Fognatura", "Depurazione", "Oneri Perequazione", "TOTALE TS"])
        st.table(df_ts.style.format("{:.2f}"))
    else:
        # Layout Tabelle + Grafici
        col_t1, col_g1 = st.columns([1.5, 1])
        with col_t1:
            st.subheader("⚖️ Confronto ATO5 vs T. Sociale")
            df_comp = pd.DataFrame({
                "ATO5 (€)": [res['r_a']['af']+res['r_a']['av'], res['r_a']['ff']+res['r_a']['fv'], res['r_a']['df']+res['r_a']['dv'], res['up'], res['t_ato']],
                "Sociale (€)": [res['r_ts']['af']+res['r_ts']['av'], res['r_ts']['ff']+res['r_ts']['fv'], res['r_ts']['df']+res['r_ts']['dv'], res['up'], res['t_ts']]
            }, index=["Acquedotto (f+v)", "Fognatura (f+v)", "Depurazione (f+v)", "Oneri Perequazione", "TOTALE DOVUTO"])
            st.table(df_comp.style.format("{:.2f}"))
            st.success(f"RISPARMIO NETTO: € {res['t_ato']-res['t_ts']:.2f}")
        with col_g1:
            st.subheader("📊 Totali Comparati")
            st.bar_chart(pd.DataFrame({"Euro": [res['t_ato'], res['t_ts']]}, index=["ATO5", "Sociale"]))

        st.markdown("---")
        col_t2, col_g2 = st.columns([1.5, 1])
        with col_t2:
            st.subheader("📝 Dettaglio Analitico Pro-Rata")
            st.table(pd.DataFrame(res["det"]))
        with col_g2:
            st.subheader("🍕 Incidenza Costi ATO5")
            fig = px.pie(values=[res['r_a']['af']+res['r_a']['av'], res['r_a']['ff']+res['r_a']['fv'], res['r_a']['df']+res['r_a']['dv'], res['up']], names=["Acquedotto", "Fognatura", "Depurazione", "Oneri UI"], color_discrete_sequence=['#1f77b4', '#9467bd', '#2ca02c', '#7f7f7f'], hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
""")

import os
os.system("pkill cloudflared")
os.system("pkill streamlit")
os.system("streamlit run app.py &")
!cloudflared tunnel --url http://localhost:8501