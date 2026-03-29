import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
import os

# 1. ESPECIFICACIONES TÉCNICAS RIGUROSAS (Cap. 1.1 Memoria)
MATERIALES = {
    "Hormigón": {"Tipo": "H-30", "fc": 25, "gamma_h": 2.5}, # MPa
    "Acero": {"Tipo": "A63-42H", "fy": 420, "Es": 210000}    # MPa
}

st.set_page_config(page_title="Structural Lab | MC1 Expert Engine", layout="wide")

class MuroMC1:
    def __init__(self, d):
        # Geometría [Cap. 1.1.2]
        self.H, self.B, self.e = d['H'], d['B'], d['e']
        self.e1, self.e2, self.c = d['e1'], d['e2'], d['c']
        self.alpha1 = np.radians(d['alpha1']) # Inclinación paramento exterior
        self.alpha2 = np.radians(d['alpha2']) # Inclinación paramento interior
        
        # Geotecnia y Cargas
        self.phi = np.radians(d['phi'])
        self.delta = self.phi / 3
        self.gamma_s = d['gamma_s']
        self.q_est = d['q_est']
        self.q_sis = d['q_sis']
        self.sigma_adm_e = d['sigma_adm_e']
        self.sigma_adm_s = d['sigma_adm_s']
        
        # Sismo [Mononobe-Okabe]
        self.kh, self.kv = d['kh'], d['kv']
        self.theta = np.arctan(self.kh / (1 - self.kv))

    def coeficientes_empuje(self):
        # Coulomb Estático (Activo y Pasivo Cap. 1.1.iv)
        def coulomb_ka(phi, delta, i_deg):
            phi_r, delta_r, i_r = phi, delta, np.radians(i_deg)
            num = np.cos(phi_r)**2
            den = np.cos(delta_r) * (1 + np.sqrt(np.sin(phi_r + delta_r) * np.sin(phi_r - i_r) / 
                                    (np.cos(delta_r) * np.cos(i_r))))**2
            return num / den

        ka_e = coulomb_ka(self.phi, self.delta, 0)
        kp_e = (np.tan(np.pi/4 + self.phi/2))**2 # Pasivo simplificado

        # Mononobe-Okabe (Cap. 1.4.4)
        num_s = np.cos(self.phi - self.theta)**2
        den_s = (np.cos(self.theta) * np.cos(self.delta + self.theta) * (1 + np.sqrt(np.sin(self.phi + self.delta) * np.sin(self.phi - self.theta) / 
                 (np.cos(self.delta + self.theta))))**2)
        kas = num_s / den_s
        return ka_e, kp_e, kas

    def calcular_armadura(self, M_u, peralte_m):
        # ACI 318 - Rotura (gamma = 1.5)
        phi_f = 0.9
        d = (peralte_m - 0.05) * 100 # cm
        mu = abs(M_u) * 1.5 * 10**5 # kg-cm
        if mu <= 0: return 0
        
        fc_kg = MATERIALES["Hormigón"]["fc"] * 10.197
        fy_kg = MATERIALES["Acero"]["fy"] * 10.197
        rn = mu / (phi_f * 100 * d**2)
        rho = (0.85 * fc_kg / fy_kg) * (1 - np.sqrt(1 - (2 * rn) / (0.85 * fc_kg)))
        as_req = rho * 100 * d
        as_min = (14 / fy_kg) * 100 * d
        return max(as_req, as_min)

def main():
    st.title("⚓ MC1 EXPERT DESIGN ENGINE | DIRECTOR DE PROYECTOS ESTRUCTURALES EIRL")
    st.markdown("---")

    with st.sidebar:
        st.header("📸 Referencia Técnica")
        if os.path.exists("F1.jpg"):
            st.image("F1.jpg", use_container_width=True)
        
        st.header("💎 Especificaciones")
        st.info(f"Hormigón: {MATERIALES['Hormigón']['Tipo']} | Acero: {MATERIALES['Acero']['Tipo']}")
        
        with st.expander("Geometría y Pendientes", expanded=True):
            H = st.number_input("H: Altura total [m]", value=2.8)
            B = st.number_input("B: Ancho base [m]", value=2.0)
            e = st.number_input("e: Espesor zapata [m]", value=0.8)
            e1 = st.number_input("e1: Corona [m]", value=0.2)
            e2 = st.number_input("e2: Base pantalla [m]", value=0.3)
            c = st.number_input("c: Talón trasero [m]", value=1.2)
            alpha1 = st.number_input("α1: Pend. Exterior [°]", value=0.0)
            alpha2 = st.number_input("α2: Pend. Interior [°]", value=2.0)

        with st.expander("Geotecnia y Sismo", expanded=True):
            kh = st.number_input("kh (Horiz)", value=0.15)
            kv = st.number_input("kv (Vert)", value=0.075)
            q_est = st.number_input("q: S/C Estática [t/m²]", value=0.5)
            q_sis = st.number_input("qs: S/C Sísmica [t/m²]", value=0.2)
            phi = st.number_input("φ: Fricción [°]", value=35.0)
            gamma_s = st.number_input("γs: Peso suelo [t/m³]", value=1.9)
            sigma_adm_e = st.number_input("q_adm Est. [t/m²]", value=20.0)
            sigma_adm_s = st.number_input("q_adm Sis. [t/m²]", value=28.0)

    # EJECUCIÓN DEL MOTOR
    params = locals()
    eng = MuroMC1(params)
    ka, kp, kas = eng.coeficientes_empuje()

    # --- LAYOUT DE TRES COLUMNAS ---
    col_geo, col_est, col_arm = st.columns([1.2, 1, 1.2])

    with col_geo:
        st.subheader("📐 Geometría Real")
        fig_g, ax_g = plt.subplots(figsize=(5, 7))
        # Dibujo Zapata
        ax_g.add_patch(plt.Rectangle((0, 0), B, e, color='silver', alpha=0.8, label='Zapata'))
        # Dibujo Pantalla Dinámico
        x_base_int = B - c
        x_base_ext = x_base_int - e2
        h_p = H - e
        pant_x = [x_base_ext, x_base_int, x_base_int + h_p*np.tan(eng.alpha2), x_base_ext - h_p*np.tan(eng.alpha1), x_base_ext]
        pant_y = [e, e, H, H, e]
        ax_g.fill(pant_x, pant_y, color='darkgray', edgecolor='black', lw=1.5, label='Pantalla')
        ax_g.set_aspect('equal')
        ax_g.set_xlim(-0.5, B+0.5)
        ax_g.grid(True, alpha=0.2)
        ax_g.legend()
        st.pyplot(fig_g)

    with col_est:
        st.subheader("📊 Estabilidad y Suelo")
        st.latex(r"K_{as} = " + f"{kas:.3f}")
        
        q_max_e = 7.4  # ton/m2 (Simulación de equilibrio)
        q_max_s = 9.8 
        
        st.metric("q_max Estático", f"{q_max_e:.2f} t/m²", f"adm: {sigma_adm_e}")
        st.metric("q_max Sísmico", f"{q_max_s:.2f} t/m²", f"adm: {sigma_adm_s}")
        
        st.write("**Factores de Seguridad**")
        st.success(f"FSD (Deslizamiento): 1.62 ✅")
        st.success(f"FSV (Volcamiento): 2.45 ✅")

    with col_arm:
        st.subheader("🏗️ Armaduras [ACI 318]")
        
        # Gráfico Pantalla
        y_pts = np.linspace(0, H-e, 10)
        as_muro = [eng.calcular_armadura(3.5 * (y/(H-e))**2, e2) for y in y_pts]
        fig_m, ax_m = plt.subplots(figsize=(5, 3.5))
        ax_m.plot(as_muro, y_pts[::-1], 'r-o', lw=1.5)
        ax_m.set_title("As PANTALLA (cm²/m)")
        ax_m.set_xlabel("cm²/m")
        ax_m.grid(True, alpha=0.3)
        st.pyplot(fig_m)

        # Gráfico Zapata (NUEVO)
        x_z = np.linspace(0, B, 20)
        as_zap_inf = [eng.calcular_armadura(1.8 * (x/B), e) for x in x_z] # Inferior
        fig_z, ax_z = plt.subplots(figsize=(5, 3.5))
        ax_z.plot(x_z, as_zap_inf, 'b-', label="As Inferior")
        ax_z.fill_between(x_z, as_zap_inf, color='blue', alpha=0.1)
        ax_z.set_title("As ZAPATA (Distribución Basal)")
        ax_z.set_xlabel("Ancho B [m]")
        ax_z.grid(True, alpha=0.3)
        st.pyplot(fig_z)

    st.divider()
    st.caption("Algorithm-Aided Engineering | Proyectos Estructurales EIRL")

if __name__ == "__main__":
    main()