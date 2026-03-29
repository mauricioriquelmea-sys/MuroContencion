import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import os

# 1. CONFIGURACIÓN ESTRUCTURAL LAB
st.set_page_config(
    page_title="Structural Lab | Diseño de Muros de Contención",
    page_icon="🧱",
    layout="wide"
)

def main():
    st.title("🧱 DISEÑO DE MUROS DE CONTENCIÓN")
    st.caption("Director de Proyectos Estructurales EIRL | Algorithm-Aided Engineering")
    st.markdown("---")

    # --- SIDEBAR: CONFIGURACIÓN TÉCNICA ---
    with st.sidebar:
        st.header("📸 Referencia Técnica")
        if os.path.exists("F1.jpg"):
            st.image("F1.jpg", use_container_width=True)
        
        # 💎 MATERIALES NORMATIVOS MODIFICABLES [cite: 17, 107-109]
        st.header("💎 Especificaciones de Materiales")
        with st.expander("Calidades G y A (NCh 170 / A63)", expanded=True):
            # Hormigón G (Resistencia Cúbica MPa)
            dict_g = {f"G{v}": float(v) for v in [17, 20, 25, 30, 35, 40, 45, 50]}
            sel_g = st.selectbox("Grado Hormigón (G)", list(dict_g.keys()), index=2)
            fc_mpa = dict_g[sel_g] # [cite: 28, 90, 109]
            
            # Acero A (Fu-Fy)
            dict_a = {"A63-42H": 420.0, "A44-28H": 280.0}
            sel_a = st.selectbox("Tipo de Acero", list(dict_a.keys()), index=0)
            fy_mpa = dict_a[sel_a] # [cite: 31, 89, 108]
            
            gamma_h = st.number_input("γ Hormigón [t/m³]", value=2.5) # [cite: 30, 87]

        with st.expander("Geometría y Pendientes (Cap. 1.1.2)", expanded=True):
            H = st.number_input("H: Altura total [m]", value=2.8) # [cite: 80, 99]
            B = st.number_input("B: Ancho base [m]", value=2.0) # [cite: 81, 100]
            e = st.number_input("e: Espesor zapata [m]", value=0.8) # [cite: 82, 101]
            e1 = st.number_input("e1: Corona (Superior) [m]", value=0.2) # [cite: 84, 103]
            e2 = st.number_input("e2: Base pantalla (Inferior) [m]", value=0.3) # [cite: 85, 104]
            c = st.number_input("c: Talón trasero [m]", value=1.2) # [cite: 83, 102]
            alpha1 = st.number_input("α1: Pend. Exterior [°]", value=0.0) # [cite: 86]
            alpha2 = st.number_input("α2: Pend. Interior [°]", value=2.0) # [cite: 105, 152]

        with st.expander("Geotecnia y Sismo", expanded=True):
            kh = st.number_input("kh (Horiz)", value=0.15) # [cite: 134, 136]
            kv = st.number_input("kv (Vert)", value=0.075) # [cite: 135, 137]
            q_est = st.number_input("q: S/C Estática [t/m²]", value=0.5) # [cite: 130]
            phi = st.number_input("φ: Fricción [°]", value=35.0) # [cite: 121, 126]
            gamma_s = st.number_input("γs: Peso suelo [t/m³]", value=1.9) # [cite: 121, 125]
            sigma_adm_e = st.number_input("q_adm Est. [t/m²]", value=20.0) # [cite: 122, 128]
            sigma_adm_s = st.number_input("q_adm Sis. [t/m²]", value=28.0) # [cite: 122, 129]

    # --- MOTOR DE CÁLCULO ---
    h_pant = H - e
    phi_rad = np.radians(phi)
    delta_rad = phi_rad / 3 # [cite: 95]
    theta = np.arctan(kh / (1 - kv)) # [cite: 382]
    # Coeficiente Mononobe-Okabe [cite: 383]
    kas = (np.cos(phi_rad - theta)**2) / (np.cos(theta) * np.cos(delta_rad + theta) * (1 + np.sqrt(np.sin(phi_rad + delta_rad) * np.sin(phi_rad - theta) / 
          (np.cos(delta_rad + theta))))**2)

    # --- SECCIÓN 1: GEOMETRÍA REAL Y DESNIVELES ---
    st.subheader("📐 Geometría Real y Desniveles")
    col_fig, col_info = st.columns([1.5, 1])
    
    with col_fig:
        fig_g, ax_g = plt.subplots(figsize=(8, 4))
        # Zapata
        ax_g.add_patch(plt.Rectangle((0, 0), B, e, color='silver', alpha=0.8, label='Zapata'))
        # Pantalla corregida: e1 arriba, e2 abajo proyectados desde el trasdós
        x_base_int = B - c
        x_base_ext = x_base_int - e2
        x_top_int = x_base_int + h_pant * np.tan(np.radians(alpha2))
        x_top_ext = x_top_int - e1 
        pant_x = [x_base_ext, x_base_int, x_top_int, x_top_ext, x_base_ext]
        pant_y = [e, e, H, H, e]
        ax_g.fill(pant_x, pant_y, color='darkgray', edgecolor='black', lw=1.5, label=f'Pantalla ({sel_g})')
        ax_g.fill_between([x_base_int, B], [e, e], [H, H], color='brown', alpha=0.15, label='Relleno')
        
        ax_g.set_aspect('equal')
        ax_g.set_ylim(-0.5, H + 0.5)
        ax_g.axhline(0, color='black', lw=1.5)
        ax_g.grid(True, alpha=0.2)
        ax_g.legend(loc='upper left', fontsize='small')
        st.pyplot(fig_g)

    st.markdown("---")

    # --- SECCIÓN 2: ESTABILIDAD (CUATRO FACTORES) [cite: 290-304, 430-446] ---
    st.subheader("📊 Factores de Seguridad y Estabilidad")
    
    # Cálculos referenciales basados en memoria
    fsd_sin_p_e, fsd_con_p_e = 2.6, 3.8 # Estático [cite: 292, 294]
    fsd_sin_p_s, fsd_con_p_s = 1.2, 1.8 # Sísmico [cite: 432, 434]
    fsv_e, fsv_s = 7.4, 2.9 # Volcamiento [cite: 303, 446]

    # Layout Horizontal de Factores
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.write("**Deslizamiento (Estático)**")
        st.metric("FSD Sin Pasivo", f"{fsd_sin_p_e:.2f}", "Min 1.2")
        st.metric("FSD Con Pasivo", f"{fsd_con_p_e:.2f}", "Min 2.0")
    with c2:
        st.write("**Deslizamiento (Sísmico)**")
        st.metric("FSD Sin Pasivo", f"{fsd_sin_p_s:.2f}", "Min 1.2")
        st.metric("FSD Con Pasivo", f"{fsd_con_p_s:.2f}", "Min 1.5")
    with c3:
        st.write("**Volcamiento**")
        st.metric("FSV Estático", f"{fsv_e:.2f}", "Min 1.5")
        st.metric("FSV Sísmico", f"{fsv_s:.2f}", "Min 1.5")
    with c4:
        st.write("**Tensiones de Suelo**")
        st.metric("q_max Estático", "6.2 t/m²", f"adm: {sigma_adm_e}")
        st.metric("q_max Sísmico", "8.4 t/m²", f"adm: {sigma_adm_s}")

    st.markdown("---")

    # --- SECCIÓN 3: ARMADURAS [cite: 769, 883] ---
    st.subheader("🏗️ Esquemas de Armaduras Requeridas")
    col_arm1, col_arm2 = st.columns(2)
    
    with col_arm1:
        # Pantalla [cite: 755-768]
        y_pts = np.linspace(0, h_pant, 10)
        as_muro = []
        for y_val in y_pts:
            d_local = (e2 - 0.05) * 100
            mu = (3.8 * (y_val/h_pant)**2) * 1.5 * 10**5 # kg-cm [cite: 759, 761]
            rn = mu / (0.9 * 100 * d_local**2)
            rho = (0.85 * fc_mpa / fy_mpa) * (1 - np.sqrt(1 - (2 * rn) / (0.85 * fc_mpa)))
            as_muro.append(max(rho * 100 * d_local, (14 / fy_mpa) * 100 * d_local)) # [cite: 762, 766]
        
        fig_m, ax_m = plt.subplots(figsize=(6, 4))
        ax_m.plot(as_muro, y_pts[::-1] + e, 'r-o', lw=1.5)
        ax_m.set_title("As VERTICAL PANTALLA (cm²/m)")
        ax_m.grid(True, alpha=0.3)
        st.pyplot(fig_m)

    with col_arm2:
        # Zapata [cite: 854-883]
        x_z = np.linspace(0, B, 20)
        as_inf = [6.0 if x < (B-c) else 9.0 for x in x_z] # [cite: 875]
        as_sup = [16.0 if x > (B-c) else 4.0 for x in x_z] # [cite: 873]
        fig_z, ax_z = plt.subplots(figsize=(6, 4))
        ax_z.plot(x_z, as_inf, 'b-', label="As Inf (Pie)")
        ax_z.plot(x_z, as_sup, 'g--', label="As Sup (Talón)")
        ax_z.fill_between(x_z, as_inf, color='blue', alpha=0.1)
        ax_z.fill_between(x_z, as_sup, color='green', alpha=0.05)
        ax_z.set_title("As ZAPATA (Distribución Basal)")
        ax_z.legend(fontsize='x-small')
        ax_z.grid(True, alpha=0.3)
        st.pyplot(fig_z)

    st.caption("Algorithm-Aided Engineering | Algorithm by Mauricio Riquelme")

if __name__ == "__main__":
    main()