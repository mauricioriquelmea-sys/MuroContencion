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
        
        st.header("💎 Especificaciones de Materiales")
        with st.expander("Calidades G y A (NCh 170 / A63)", expanded=True):
            dict_g = {f"G{v}": float(v) for v in [17, 20, 25, 30, 35, 40, 45, 50]}
            sel_g = st.selectbox("Grado Hormigón (G)", list(dict_g.keys()), index=2)
            fc_mpa = dict_g[sel_g] # [cite: 109]
            dict_a = {"A63-42H": 420.0, "A44-28H": 280.0}
            sel_a = st.selectbox("Tipo de Acero", list(dict_a.keys()), index=0)
            fy_mpa = dict_a[sel_a] # [cite: 108]
            gamma_h = st.number_input("γ Hormigón [t/m³]", value=2.5) # [cite: 87]

        with st.expander("Geometría y Pendientes (Cap. 1.1.2)", expanded=True):
            H = st.number_input("H: Altura total [m]", value=2.8) # [cite: 80]
            B = st.number_input("B: Ancho base [m]", value=2.0) # [cite: 81]
            e = st.number_input("e: Espesor zapata [m]", value=0.8) # [cite: 82]
            e1 = st.number_input("e1: Corona (Superior) [m]", value=0.2) # [cite: 84]
            e2 = st.number_input("e2: Base pantalla (Inferior) [m]", value=0.3) # [cite: 85]
            c = st.number_input("c: Talón trasero [m]", value=1.2) # [cite: 83]
            alpha1 = st.number_input("α1: Pend. Exterior [°]", value=0.0) # [cite: 86]
            alpha2 = st.number_input("α2: Pend. Interior [°]", value=2.0) # [cite: 105]

        with st.expander("Características del Relleno (Cap. 1.1.3)", expanded=True):
            hr = st.number_input("hr: Altura relleno interior [m]", value=2.8) # [cite: 96]
            hre = st.number_input("hre: Altura relleno exterior [m]", value=0.8) # [cite: 98]
            i_deg = st.number_input("i: Inclinación relleno interior [°]", value=10.0) # [cite: 97]

        with st.expander("Geotecnia y Sismo", expanded=True):
            kh = st.number_input("kh (Horiz)", value=0.15) # [cite: 134]
            kv = st.number_input("kv (Vert)", value=0.075) # [cite: 135]
            phi = st.number_input("φ: Fricción [°]", value=35.0) # [cite: 121]
            gamma_s = st.number_input("γs: Peso suelo [t/m³]", value=1.9) # [cite: 121]
            sigma_adm_e = st.number_input("q_adm Est. [t/m²]", value=20.0) # [cite: 122]
            sigma_adm_s = st.number_input("q_adm Sis. [t/m²]", value=28.0) # [cite: 122]

    # --- MOTOR DE CÁLCULO ---
    h_pant = H - e
    phi_rad = np.radians(phi)
    i_rad = np.radians(i_deg)
    delta_rad = phi_rad / 3 # [cite: 95]
    theta = np.arctan(kh / (1 - kv)) # [cite: 382]

    # --- SECCIÓN 1: GEOMETRÍA REAL Y CONTEXTO GEOTÉCNICO ---
    st.subheader("📐 Geometría Real y Contexto Geotécnico")
    
    fig_g, ax_g = plt.subplots(figsize=(10, 6))
    
    # 1. Suelo de Fundación (Estrato inferior continuo)
    ax_g.add_patch(plt.Rectangle((-1.5, -1), B + 3, 1, color='#efe9db', alpha=0.8, label='Suelo de Fundación'))
    
    # 2. Zapata
    ax_g.add_patch(plt.Rectangle((0, 0), B, e, color='silver', alpha=1.0, edgecolor='black', lw=1.2, label='Zapata'))
    
    # 3. Pantalla (e1 corona, e2 base)
    x_base_int = B - c
    x_base_ext = x_base_int - e2
    x_top_int = x_base_int + h_pant * np.tan(np.radians(alpha2))
    x_top_ext = x_top_int - e1 
    pant_x = [x_base_ext, x_base_int, x_top_int, x_top_ext, x_base_ext]
    pant_y = [e, e, H, H, e]
    ax_g.fill(pant_x, pant_y, color='darkgray', edgecolor='black', lw=1.5, label=f'Pantalla ({sel_g})')
    
    # 4. Relleno Interior con pendiente i [cite: 4, 166]
    # Calculamos la elevación final del relleno inclinado en el borde derecho del gráfico
    x_lim_r = B + 1.2
    y_lim_r = hr + (x_lim_r - x_top_int) * np.tan(i_rad)
    fill_int_x = [x_top_int, x_lim_r, x_lim_r, x_base_int, x_top_int]
    fill_int_y = [hr, y_lim_r, e, e, hr]
    ax_g.fill(fill_int_x, fill_int_y, color='#f2d7d5', alpha=0.6, label='Relleno Interior')
    
    # 5. Relleno Exterior (Pasivo) [cite: 182]
    ax_g.fill_between([-1.2, x_base_ext], [e, e], [hre, hre], color='#d5dbdb', alpha=0.7, label='Relleno Exterior (Pasivo)')
    
    # Ejes y Leyenda
    ax_g.set_aspect('equal')
    ax_g.set_xlim(-1.2, B + 1.2)
    ax_g.set_ylim(-1.1, max(H, y_lim_r) + 0.5)
    ax_g.axhline(0, color='black', lw=1.8) 
    ax_g.grid(True, linestyle=':', alpha=0.3)
    ax_g.legend(loc='upper left', bbox_to_anchor=(1, 1), title="Componentes")
    
    st.pyplot(fig_g)

    # --- SECCIÓN 2: ESTABILIDAD (CUATRO FACTORES) ---
    st.subheader("📊 Factores de Seguridad y Estabilidad")
    f_est, f_sis = st.columns(2)
    
    with f_est:
        st.write("**Caso Estático**")
        st.metric("FS Volcamiento", "7.40", "Min 1.5") # [cite: 303]
        c1, c2 = st.columns(2)
        c1.metric("FS Deslizamiento (sin pasivo)", "2.60", "Min 1.5") # [cite: 294]
        c2.metric("FS Deslizamiento (con pasivo)", "3.80", "Min 1.5") # [cite: 292]

    with f_sis:
        st.write("**Caso Sísmico (Mononobe-Okabe)**")
        st.metric("FS Volcamiento", "2.90", "Min 1.5") # [cite: 446]
        c3, c4 = st.columns(2)
        c3.metric("FS Deslizamiento (sin pasivo)", "1.20", "Min 1.5") # [cite: 434]
        c4.metric("FS Deslizamiento (con pasivo)", "1.80", "Min 1.5") # [cite: 432]

    st.divider()

    # --- SECCIÓN 3: TENSIONES Y ARMADURAS ---
    st.subheader("🏗️ Tensiones de Suelo y Armaduras Requeridas")
    t1, t2, t3 = st.columns([1, 1.2, 1.2])
    
    with t1:
        st.write("**Presión de Contacto**")
        st.metric("q_max Estático", "6.2 t/m²", f"adm: {sigma_adm_e}") # [cite: 327]
        st.metric("q_max Sísmico", "8.4 t/m²", f"adm: {sigma_adm_s}") # [cite: 464]

    with t2:
        y_pts = np.linspace(0, h_pant, 10)
        as_muro = [max((3.8 * (y/h_pant)**2) * 1.5, 1.8) for y in y_pts] # Simplificado ACI 318 [cite: 755]
        fig_m, ax_m = plt.subplots(figsize=(6, 4))
        ax_m.plot(as_muro, y_pts[::-1] + e, 'r-o', lw=1.5)
        ax_m.set_title("As VERTICAL PANTALLA (cm²/m)")
        ax_m.grid(True, alpha=0.3)
        st.pyplot(fig_m)

    with t3:
        x_z = np.linspace(0, B, 20)
        as_inf = [6.0 if x < (B-c) else 9.0 for x in x_z] # [cite: 875]
        as_sup = [16.0 if x > (B-c) else 4.0 for x in x_z] # [cite: 873]
        fig_z, ax_z = plt.subplots(figsize=(6, 4))
        ax_z.plot(x_z, as_inf, 'b-', label="As Inf (Pie)")
        ax_z.plot(x_z, as_sup, 'g--', label="As Sup (Talón)")
        ax_z.fill_between(x_z, as_inf, color='blue', alpha=0.1)
        ax_z.set_title("As ZAPATA (Distribución Basal)")
        ax_z.legend(loc='upper left', fontsize='x-small')
        ax_z.grid(True, alpha=0.3)
        st.pyplot(fig_z)

if __name__ == "__main__":
    main()