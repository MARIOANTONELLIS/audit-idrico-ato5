import os
from datetime import datetime
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
from kivy.config import Config
Config.set('graphics', 'width', '380'), Config.set('graphics', 'height', '780')

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Line
from kivy.metrics import dp

# --- DATABASE ---
UI_TOT = 0.0329 
D_LIM_INI, D_LIM_FIN = datetime(2024, 1, 1), datetime(2026, 12, 31)
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

class GridLabel(MDLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.halign = "center"
        self.valign = "middle"
        self.font_style = "Caption"
        with self.canvas.before:
            Color(0.8, 0.8, 0.8, 1)
            self.rect = Line(rectangle=(self.x, self.y, self.width, self.height), width=1)
        self.bind(pos=self._update_rect, size=self._update_rect)
    def _update_rect(self, *args):
        self.rect.rectangle = (self.x, self.y, self.width, self.height)

class AuditATO5_Mobile(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        screen = MDScreen()
        main_layout = MDBoxLayout(orientation="vertical")
        
        # HEADER
        header = MDBoxLayout(orientation="vertical", size_hint_y=None, height="100dp", md_bg_color=self.theme_cls.primary_color, padding=[0,5,0,5], spacing="5dp")
        header.add_widget(MDLabel(text="AUDIT IDRICO ATO5", halign="center", theme_text_color="Custom", text_color=(1,1,1,1), font_style="H6"))
        self.btn_tar_top = MDRaisedButton(text="TARIFFE (2024-2026)", md_bg_color=(0.1, 0.5, 0.2, 1), pos_hint={"center_x": .5}, on_release=self.mostra_dialog_tariffe)
        header.add_widget(self.btn_tar_top)
        main_layout.add_widget(header)
        
        scroll = ScrollView()
        # Aumentato spacing a 15dp tra le card
        container = MDBoxLayout(orientation="vertical", spacing="15dp", padding="12dp", size_hint_y=None)
        container.bind(minimum_height=container.setter('height'))
        
        # 1. INPUT CARD (Altezza aumentata a 260dp per evitare overlap)
        in_card = MDCard(orientation='vertical', padding=[dp(15), dp(10), dp(15), dp(15)], spacing="15dp", size_hint_y=None, height="260dp", radius=[10], elevation=1)
        self.btn_cat = MDRaisedButton(text="Resid. Nucleo 3", pos_hint={"center_x": .5}, size_hint_x=0.9, on_release=self.open_menu)
        in_card.add_widget(self.btn_cat)

        # Griglia aumentata a 140dp per contenere bene 2 righe di input
        grid_in = MDGridLayout(cols=4, spacing="6dp", size_hint_y=None, height="140dp")
        for h in ["GG", "MM", "AAAA", "mc"]: grid_in.add_widget(MDLabel(text=h, halign="center", font_style="Caption"))
        for p in ["l1", "l2"]:
            for s, v in zip(["d", "m", "y", ""], ["01" if p=="l1" else "31", "01" if p=="l1" else "12", "2024" if p=="l1" else "2026", ""]):
                t = MDTextField(text=v, input_filter="float" if not s else "int", mode="rectangle", halign="center")
                t.bind(text=self.auto_reset); setattr(self, f"{p}_{s}" if s else p, t); grid_in.add_widget(t)
        in_card.add_widget(grid_in)
        container.add_widget(in_card)

        # 2. OPZIONI
        opt_card = MDCard(orientation='vertical', padding="10dp", spacing="10dp", size_hint_y=None, height="120dp", radius=[10], elevation=1)
        sw_box = MDBoxLayout(orientation="horizontal", spacing="20dp", pos_hint={"center_x": .5}, size_hint_x=None, width="280dp")
        for n, a in [("Fogn.", "sw_fog"), ("Depur.", "sw_dep")]:
            b = MDBoxLayout(spacing="5dp"); b.add_widget(MDLabel(text=n, halign="right", font_style="Caption"))
            s = MDSwitch(); s.active=True; s.bind(active=self.auto_reset); setattr(self, a, s); b.add_widget(s); sw_box.add_widget(b)
        opt_card.add_widget(sw_box)
        self.btn_calc = MDRaisedButton(text="ESEGUI AUDIT COMPARATIVO", pos_hint={"center_x": .5}, size_hint_x=0.9, md_bg_color=(0.1, 0.5, 0.2, 1), on_release=self.elabora)
        opt_card.add_widget(self.btn_calc)
        container.add_widget(opt_card)

        # 3. RISULTATI
        self.res_card = MDCard(orientation='vertical', padding="5dp", size_hint_y=None, height="380dp", radius=[10], elevation=2)
        self.grid_res = MDGridLayout(cols=3, spacing=0, size_hint_y=1)
        self.res_card.add_widget(self.grid_res)
        container.add_widget(self.res_card)

        scroll.add_widget(container); main_layout.add_widget(scroll); screen.add_widget(main_layout)
        self.menu = MDDropdownMenu(caller=self.btn_cat, items=[{"viewclass": "OneLineListItem", "text": c, "font_style": "Caption", "on_release": lambda x=c: self.set_item(x)} for c in CATEGORIE], width_mult=5, max_height=dp(300))
        return screen

    def auto_reset(self, *args):
        self.grid_res.clear_widgets()
        self.grid_res.add_widget(MDLabel(text="Inserire mc e calcolare", halign="center"))

    def set_item(self, x): self.btn_cat.text = x; self.menu.dismiss(); self.auto_reset()
    def open_menu(self, i): self.menu.open()

    # --- TARIFFE E CALCOLO (Resto del codice invariato) ---
    def mostra_dialog_tariffe(self, *args):
        self.t_y, self.t_c = "2026", self.btn_cat.text
        content = MDBoxLayout(orientation="vertical", spacing="2dp", size_hint_y=None, height="520dp")
        sel = MDBoxLayout(spacing="5dp", size_hint_y=None, height="45dp")
        self.b_y = MDFlatButton(text=f"ANNO: {self.t_y}", on_release=self.menu_y)
        self.b_c = MDFlatButton(text=f"{self.t_c}", on_release=self.menu_c_tariffe)
        sel.add_widget(self.b_y); sel.add_widget(self.b_c); content.add_widget(sel)
        self.grid_tar = MDGridLayout(cols=3, spacing=0, size_hint_y=None, height="460dp")
        content.add_widget(self.grid_tar)
        self.d_tar = MDDialog(title="DATI TARIFFE", type="custom", content_cls=content, buttons=[MDFlatButton(text="CHIUDI", on_release=lambda x: self.d_tar.dismiss())])
        self.up_t(); self.d_tar.open()

    def up_t(self, *args):
        self.grid_tar.clear_widgets()
        y, c = int(self.t_y), self.t_c
        db = DB_ATO[y] if "Sociale" not in c else DATA_SOC
        fa = db["f_acq_nres"] if c == "Non Residenziale" else (db["f_acq"] if "Sociale" in c else db["f_acq_res"])
        self.grid_tar.add_widget(GridLabel(text="FISSE:", bold=True)); self.grid_tar.add_widget(GridLabel(text=f"Acq: €{fa:.2f}")); self.grid_tar.add_widget(GridLabel(text=f"Fog: €{db['f_fog']:.2f}"))
        self.grid_tar.add_widget(GridLabel(text="")); self.grid_tar.add_widget(GridLabel(text=f"Dep: €{db['f_dep']:.2f}")); self.grid_tar.add_widget(GridLabel(text=""))
        vfog, vdep = (db["v_fog"] if "Sociale" not in c else db["p_fog"]), (db["v_dep"] if "Sociale" not in c else db["p_dep"])
        self.grid_tar.add_widget(GridLabel(text="VARIABILI:", bold=True)); self.grid_tar.add_widget(GridLabel(text=f"Fog: €{vfog:.4f}")); self.grid_tar.add_widget(GridLabel(text=f"Dep: €{vdep:.4f}"))
        self.grid_tar.add_widget(GridLabel(text="UI Pereq.", bold=True)); self.grid_tar.add_widget(GridLabel(text=f"€ {UI_TOT:.4f}")); self.grid_tar.add_widget(GridLabel(text=""))
        for h in ["Fascia", "Range mc", "€/mc"]: self.grid_tar.add_widget(GridLabel(text=h, bold=True))
        sogl, p = (SOGLIE_DATA[c] if "Sociale" not in c else DATA_SOC['scaglioni']), ((db["p_res"] if c != "Non Residenziale" else db["p_nres"]) if "Sociale" not in c else DATA_SOC['p_acq'])
        for i in range(len(p)):
            rg = f"0-{sogl[0]}" if i==0 else (f"{sogl[i-1]+1}-{sogl[i]}" if i < len(sogl) else f">{sogl[-1]}")
            self.grid_tar.add_widget(GridLabel(text=f"F.{i+1}")); self.grid_tar.add_widget(GridLabel(text=rg)); self.grid_tar.add_widget(GridLabel(text=f"{p[i]:.4f}"))

    def menu_y(self, i): MDDropdownMenu(caller=i, items=[{"viewclass":"OneLineListItem","text":y,"on_release":lambda x=y:self.set_y(x)} for y in ["2024","2025","2026"]], width_mult=2).open()
    def set_y(self, x): self.t_y = x; self.b_y.text=f"ANNO: {x}"; self.up_t()
    def menu_c_tariffe(self, i): MDDropdownMenu(caller=i, items=[{"viewclass":"OneLineListItem","text":c,"font_style":"Caption","on_release":lambda x=c:self.set_c_tariffe(x)} for c in CATEGORIE], width_mult=5, max_height=dp(300)).open()
    def set_c_tariffe(self, c): self.t_c = c; self.b_c.text=c; self.up_t()

    def calc_v(self, mc, s, p):
        v, tm = [], mc
        for i in range(len(s)):
            l = s[i] if i==0 else s[i]-s[i-1]; pr = min(tm, l); v.append(pr * p[i]); tm -= pr
        if tm > 0: v.append(tm * p[-1])
        return sum(v)

    def elabora(self, *args):
        if not self.l1.text.strip() or not self.l2.text.strip(): return
        try:
            l1, l2 = float(self.l1.text), float(self.l2.text); d1 = datetime(int(self.l1_y.text), int(self.l1_m.text), int(self.l1_d.text)); d2 = datetime(int(self.l2_y.text), int(self.l2_m.text), int(self.l2_d.text))
            mc_t, gg_t, c_s = l2-l1, (d2-d1).days+1, self.btn_cat.text
            mf, md, up = (1 if self.sw_fog.active else 0), (1 if self.sw_dep.active else 0), mc_t*UI_TOT
            r_ts = {"af":DATA_SOC["f_acq"]*(gg_t/365),"av":self.calc_v(mc_t,DATA_SOC["scaglioni"],DATA_SOC["p_acq"]),"ff":DATA_SOC["f_fog"]*(gg_t/365)*mf,"fv":mc_t*DATA_SOC["p_fog"]*mf,"df":DATA_SOC["f_dep"]*(gg_t/365)*md,"dv":mc_t*DATA_SOC["p_dep"]*md}
            t_ts = (sum(r_ts.values())+up)*1.1
            r_a = {"af":0,"av":0,"ff":0,"fv":0,"df":0,"dv":0}
            for y in [2024, 2025, 2026]:
                ei, ef = max(d1, datetime(y,1,1)), min(d2, datetime(y,12,31))
                if ei <= ef:
                    gg = (ef-ei).days+1; mc_y = mc_t*(gg/gg_t); db = DB_ATO[y]; f = db["f_acq_nres"] if c_s == "Non Residenziale" else db["f_acq_res"]
                    s, p = SOGLIE_DATA[c_s] if "Sociale" not in c_s else ([],[]), (db["p_res"] if c_s != "Non Residenziale" else db["p_nres"])
                    r_a["af"]+=f*(gg/365); r_a["av"]+=self.calc_v(mc_y,s,p); r_a["ff"]+=db["f_fog"]*(gg/365)*mf; r_a["fv"]+=mc_y*db["v_fog"]*mf; r_a["df"]+=db["f_dep"]*(gg/365)*md; r_a["dv"]+=mc_y*db["v_dep"]*md
            t_ato = (sum(r_a.values())+up)*1.1
            self.grid_res.clear_widgets(); self.grid_res.add_widget(GridLabel(text=f"{mc_t}mc - {gg_t}gg", bold=True))
            self.grid_res.add_widget(GridLabel(text="ATO5 (€)", bold=True)); self.grid_res.add_widget(GridLabel(text="T.SOC(€)", bold=True))
            voci = [("Acquedotto(*)", r_a['af']+r_a['av'], r_ts['af']+r_ts['av']), ("Fognatura (*)", r_a['ff']+r_a['fv'], r_ts['ff']+r_ts['fv']), ("Depurazione(*)", r_a['df']+r_a['dv'], r_ts['df']+r_ts['dv']), ("Oneri UI", up, up)]
            for n, a, t in voci: self.grid_res.add_widget(GridLabel(text=n)); self.grid_res.add_widget(GridLabel(text=f"{a:.2f}")); self.grid_res.add_widget(GridLabel(text=f"{t:.2f}"))
            self.grid_res.add_widget(GridLabel(text="TOT. IVA", bold=True)); self.grid_res.add_widget(GridLabel(text=f"{t_ato:.2f}", bold=True)); self.grid_res.add_widget(GridLabel(text=f"{t_ts:.2f}", bold=True))
            self.grid_res.add_widget(GridLabel(text="RISPARMIO", bold=True, color=(0.1,0.5,0.1,1))); self.grid_res.add_widget(GridLabel(text="NETTO:", bold=True, color=(0.1,0.5,0.1,1))); self.grid_res.add_widget(GridLabel(text=f"€ {t_ato-t_ts:.2f}", bold=True, color=(0.1,0.5,0.1,1)))
        except: pass

if __name__ == "__main__":
    AuditATO5_Mobile().run()