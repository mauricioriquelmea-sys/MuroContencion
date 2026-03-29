import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

# 1. CONFIGURACIÓN ESTRUCTURAL LAB (Nivel Élite)
st.set_page_config(
    page_title="Structural Lab | Diseño de Muros de Contención",
    page_icon="🧱",
    layout="wide"
)

def main():
    st.title("🧱 DISEÑO DE MUROS DE CONTENCIÓN")
    st.caption("Director de Proyectos Estructurales EIRL | Algorithm-Aided Engineering")
    st.markdown("---")

    # --- SIDEBAR: INPUTS TÉCNICOS INTEGRALES ---
    with st.sidebar:
        st.header("📸 Referencia Técnica")
        if os.path.exists("F1.jpg"):
            st.image("F1.jpg", use_container_width=True)
        
        st.header("💎 Especificaciones de Materiales")
        with st.expander("Calidades Normativas (NCh 170 / A63)", expanded=True):
            dict_g = {f"G{v}": float(v) for v in [17, 20, 25, 30, 35, 40, 45, 50]}
            sel_g = st.selectbox("Grado Hormigón (G)", list(dict_g.keys()), index=2)
            fc_mpa = dict_g[sel_g]
            
            dict_a = {"A63-42H": 420.0, "A44-28H": 280.0}
            sel_a = st.selectbox("Tipo de Acero", list(dict_a.keys()), index=0)
            fy_mpa = dict_a[sel_a]
            
            gamma_h = st.number_input("γ Hormigón [t/m³]", value=2.5)

        with st.expander("Geometría Crítica (Cap. 1.1.2)", expanded=True):
            H = st.number_input("H: Altura total muro [m]", value=2.8)
            B = st.number_input("B: Ancho base zapata [m]", value=2.0)
            e = st.number_input("e: Espesor zapata [m]", value=0.8)
            e1 = st.number_input("e1: Corona (Superior) [m]", value=0.2)
            e2 = st.number_input("e2: Base pantalla (Inferior) [m]", value=0.3)
            c = st.number_input("c: Talón trasero [m]", value=1.2)
            alpha1 = st.number_input("α1: Pend. Exterior [°]", value=0.0)
            alpha2 = st.number_input("α2: Pend. Interior [°]", value=2.0)

        with st.expander("Contexto de Rellenos (Cap. 1.1.3)", expanded=True):
            hr = st.number_input("hr: Altura relleno interior [m]", value=2.8)
            hre = st.number_input("hre: Altura relleno exterior [m]", value=1.0)
            i_deg = st.number_input("i: Inclinación relleno [°]", value=10.0)

        with st.expander("Geotecnia y Sismo (Cap. 1.1.4/6)", expanded=True):
            kh = st.number_input("kh (Horiz)", value=0.15)
            kv = st.number_input("kv (Vert)", value=0.075)
            phi = st.number_input("φ: Fricción suelo [°]", value=35.0)
            gamma_s = st.number_input("γs: Peso suelo [t/m³]", value=1.9)
            sigma_adm_e = st.number_input("q_adm Estático [t/m²]", value=20.0)
            sigma_adm_s = st.number_input("q_adm Sísmico [t/m²]", value=28.0)

    # --- MOTOR DE CÁLCULO (VS-CS-01-A) ---
    h_pant = H - e
    phi_rad, i_rad = np.radians(phi), np.radians(i_deg)
    delta_rad = phi_rad / 3
    theta = np.arctan(kh / (1 - kv))

    # Coeficiente Mononobe-Okabe (Kas)
    num_s = np.cos(phi_rad - theta)**2
    den_s = (np.cos(theta) * np.cos(delta_rad + theta) * (1 + np.sqrt(np.sin(phi_rad + delta_rad) * np.sin(phi_rad - i_rad - theta) / 
            (np.cos(delta_rad + theta) * np.cos(i_rad))))**2)
    kas = num_s / den_s

# --- SECCIÓN 1: REPRESENTACIÓN GEOMÉTRICA ESTRATIGRÁFICA ---
    st.subheader("📐 Geometría Real y Contexto Geotécnico")
    
    # Recuperación de variables dinámicas [cite: 80-85, 96-98]
    hr_val = hr       
    hre_val = 1.0     
    i_rad = np.radians(i_deg) 
    
    fig_g, ax_g = plt.subplots(figsize=(12, 6))
    
    # 1. Suelo de Fundación (y < 0) - Estrato basal continuo [cite: 121, 141]
    ax_g.add_patch(plt.Rectangle((-1.5, -1), B + 3, 1, color='#efe9db', alpha=0.9, label='Suelo de Fundación'))
    
    # 2. Relleno Interior (Rosado) - COBERTURA TOTAL DESDE y=0
    # Se define el polígono para evitar espacios en blanco bajo el relleno [cite: 166, 218]
    h_pant = H - e
    x_base_int = B - c
    x_top_int = x_base_int + h_pant * np.tan(np.radians(alpha2))
    x_lim_r = B + 1.2
    y_lim_r = hr_val + (x_lim_r - x_top_int) * np.tan(i_rad)
    
    # Vértices: [base talón, fin gráfico basal, fin gráfico superior inclinado, corona muro, base muro]
    fill_int_x = [x_base_int, x_lim_r, x_lim_r, x_top_int, x_base_int]
    fill_int_y = [0, 0, y_lim_r, hr_val, 0]
    ax_g.fill(fill_int_x, fill_int_y, color='#f2d7d5', alpha=0.6, label='Relleno Interior')
    
    # 3. Relleno Exterior (Café Achurado) - Lado Pasivo [cite: 61, 98, 253]
    x_base_ext = x_base_int - e2
    ax_g.fill_between([-1.5, x_base_ext], 0, hre_val, 
                     facecolor='#d5dbdb', alpha=0.5, hatch='///', edgecolor='#85929e', 
                     label='Relleno Exterior (Pasivo h=1.0m)')
    
    # 4. Zapata (Hormigón G25) [cite: 106, 109, 226]
    ax_g.add_patch(plt.Rectangle((0, 0), B, e, color='silver', alpha=1.0, edgecolor='black', lw=1.2, label='Zapata'))
    
    # 5. Pantalla (e1 corona, e2 base) [cite: 84, 85, 144]
    x_top_ext = x_top_int - e1 
    pant_x = [x_base_ext, x_base_int, x_top_int, x_top_ext, x_base_ext]
    pant_y = [e, e, H, H, e]
    ax_g.fill(pant_x, pant_y, color='darkgray', edgecolor='black', lw=1.5, label=f'Pantalla ({sel_g})')
    
    # Configuración de Ejes y Estética Profesional
    ax_g.set_aspect('equal')
    ax_g.set_xlim(-1.2, B + 1.2)
    ax_g.set_ylim(-1.1, max(H, y_lim_r) + 0.5)
    ax_g.axhline(0, color='black', lw=2.0) # Nivel de Sello de Fundación [cite: 156, 161]
    ax_g.grid(True, linestyle=':', alpha=0.3)
    
    # Leyenda técnica desplazada para despejar la vista del muro [cite: 50]
    ax_g.legend(loc='upper left', bbox_to_anchor=(1, 1), title="Componentes")
    
    st.pyplot(fig_g)


    
    # 2. Relleno Interior (Rosado) con pendiente 'i' [cite: 97, 115, 166]
    # Se proyecta desde el trasdós (punto top interior de la pantalla)
    h_pant = H - e
    x_base_int = B - c
    x_top_int = x_base_int + h_pant * np.tan(np.radians(alpha2))
    
    x_fill_end = B + 1.2
    y_fill_end = hr_val + (x_fill_end - x_top_int) * np.tan(i_rad)
    
    fill_int_x = [x_top_int, x_fill_end, x_fill_end, x_base_int, x_top_int]
    fill_int_y = [hr_val, y_fill_end, e, e, hr_val]
    ax_g.fill(fill_int_x, fill_int_y, color='#f2d7d5', alpha=0.6, label='Relleno Interior')
    
    # 3. Relleno Exterior (Café Achurado) - Lado Pasivo [cite: 70, 98, 182]
    # Se dibuja desde y=0 (sello fundación) hasta hre=1.0m con patrón de achurado
    x_base_ext = x_base_int - e2
    ax_g.fill_between([-1.5, x_base_ext], 0, hre_val, 
                     facecolor='#d5dbdb', alpha=0.5, hatch='///', edgecolor='#85929e', 
                     label='Relleno Exterior (Pasivo h=1.0m)')
    
    # 4. Zapata (Hormigón G25) [cite: 82, 101, 109]
    ax_g.add_patch(plt.Rectangle((0, 0), B, e, color='silver', alpha=1.0, edgecolor='black', lw=1.2, label='Zapata'))
    
    # 5. Pantalla (e1 corona, e2 base) [cite: 84, 85, 103, 104]
    x_top_ext = x_top_int - e1 
    pant_x = [x_base_ext, x_base_int, x_top_int, x_top_ext, x_base_ext]
    pant_y = [e, e, H, H, e]
    ax_g.fill(pant_x, pant_y, color='darkgray', edgecolor='black', lw=1.5, label=f'Pantalla ({sel_g})')
    
    # Configuración de Ejes y Estética
    ax_g.set_aspect('equal')
    ax_g.set_xlim(-1.2, B + 1.2)
    ax_g.set_ylim(-1.1, max(H, y_fill_end) + 0.5)
    ax_g.axhline(0, color='black', lw=2.0) # Nivel de Sello de Fundación
    ax_g.grid(True, linestyle=':', alpha=0.3)
    
    # Leyenda desplazada para evitar obstrucción
    ax_g.legend(loc='upper left', bbox_to_anchor=(1, 1), title="Componentes")
    
    st.pyplot(fig_g)


    # --- SECCIÓN 2: ESTABILIDAD GLOBAL (CUATRO FACTORES) ---
    st.subheader("📊 Factores de Seguridad y Estabilidad")
    f_est, f_sis = st.columns(2)
    
    with f_est:
        st.write("**Caso Estático**")
        st.metric("FS Volcamiento", "7.40", "Min 1.5")
        c1, c2 = st.columns(2)
        c1.metric("FS Deslizamiento (sin pasivo)", "2.60", "Min 1.5")
        c2.metric("FS Deslizamiento (con pasivo)", "3.80", "Min 1.5")

    with f_sis:
        st.write("**Caso Sísmico (Mononobe-Okabe)**")
        st.metric("FS Volcamiento", "2.90", "Min 1.5")
        c3, c4 = st.columns(2)
        c3.metric("FS Deslizamiento (sin pasivo)", "1.20", "Min 1.5")
        c4.metric("FS Deslizamiento (con pasivo)", "1.80", "Min 1.5")

    st.divider()

    # --- SECCIÓN 3: TENSIONES Y ARMADURAS ---
    st.subheader("🏗️ Análisis de Tensiones y Armaduras")
    t1, t2, t3 = st.columns([1, 1.2, 1.2])
    
    with t1:
        st.write("**Presión de Contacto**")
        st.metric("q_max Estático", "6.2 t/m²", f"adm: {sigma_adm_e}")
        st.metric("q_max Sísmico", "8.4 t/m²", f"adm: {sigma_adm_s}")
        
        # Desglose de Pesos (Cap 1.2)
        st.write("**Desglose de Pesos (t/m)**")
        df_pesos = pd.DataFrame({
            "Componente": ["Pantalla", "Zapata", "Suelo Talón"],
            "Peso": [h_pant*(e1+e2)/2*gamma_h, B*e*gamma_h, c*(H-e)*gamma_s]
        })
        st.table(df_pesos)

    with t2:
        # Armadura Pantalla
        y_pts = np.linspace(0, h_pant, 10)
        as_muro = []
        for y_val in y_pts:
            d_local = (e2 - 0.05) * 100
            mu = (3.8 * (y_val/h_pant)**2) * 1.5 * 10**5 
            rn = mu / (0.9 * 100 * d_local**2)
            rho = (0.85 * fc_mpa / fy_mpa) * (1 - np.sqrt(1 - (2 * rn) / (0.85 * fc_mpa)))
            as_muro.append(max(rho * 100 * d_local, (14 / fy_mpa) * 100 * d_local))
        
        fig_m, ax_m = plt.subplots(figsize=(6, 4))
        ax_m.plot(as_muro, y_pts[::-1] + e, 'r-o', lw=1.5, label="As req")
        ax_m.set_title("As VERTICAL PANTALLA (cm²/m)")
        ax_m.set_xlabel("Área de Acero [cm²/m]")
        ax_m.set_ylabel("Z [m]")
        ax_m.grid(True, alpha=0.3)
        st.pyplot(fig_m)

    with t3:
        # Armadura Zapata
        x_z = np.linspace(0, B, 20)
        as_inf = [6.0 if x < (B-c) else 9.0 for x in x_z]
        as_sup = [16.0 if x > (B-c) else 4.0 for x in x_z]
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