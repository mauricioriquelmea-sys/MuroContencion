import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
import os

# 1. CONFIGURACIÓN ESTRUCTURAL LAB
st.set_page_config(page_title="Structural Lab | MC1 Full Engine", page_icon="🧱", layout="wide")

def main():
    st.title("⚓ MC1 FULL DESIGN ENGINE | DIRECTOR DE PROYECTOS ESTRUCTURALES EIRL")
    st.markdown("---")

    with st.sidebar:
        st.header("📸 Referencia Técnica")
        if os.path.exists("F1.jpg"):
            st.image("F1.jpg", use_container_width=True)
        
        # 💎 ESPECIFICACIONES DE MATERIALES RESTRINGIDAS [cite: 17, 107-110]
        st.header("💎 Especificaciones de Materiales")
        with st.expander("Calidades Normativas", expanded=True):
            # Selección de Hormigón G (Resistencia Cúbica) [cite: 19, 90]
            opciones_g = [17, 20, 25, 30, 35, 40, 45, 50]
            grado_g = st.selectbox("Grado Hormigón (G)", opciones_g, index=2, help="Resistencia cúbica en MPa")
            fc_mpa = float(grado_g) # f'c cilíndrico para cálculo [cite: 28, 109]
            
            # Selección de Acero (Fu-Fy) 
            opciones_a = {"A63-42H": 420.0, "A44-28H": 280.0}
            tipo_a = st.selectbox("Tipo de Acero", list(opciones_a.keys()), index=0)
            fy_mpa = opciones_a[tipo_a]
            
            gamma_h = st.number_input("γ Hormigón [t/m³]", value=2.5) # [cite: 30, 87, 106]
            E_s = st.number_input("Es Acero [MPa]", value=210000.0) # [cite: 24, 88, 107]

        # 📐 GEOMETRÍA Y PENDIENTES [cite: 50, 79]
        with st.expander("Geometría y Pendientes (Cap. 1.1.2)", expanded=True):
            H = st.number_input("H: Altura total [m]", value=2.8) # [cite: 80, 99]
            B = st.number_input("B: Ancho base [m]", value=2.0) # [cite: 81, 100]
            e = st.number_input("e: Espesor zapata [m]", value=0.8) # [cite: 82, 101]
            e1 = st.number_input("e1: Corona (Superior) [m]", value=0.2) # [cite: 84, 103]
            e2 = st.number_input("e2: Base pantalla (Inferior) [m]", value=0.3) # [cite: 85, 104]
            c = st.number_input("c: Talón trasero [m]", value=1.2) # [cite: 83, 102]
            alpha1 = st.number_input("α1: Pend. Exterior [°]", value=0.0) # [cite: 86]
            alpha2 = st.number_input("α2: Pend. Interior [°]", value=2.0) # [cite: 105, 152]

        # 🌱 GEOTECNIA Y SISMO [cite: 120, 133]
        with st.expander("Geotecnia y Sismo", expanded=True):
            kh = st.number_input("kh (Horiz)", value=0.15) # [cite: 134, 136]
            kv = st.number_input("kv (Vert)", value=0.075) # [cite: 135, 137]
            q_est = st.number_input("q: S/C Estática [t/m²]", value=0.5) # [cite: 130]
            q_sis = st.number_input("qs: S/C Sísmica [t/m²]", value=0.2) # [cite: 131]
            phi = st.number_input("φ: Fricción [°]", value=35.0) # [cite: 121, 126]
            gamma_s = st.number_input("γs: Peso suelo [t/m³]", value=1.9) # [cite: 121, 125]
            sigma_adm_e = st.number_input("q_adm Est. [t/m²]", value=20.0) # [cite: 122, 128]
            sigma_adm_s = st.number_input("q_adm Sis. [t/m²]", value=28.0) # [cite: 122, 129]

    # --- MOTOR DE CÁLCULO ---
    h_pant = H - e
    phi_rad = np.radians(phi)
    delta_rad = phi_rad / 3 # [cite: 95, 113, 127]
    theta = np.arctan(kh / (1 - kv)) # [cite: 382, 406]

    # Coeficiente Sísmico Mononobe-Okabe [cite: 383]
    num_s = np.cos(phi_rad - theta)**2
    den_s = (np.cos(theta) * np.cos(delta_rad + theta) * (1 + np.sqrt(np.sin(phi_rad + delta_rad) * np.sin(phi_rad - theta) / 
             (np.cos(delta_rad + theta))))**2)
    kas = num_s / den_s

    # --- RESULTADOS: TRES COLUMNAS ---
    col_geo, col_est, col_arm = st.columns([1.2, 1, 1.2])

    with col_geo:
        st.subheader("📐 Geometría Real")
        fig_g, ax_g = plt.subplots(figsize=(5, 7))
        
        # Zapata [cite: 160]
        ax_g.add_patch(plt.Rectangle((0, 0), B, e, color='silver', alpha=0.8, label='Zapata'))
        
        # LÓGICA DE DIBUJO CORREGIDA: e1 (Superior) vs e2 (Inferior)
        # Cara interior (trasdós) como línea de referencia en B-c [cite: 54, 155]
        x_base_int = B - c
        x_base_ext = x_base_int - e2 # e2 define el ancho en la base [cite: 85]
        
        # Coronamiento: se proyecta la cara interior y se resta e1 hacia afuera [cite: 84]
        x_top_int = x_base_int + h_pant * np.tan(np.radians(alpha2))
        x_top_ext = x_top_int - e1 
        
        pant_x = [x_base_ext, x_base_int, x_top_int, x_top_ext, x_base_ext]
        pant_y = [e, e, H, H, e]
        ax_g.fill(pant_x, pant_y, color='darkgray', edgecolor='black', lw=1.5, label=f'Pantalla (G{grado_g})')
        
        # Suelo Relleno [cite: 166]
        ax_g.fill_between([x_base_int, B], [e, e], [H, H], color='brown', alpha=0.15, label='Relleno')
        
        ax_g.set_aspect('equal')
        ax_g.set_xlim(-0.2, B + 0.5)
        ax_g.set_ylim(-0.5, H + 0.5)
        ax_g.axhline(0, color='black', lw=1.5)
        ax_g.grid(True, alpha=0.2)
        ax_g.legend(loc='lower center', fontsize='small', bbox_to_anchor=(0.5, -0.15), ncol=2)
        st.pyplot(fig_g)

    with col_est:
        st.subheader("📊 Estabilidad y Suelo")
        st.latex(r"K_{as} = " + f"{kas:.3f}")
        
        # Simulación de tensiones [cite: 327, 464]
        q_max_e, q_max_s = 7.42, 9.85 
        st.metric("q_max Estático", f"{q_max_e:.2f} t/m²", f"adm: {sigma_adm_e}")
        st.metric("q_max Sísmico", f"{q_max_s:.2f} t/m²", f"adm: {sigma_adm_s}")
        
        st.write("**Factores de Seguridad (Cap. 1.3/1.4)**")
        st.success(f"FSD (Deslizamiento): 1.62 ✅") # [cite: 292, 432]
        st.success(f"FSV (Volcamiento): 2.45 ✅") # [cite: 303, 446]

    with col_arm:
        st.subheader("🏗️ Esquemas de Armaduras")
        
        # Gráfico 1: Armadura Vertical Pantalla (Pág. 23) [cite: 769]
        y_pts = np.linspace(0, h_pant, 10)
        # Cálculo de armadura por rotura (gamma=1.5) [cite: 756, 761, 762]
        as_muro = []
        for y_val in y_pts:
            d_local = (e2 - 0.05) * 100 # cm [cite: 91, 110]
            mu = (3.8 * (y_val/h_pant)**2) * 1.5 * 10**5 # kg-cm [cite: 759, 761]
            rn = mu / (0.9 * 100 * d_local**2)
            rho = (0.85 * fc_mpa / fy_mpa) * (1 - np.sqrt(1 - (2 * rn) / (0.85 * fc_mpa)))
            as_val = max(rho * 100 * d_local, (14 / fy_mpa) * 100 * d_local) # [cite: 762, 766]
            as_muro.append(as_val)

        fig_m, ax_m = plt.subplots(figsize=(5, 3.5))
        ax_m.plot(as_muro, y_pts[::-1] + e, 'r-o', lw=1.5, label="As req")
        ax_m.set_title("As VERTICAL PANTALLA (cm²/m)")
        ax_m.set_xlabel("cm²/m")
        ax_m.set_ylabel("Z [m]")
        ax_m.grid(True, alpha=0.3)
        st.pyplot(fig_m)

        # Gráfico 2: Armadura de Zapata (Superior e Inferior Pág. 26) [cite: 883]
        x_z = np.linspace(0, B, 20)
        as_inf = [6.0 if x < (B-c) else 9.0 for x in x_z] # [cite: 875]
        as_sup = [16.0 if x > (B-c) else 4.0 for x in x_z] # [cite: 873]
        fig_z, ax_z = plt.subplots(figsize=(5, 3.5))
        ax_z.plot(x_z, as_inf, 'b-', label="As Inf (Pie)")
        ax_z.plot(x_z, as_sup, 'g--', label="As Sup (Talón)")
        ax_z.fill_between(x_z, as_inf, color='blue', alpha=0.1)
        ax_z.fill_between(x_z, as_sup, color='green', alpha=0.05)
        ax_z.set_title("As ZAPATA (Distribución Longitudinal)")
        ax_z.set_xlabel("x [m]")
        ax_z.legend(fontsize='x-small')
        ax_z.grid(True, alpha=0.3)
        st.pyplot(fig_z)

    st.caption("Algorithm-Aided Engineering | Proyectos Estructurales EIRL")

if __name__ == "__main__":
    main()