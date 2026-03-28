import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
import os

# 1. CONFIGURACIÓN PROFESIONAL DE PÁGINA
st.set_page_config(
    page_title="Structural Lab | Muro de Contención",
    page_icon="🧱",
    layout="wide"
)

# 2. FUNCIONES DE CÁLCULO (VS-CS-01-A)
def get_ka(phi, delta, beta, i):
    phi_r, delta_r, beta_r, i_r = np.radians([phi, delta, beta, i])
    num = np.sin(beta_r + phi_r)**2
    den = np.sin(beta_r)**2 * np.sin(beta_r - delta_r)
    term_sqrt = 1 + np.sqrt((np.sin(phi_r + delta_r) * np.sin(phi_r - i_r)) / 
                            (np.sin(beta_r - delta_r) * np.sin(beta_r + i_r)))
    return num / (den * term_sqrt**2)

def main():
    st.title("🧱 VERIFICACIÓN ESTRUCTURAL DE MUROS DE CONTENCIÓN")
    st.markdown("---")

    # --- SIDEBAR: INPUTS Y REFERENCIA ---
    with st.sidebar:
        st.header("📸 Referencia Geométrica")
        if os.path.exists("F1.jpg"):
            st.image("F1.jpg", caption="Esquema de variables (Figura 4.2)")
        else:
            st.warning("⚠️ F1.jpg no encontrada en el repositorio.")

        st.header("📏 Geometría del Muro")
        h_total = st.number_input("Altura H [m]", value=3.5, step=0.1)
        b_zapata = st.number_input("Ancho Zapata B [m]", value=2.2, step=0.1)
        e_zap = st.number_input("Espesor Zapata [m]", value=0.5, step=0.1)
        e_inf = st.number_input("Espesor Pantalla Inf. [m]", value=0.3, step=0.05)
        e_sup = st.number_input("Espesor Pantalla Sup. [m]", value=0.2, step=0.05)
        t_talon = st.number_input("Talón Trasero [m]", value=1.3, step=0.1)

        st.header("🌱 Suelo y Sismo")
        gamma_s = st.number_input("Peso Suelo [ton/m³]", value=1.9)
        phi = st.number_input("Ángulo Fricción [°]", value=32.0)
        kh = st.number_input("Coef. Sísmico kh", value=0.15)
        q_adm = st.number_input("Capacidad Adm. [ton/m²]", value=20.0)

    # --- PANEL CENTRAL: CÁLCULOS Y GRÁFICOS ---
    col1, col2 = st.columns([1, 1.2])

    # Lógica Interna de Ingeniería
    gamma_c = 2.5
    h_pantalla = h_total - e_zap
    
    # Pesos
    w_pantalla = ((e_sup + e_inf)/2) * h_pantalla * gamma_c
    w_zapata = b_zapata * e_zap * gamma_c
    w_suelo = t_talon * h_pantalla * gamma_s
    w_total = w_pantalla + w_zapata + w_suelo
    
    # Empujes (Coulomb)
    ka = get_ka(phi, phi*0.66, 90, 0)
    pa_h = 0.5 * gamma_s * h_total**2 * ka
    
    # Verificaciones
    momento_res = (w_total * (b_zapata/2)) # Simplificado para el demo
    momento_vol = (pa_h * (h_total/3))
    fsv = momento_res / momento_vol
    q_max = (w_total / b_zapata) * (1 + (6 * 0.1 / b_zapata))

    with col1:
        st.header("📋 Resultados de Estabilidad")
        
        # Formato de métricas
        m1, m2 = st.columns(2)
        m1.metric("FSV (Volcamiento)", f"{fsv:.2f}")
        m2.metric("q_máx (Tensión)", f"{q_max:.1f} t/m²")

        st.markdown("---")
        
        # Validaciones Normativas
        if fsv >= 1.5:
            st.success("✅ Estabilidad al Volcamiento: CUMPLE")
        else:
            st.error("❌ Estabilidad al Volcamiento: FALLA")

        if q_max <= q_adm:
            st.success("✅ Tensión en la Base: CUMPLE")
        else:
            st.error("❌ Tensión en la Base: EXCEDE CAPACIDAD")

    with col2:
        st.header("📐 Esquema Dinámico")
        
        fig, ax = plt.subplots(figsize=(6, 8))
        # Dibujo Zapata
        ax.add_patch(plt.Rectangle((0, 0), b_zapata, e_zap, color='gray', alpha=0.7))
        # Dibujo Pantalla
        px = [b_zapata - t_talon - e_inf, b_zapata - t_talon, b_zapata - t_talon, b_zapata - t_talon - e_sup]
        py = [e_zap, e_zap, h_total, h_total]
        ax.fill(px, py, color='darkgray', label='Hormigón')
        
        # Suelo
        ax.fill_between([b_zapata - t_talon, b_zapata], [e_zap, e_zap], [h_total, h_total], color='brown', alpha=0.2)
        
        # Configuración ejes
        ax.set_aspect('equal')
        ax.set_xlim(-0.5, b_zapata + 1)
        ax.set_ylim(-1, h_total + 1)
        ax.axhline(0, color='black', lw=2)
        ax.grid(True, linestyle=':', alpha=0.6)
        
        st.pyplot(fig)

if __name__ == "__main__":
    main()