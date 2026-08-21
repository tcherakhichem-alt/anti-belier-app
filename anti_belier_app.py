import math

def resolver_abaque_u0_ls(h0_Z0, Zmax_Z0):
    log_h = math.log10(h0_Z0)
    val = (Zmax_Z0 - 1.10) / 1.1667
    log_u = (0.30 - 0.12 * (log_h + 3.5) - val) / 0.25 - 2.5
    return 10 ** log_u

def dimensionner_anti_belier():
    print("===============================================================")
    print(" PROGRAMME DE DIMENSIONNEMENT DU RÉSERVOIR ANTI-BÉLIER ")
    print("===============================================================\n")
    
    print("--- أدخل معطيات المشروع (اضغط Enter لاستعمال القيم الافتراضية) ---")
    D_int_mm = float(input("1. Diamètre intérieur D (mm) [افتراضي 327.4] : ") or 327.4)
    DN_mm = float(input("2. Diamètre nominal DN (mm) [افتراضي 800] : ") or 800.0)
    L = float(input("3. Longueur de refoulement L (m) [افتراضي 860] : ") or 860.0)
    Hg = float(input("4. Hauteur Géométrique Hg (mCE) [افتراضي 120] : ") or 120.0)
    Q_m3h = float(input("5. Débit Q (m3/h) [افتراضي 454] : ") or 454.0)
    PN_bar = float(input("6. Pression Nominale PN (Bar) [افتراضي 16] : ") or 16.0)
    E_conduite = float(input("7. Module d'élasticité E (Pa) [افتراضي 1.2e9] : ") or 1.2e9)
    
    epsilon_eau = 2.05e9
    rho = 1000.0
    g = 9.81

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
    
    U0_LS = resolver_abaque_u0_ls(h0_Z0, Zmax_Z0)
    
    S = math.pi * (D ** 2) / 4.0
    U0_L = 1000.0 * U0_LS * L * S
    Ve_L = U0_L * (Z0 / Zmaxi)
    V_m3 = math.ceil(U0_L / 1000.0)
    
    print("\n" + "="*55)
    print(" RÉSULTATS DU DIMENSIONNEMENT ")
    print("="*55)
    print(f"• Célérité C (m/s) : {C} m/s")
    print(f"• Vitesse U (m/s) : {U:.2f} m/s")
    print(f"• Coup de Bélier B : {B:.2f} mCE ({delta_P_bar:.2f} Bar)")
    print(f"• Pression Max ΔP+ : {delta_P_plus:.2f} mCE")
    print(f"• Rapport h0 / Z0 : {h0_Z0:.6f}")
    print(f"• Rapport Zmax / Z0 : {Zmax_Z0:.4f}")
    print(f"• Valeur de l'Abaque U0/(L.S): {U0_LS:.6f}")
    print("-" * 55)
    print(f" VOLUME D'AIR U0 : {U0_L:.2f} Litres")
    print(f" VOLUME D'EAU Ve : {Ve_L:.2f} Litres")
    print(f" >>> VOLUME DU RÉSERVOIR : {U0_L:.2f} L (~ {V_m3} m³)")
    print("="*55)

if __name__ == "__main__":
    dimensionner_anti_belier()
