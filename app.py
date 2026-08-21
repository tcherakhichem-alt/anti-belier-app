import streamlit as st
import math
import numpy as np
import plotly.graph_objects as go
import streamlit.components.v1 as components
import pathlib

st.set_page_config(
    page_title="Dimensionnement Réservoir Anti-Bélier",
    layout="wide",
    initial_sidebar_state="collapsed",   # sidebar fermée par défaut sur mobile
)

# ── Injection CSS responsive & mobile-first ──────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

/* ── Variables globales ── */
:root {
  --accent: #3fb6a8;
  --accent2: #e0a458;
  --bg-card: #16212c;
  --border: #2a3a45;
}

/* ── Base ── */
html, body, [class*="css"] {
  font-family: 'Inter', sans-serif !important;
}

/* ── Titre principal ── */
h1 { font-size: clamp(18px, 4vw, 28px) !important; line-height: 1.3; }
h2 { font-size: clamp(15px, 3.5vw, 22px) !important; }
h3 { font-size: clamp(13px, 3vw, 18px) !important; }

/* ── Métriques : empêche le chevauchement sur mobile ── */
[data-testid="metric-container"] {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px 12px !important;
  min-width: 0;
  word-break: break-word;
}
[data-testid="metric-container"] label {
  font-size: clamp(10px, 2.5vw, 13px) !important;
  white-space: normal !important;
  line-height: 1.3;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
  font-size: clamp(16px, 4vw, 26px) !important;
}

/* ── Colonnes : empilage vertical sur petit écran ── */
@media (max-width: 640px) {
  [data-testid="column"] {
    width: 100% !important;
    flex: 1 1 100% !important;
    min-width: 0 !important;
  }
  /* Blocs côte à côte → empilés */
  [data-testid="stHorizontalBlock"] {
    flex-wrap: wrap !important;
    gap: 8px !important;
  }
}

/* ── Textes longs / équations ── */
p, .stMarkdown, .stInfo, .element-container {
  overflow-wrap: break-word;
  word-wrap: break-word;
}

/* ── Tableaux horizontalement défilables ── */
[data-testid="stDataFrame"], .dataframe-container {
  overflow-x: auto !important;
  -webkit-overflow-scrolling: touch;
}

/* ── Graphiques Plotly : scroll horizontal si trop larges ── */
.js-plotly-plot {
  overflow-x: auto !important;
}

/* ── Sidebar déclenchée par bouton burger → OK par défaut ── */
@media (max-width: 768px) {
  section[data-testid="stSidebar"] { width: 100% !important; }
}

/* ── Info banner ── */
.stAlert { font-size: clamp(11px, 2.5vw, 14px) !important; }

/* ── Radio buttons ── */
.stRadio label { font-size: clamp(12px, 2.8vw, 14px) !important; }

/* ── Number input ── */
.stNumberInput input { font-size: clamp(13px, 3vw, 15px) !important; }

/* ── Séparateur ── */
hr { border-color: var(--border) !important; margin: 20px 0 !important; }
</style>
""", unsafe_allow_html=True)


# ── Titre ────────────────────────────────────────────────────────────────────
st.title("🌊 Dashboard Anti-Bélier")
st.markdown(
    "<p style='font-size:clamp(12px,2.8vw,15px);color:#9aa7b0;'>"
    "Calcul interactif étape par étape — Méthode & Abaque de M. Vibert (Planche XXVII)"
    "</p>",
    unsafe_allow_html=True,
)

# ── SIDEBAR : Paramètres ──────────────────────────────────────────────────────
st.sidebar.header("⚙️ Paramètres d'Entrée")
D_int_mm   = st.sidebar.number_input("Diamètre intérieur D (mm)",   value=327.4, step=1.0)
DN_mm      = st.sidebar.number_input("Diamètre nominal DN (mm)",     value=800.0, step=10.0)
L          = st.sidebar.number_input("Longueur conduite L (m)",      value=860.0, step=10.0)
Hg         = st.sidebar.number_input("Hauteur Géométrique Hg (mCE)", value=120.0, step=1.0)
Q_m3h      = st.sidebar.number_input("Débit Q (m³/h)",               value=454.0, step=5.0)
PN_bar     = st.sidebar.number_input("Pression Nominale PN (Bar)",   value=16.0,  step=1.0)
E_conduite = st.sidebar.number_input("Module élasticité E (Pa)",     value=1.2e9, format="%.1e")

# ── Calculs communs ───────────────────────────────────────────────────────────
epsilon_eau = 2.05e9
rho = 1000.0
g   = 9.81

D  = D_int_mm / 1000.0
DN = DN_mm    / 1000.0
e  = (DN - D) / 2.0

C      = math.sqrt(1.0 / (rho * ((1.0 / epsilon_eau) + (D / (E_conduite * e)))))
Q_m3s  = Q_m3h / 3600.0
U      = (4.0 * Q_m3s) / (math.pi * D**2)

B            = (C * U) / g
delta_P_bar  = (rho * C * U) * 1e-5
PN_mCE       = (PN_bar * 1e5) / (rho * g)
Patm_mCE     = 10.19
Z0           = Hg + Patm_mCE
Zmaxi        = PN_mCE + Patm_mCE
Zmax_Z0      = Zmaxi / Z0
h0           = U**2 / (2.0 * g)
h0_Z0        = h0 / Z0


# ════════════════════════════════════════════════════════════
# ÉTAPE 1
# ════════════════════════════════════════════════════════════
st.header("Étape 1 — Paramètres Initiaux")

# 4 métriques : sur mobile → 2×2, sur desktop → 1×4
col_a, col_b = st.columns(2)
col_c, col_d = st.columns(2)
col_a.metric("Pression Statique Z₀",  f"{Z0:.2f} mCE")
col_b.metric("Hauteur Cinétique h₀",  f"{h0:.4f} mCE")
col_c.metric("Ratio Zmax / Z₀",       f"{Zmax_Z0:.4f}")
col_d.metric("Ratio h₀ / Z₀",         f"{h0_Z0:.2e}")

st.markdown("---")


# ════════════════════════════════════════════════════════════
# ÉTAPE 2
# ════════════════════════════════════════════════════════════
st.header("Étape 2 — Valeur U₀/(L·S)")

log_h            = math.log10(h0_Z0)
val              = (Zmax_Z0 - 1.10) / 1.1667
log_u            = (0.30 - 0.12 * (log_h + 3.5) - val) / 0.25 - 2.5
U0_LS_theorique  = 10 ** log_u

# Sur mobile on empile radio + input
mode_abaque = st.radio(
    "Méthode U₀/(L·S) :",
    ["Calcul Automatique", "Personnalisée"],
    horizontal=True,
)

if mode_abaque == "Calcul Automatique":
    U0_LS = float(U0_LS_theorique)
    st.info(f"Valeur calculée : **{U0_LS:.6f}**")
else:
    U0_LS = st.number_input(
        "Valeur lue sur l'abaque :",
        value=float(U0_LS_theorique),
        step=0.001,
        format="%.6f",
    )

st.markdown("---")


# ════════════════════════════════════════════════════════════
# ÉTAPE 3
# ════════════════════════════════════════════════════════════
st.header("Étape 3 — Volumes & Nomogramme")

y_left   = (math.log10(h0_Z0) - (-5.0)) / (-2.0 - (-5.0))
y_center = (math.log10(U0_LS) - (-4.0)) / (-1.0 - (-4.0))
y_right  = 2 * y_center - y_left

Zmaxi_adjusted = Zmaxi
S      = math.pi * D**2 / 4.0
U0_L   = 1000.0 * U0_LS * L * S
Ve_L   = U0_L * (Z0 / Zmaxi_adjusted)
V_m3   = math.ceil(U0_L / 1000.0)

# 4 métriques 2×2
col_e, col_f = st.columns(2)
col_g, col_h = st.columns(2)
col_e.metric("Célérité C",           f"{round(C)} m/s")
col_f.metric("Surpression Max (B)",  f"{B:.2f} mCE")
col_g.metric("Volume d'Air U₀",      f"{U0_L:.2f} L")
col_h.metric("Volume Réservoir V",   f"{V_m3} m³")

st.markdown("---")


# ════════════════════════════════════════════════════════════
# ABAQUE INTERACTIF DE VIBERT (Planche XXVII)
# ════════════════════════════════════════════════════════════
st.subheader("📐 Abaque Interactif de M. Vibert — Planche XXVII")

st.info(
    f"Valeurs pré-chargées ▸  **h₀/Z₀ = {h0_Z0:.2e}**  |  **U₀/(L·S) = {U0_LS:.2e}**  \n"
    "Glissez les points sur l'abaque pour affiner la lecture de Zmin/Z₀ et Zmax/Z₀."
)

# Mantisse / exposant pour h0_Z0
_h_exp  = int(math.floor(math.log10(max(h0_Z0, 1e-9))))
_h_mant = h0_Z0 / (10 ** _h_exp)
_h_exp  = max(-4, min(-2, _h_exp))
_h_mant = round(_h_mant, 1)

# Mantisse / exposant pour U0_LS
_u_exp  = int(math.floor(math.log10(max(U0_LS, 1e-9))))
_u_mant = U0_LS / (10 ** _u_exp)
_u_exp  = max(-3, min(-1, _u_exp))
_u_mant = round(_u_mant, 1)

# Chargement + injection des valeurs calculées
_html_path = pathlib.Path(__file__).parent / "vibert_abaque.html"
_html_raw  = _html_path.read_text(encoding="utf-8")

_html_injected = _html_raw \
    .replace('id="hMant" min="1" max="9.99" step="0.1" value="8"',
             f'id="hMant" min="1" max="9.99" step="0.1" value="{_h_mant}"') \
    .replace('<option value="-2" selected>-2</option>\n        <option value="-3">-3</option>\n        <option value="-4">-4</option>',
             f'<option value="-2"{" selected" if _h_exp==-2 else ""}>-2</option>\n        '
             f'<option value="-3"{" selected" if _h_exp==-3 else ""}>-3</option>\n        '
             f'<option value="-4"{" selected" if _h_exp==-4 else ""}>-4</option>') \
    .replace('id="uMant" min="1" max="9.99" step="0.1" value="1"',
             f'id="uMant" min="1" max="9.99" step="0.1" value="{_u_mant}"') \
    .replace('<option value="-1" selected>-1</option>\n        <option value="-2">-2</option>\n        <option value="-3">-3</option>',
             f'<option value="-1"{" selected" if _u_exp==-1 else ""}>-1</option>\n        '
             f'<option value="-2"{" selected" if _u_exp==-2 else ""}>-2</option>\n        '
             f'<option value="-3"{" selected" if _u_exp==-3 else ""}>-3</option>')

components.html(_html_injected, height=750, scrolling=True)
