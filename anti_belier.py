import math
import streamlit as st
import streamlit.components.v1 as components

def dimensionner_anti_belier():
    st.set_page_config(page_title="Dimensionnement Anti-Bélier", layout="wide")
    
    st.title("⚡ PROGRAMME DE DIMENSIONNEMENT DU RÉSERVOIR ANTI-BÉLIER")
    st.write("---")
    
    # 1. Inputs de l'utilisateur
    st.subheader("1. Paramètres d'entrée")
    
    col1, col2 = st.columns(2)
    
    with col1:
        D_int_mm = st.number_input("1. Diamètre intérieur D (mm)", value=327.4, step=1.0)
        DN_mm = st.number_input("2. Diamètre nominal DN (mm)", value=800.0, step=1.0)
        L = st.number_input("3. Longueur de refoulement L (m)", value=860.0, step=10.0)
        Hg = st.number_input("4. Hauteur Géométrique Hg (mCE)", value=120.0, step=1.0)
        
    with col2:
        Q_m3h = st.number_input("5. Débit Q (m3/h)", value=454.0, step=10.0)
        PN_bar = st.number_input("6. Pression Nominale PN (Bar)", value=16.0, step=1.0)
        E_conduite = st.number_input("7. Module d'élasticité E (Pa) [ex: 1.2e9 pour PEHD]", value=1.2e9, format="%e")

    epsilon_eau = 2.05e9
    rho = 1000.0
    g = 9.81

    # 2. Calculs préliminaires
    D = D_int_mm / 1000.0
    DN = DN_mm / 1000.0
    e = (DN - D) / 2.0
    
    C = round(math.sqrt(1.0 / (rho * ((1.0 / epsilon_eau) + (D / (E_conduite * e))))))
    Q_m3s = Q_m3h / 3600.0
    U = (4.0 * Q_m3s) / (math.pi * (D ** 2))
    
    B = (C * U) / g
    delta_P_bar = (rho * C * U) * 1e-5
    delta_P_plus = B + Hg
    PN_mCE = (PN_bar * 1e5) / (rho * g)
    
    Patm_mCE = 1e5 / (rho * g)
    Z0 = Hg + Patm_mCE
    Zmaxi = PN_mCE + Patm_mCE
    
    Zmax_Z0 = Zmaxi / Z0
    h0_Z0 = (U ** 2) / (2.0 * g * Z0)
    
    # 3. Saisie Manuelle de la valeur de l'Abaque
    st.write("---")
    st.subheader("2. Lecture de l'Abaque")
    
    col_ab1, col_ab2 = st.columns(2)
    with col_ab1:
        st.info(f"• **Rapport h0 / Z0 :** `{h0_Z0:.6f}`\n\n• **Rapport Zmax / Z0 :** `{Zmax_Z0:.4f}`")
    
    with col_ab2:
        U0_LS = st.number_input("✍️ Entrez la valeur U0/(L.S) lue sur l'abaque :", value=0.015000, format="%.6f", step=0.000100)

    # Calcul des volumes selon la valeur saisie
    S = math.pi * (D ** 2) / 4.0
    U0_L = 1000.0 * U0_LS * L * S
    Ve_L = U0_L * (Z0 / Zmaxi)
    V_m3 = math.ceil(U0_L / 1000.0)
    
    # 4. Affichage des résultats
    st.write("---")
    st.subheader("📊 RÉSULTATS DU DIMENSIONNEMENT")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Célérité des ondes (C)", f"{C} m/s")
    m2.metric("Vitesse d'écoulement (U)", f"{U:.2f} m/s")
    m3.metric("Surpression (Coup de Bélier)", f"{B:.2f} mCE", f"{delta_P_bar:.2f} Bar")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.info(f"**Pression Max (ΔP+) :** {delta_P_plus:.2f} mCE")
        st.write(f"• **Rapport h0 / Z0 :** `{h0_Z0:.6f}`")
        st.write(f"• **Rapport Zmax / Z0 :** `{Zmax_Z0:.4f}`")
        st.write(f"• **Valeur U0/(L.S) appliquée :** `{U0_LS:.6f}`")

    with col_r2:
        st.success(f"💧 **VOLUME D'AIR (U0) :** {U0_L:.2f} Litres")
        st.warning(f"🌊 **VOLUME D'EAU À ABSORBER :** {Ve_L:.2f} Litres")
        st.error(f"🚀 **VOLUME RÉSERVOIR :** {U0_L:.2f} L (~ **{V_m3} m³**)")

    # 5. Affichage de l'Abaque HTML
    st.write("---")
    st.subheader("📈 ABAQUE DE VIBERT INTERACTIF")
    
    try:
        with open("vibert_abaque.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        components.html(html_content, height=600, scrolling=True)
    except FileNotFoundError:
        st.error("Le fichier `vibert_abaque.html` est introuvable sur GitHub.")

if __name__ == "__main__":
    dimensionner_anti_belier()
