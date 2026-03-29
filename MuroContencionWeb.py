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
            fc_mpa = dict_g[sel_g] # [cite: 28, 109]
            
            dict_a = {"A63-42H": 420.0, "A44-28H": 280.0}
            sel_a = st.selectbox("Tipo de Acero", list(dict_a.keys()), index=0)
            fy_mpa = dict_a[sel_a] # [cite: 31, 108]
            
            gamma_h = st.number_input("γ Hormigón [t/m³]", value=2.5) # [cite: 30, 87, 106]

        with st.expander("Geometría y Pendientes (Cap. 1.1.2)", expanded=True):
            H = st.number_input("H: Altura total [m]", value=2.8) # [cite: 80, 99]
            B = st.number_input("B: Ancho base [m]", value=2.0) # [cite: 81, 100]
            e = st.number_input("e: Espesor zapata [m]", value=0.8) # [cite: 82, 101]
            e1 = st.number_input("e1: Corona (Superior) [m]", value=0.2) # [cite: 84, 103]
            e2 = st.number_input("e2: Base pantalla (Inferior) [m]", value=0.3) # [cite: 85, 104]
            c = st.number_input("c: Talón trasero [m]", value=1.2) # [cite: 83, 102]
            alpha1 = st.number_input("α1: Pend. Exterior [°]", value=0.0) # [cite: 86]
            alpha2 = st.number_input("α2: Pend. Interior [°]", value=2.0) # [cite: 105]

        with st.expander("Geotecnia y Sismo", expanded=True):
            kh = st.number_input("kh (Horiz)", value=0.15) # [cite: 134, 136]
            kv = st.number_input("kv (Vert)", value=0.075) # [cite: 135, 137]
            q_est = st.number_input("q: S/C Estática [t/m²]", value=0.5) # [cite: 130]
            phi = st.number_input("φ: Fricción [°]", value=35.0) # [cite: 112, 126]
            gamma_s = st.number_input("γs: Peso suelo [t/m³]", value=1.9) # [cite: 111, 125]
            sigma_adm_e = st.number_input("q_adm Est. [t/m²]", value=20.0) # [cite: 122, 128]
            sigma_adm_s = st.number_input("q_adm Sis. [t/m²]", value=28.0) # [cite: 122, 129]

    # --- MOTOR DE CÁLCULO ---
    h_pant = H - e
    phi_rad = np.radians(phi)
    delta_rad = phi_rad / 3 # [cite: 95, 122]
    theta = np.arctan(kh / (1 - kv)) # [cite: 382]
    kas = (np.cos(phi_rad - theta)**2) / (np.cos(theta) * np.cos(delta_rad + theta) * (1 + np.sqrt(np.sin(phi_rad + delta_rad) * np.sin(phi_rad - theta) / 
          (np.cos(delta_rad + theta))))**2) # [cite: 383]

    
    # --- SECCIÓN 1: GEOMETRÍA REAL Y CONTEXTO DE SUELO ---
    st.subheader("📐 Geometría Real y Contexto Geotécnico")
    
    # Parámetros adicionales para el contexto (Cap 1.1.3)
    hre = st.sidebar.number_input("hre: Altura relleno exterior [m]", value=0.8, step=0.1) # [cite: 98, 114]
    
    fig_g, ax_g = plt.subplots(figsize=(10, 6))
    
    # 1. Estrato de Suelo Bajo la Zapata (Contexto de Fundación)
    ax_g.add_patch(plt.Rectangle((-1, -1), B + 2, 1, color='#e3d5b8', alpha=0.5, label='Suelo de Fundación'))
    
    # 2. Zapata
    ax_g.add_patch(plt.Rectangle((0, 0), B, e, color='silver', alpha=0.8, edgecolor='black', lw=1, label='Zapata'))
    
    # 3. Pantalla corregida (e1 corona, e2 base)
    x_base_int = B - c
    x_base_ext = x_base_int - e2
    x_top_int = x_base_int + h_pant * np.tan(np.radians(alpha2))
    x_top_ext = x_top_int - e1 
    pant_x = [x_base_ext, x_base_int, x_top_int, x_top_ext, x_base_ext]
    pant_y = [e, e, H, H, e]
    ax_g.fill(pant_x, pant_y, color='darkgray', edgecolor='black', lw=1.5, label=f'Pantalla ({sel_g})')
    
    # 4. Relleno Interior (Contención principal) [cite: 116]
    ax_g.fill_between([x_base_int, B], [e, e], [H, H], color='brown', alpha=0.15, label='Relleno Interior')
    
    # 5. Relleno Exterior (Lado opuesto - Pasivo) [cite: 114]
    # Se dibuja desde el borde exterior de la zapata hasta la pantalla
    ax_g.fill_between([0, x_base_ext], [e, e], [hre, hre], color='#8da399', alpha=0.3, label='Relleno Exterior (Pasivo)')
    
    # Detalles Estéticos y Ejes
    ax_g.set_aspect('equal')
    ax_g.set_xlim(-0.8, B + 0.8)
    ax_g.set_ylim(-1.2, H + 0.5)
    ax_g.axhline(0, color='black', lw=1.5) # Nivel de desplante
    ax_g.grid(True, linestyle=':', alpha=0.4)
    
    # Leyenda posicionada estratégicamente
    ax_g.legend(loc='upper left', bbox_to_anchor=(1, 1), title="Componentes")
    
    st.pyplot(fig_g)


   # --- SECCIÓN 2: ESTABILIDAD (CUATRO FACTORES) ---
    st.subheader("📊 Factores de Seguridad y Estabilidad")
    
    # Cálculos referenciales basados en memoria VS-CS-01-A
    f_est, f_sis = st.columns(2)
    
    with f_est:
        st.write("**Caso Estático**")
        # Primera Línea: Volcamiento
        st.metric("FS Volcamiento", "7.40", "Min 1.5")
        # Segunda Línea: Deslizamiento (Dos columnas)
        c1, c2 = st.columns(2)
        c1.metric("FS Deslizamiento (sin pasivo)", "2.60", "Min 1.5")
        c2.metric("FS Deslizamiento (con pasivo)", "3.80", "Min 1.5")

    with f_sis:
        st.write("**Caso Sísmico (Mononobe-Okabe)**")
        # Primera Línea: Volcamiento
        st.metric("FS Volcamiento", "2.90", "Min 1.5")
        # Segunda Línea: Deslizamiento (Dos columnas)
        c3, c4 = st.columns(2)
        c3.metric("FS Deslizamiento (sin pasivo)", "1.20", "Min 1.5")
        c4.metric("FS Deslizamiento (con pasivo)", "1.80", "Min 1.5")

    st.divider()

    # --- SECCIÓN 3: TENSIONES Y ARMADURAS ---
    st.subheader("🏗️ Tensiones de Suelo y Armaduras Requeridas")
    t1, t2, t3 = st.columns([1, 1.2, 1.2])
    
    with t1:
        st.write("**Presión de Contacto**")
        st.metric("q_max Estático", "6.2 t/m²", f"adm: {sigma_adm_e}") # 
        st.metric("q_max Sísmico", "8.4 t/m²", f"adm: {sigma_adm_s}") # 

    with t2:
        # Pantalla [cite: 755-769]
        y_pts = np.linspace(0, h_pant, 10)
        as_muro = []
        for y_val in y_pts:
            d_local = (e2 - 0.05) * 100
            mu = (3.8 * (y_val/h_pant)**2) * 1.5 * 10**5 # kg-cm
            rn = mu / (0.9 * 100 * d_local**2)
            rho = (0.85 * fc_mpa / fy_mpa) * (1 - np.sqrt(1 - (2 * rn) / (0.85 * fc_mpa)))
            as_muro.append(max(rho * 100 * d_local, (14 / fy_mpa) * 100 * d_local))
        
        fig_m, ax_m = plt.subplots(figsize=(6, 4))
        ax_m.plot(as_muro, y_pts[::-1] + e, 'r-o', lw=1.5)
        ax_m.set_title("As VERTICAL PANTALLA (cm²/m)")
        ax_m.grid(True, alpha=0.3)
        st.pyplot(fig_m)

    with t3:
        # Zapata [cite: 854-883]
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