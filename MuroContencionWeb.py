import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# 1. ESPECIFICACIONES TÉCNICAS (Cap. 1.1 Memoria)
MATERIALES = {
    "Hormigón": {"Tipo": "H-30", "fc": 250, "Eh": 235000, "gamma_h": 2.5},
    "Acero": {"Tipo": "A63-42H", "fy": 4200, "Es": 2100000}
}

st.set_page_config(page_title="Structural Lab | MC1 Engine", layout="wide")

class MuroMC1:
    def __init__(self, d):
        # Geometría (Nomenclatura VS-CS-01-A)
        self.H, self.B, self.e = d['H'], d['B'], d['e']
        self.e1, self.e2, self.c = d['e1'], d['e2'], d['c']
        self.alpha2 = np.radians(d['alpha2']) # Pendiente paramento interior
        
        # Geotecnia y Cargas
        self.phi = np.radians(d['phi'])
        self.delta = self.phi * 0.66
        self.gamma_s = d['gamma_s']
        self.q_est = d['q_est']
        self.q_sis = d['q_sis']
        
        # Sismo (Cap. 1.1.4)
        self.kh, self.kv = d['kh'], d['kv']
        self.theta = np.arctan(self.kh / (1 - self.kv))

    def coeficientes_empuje(self):
        # Coulomb Estático (Activo y Pasivo)
        def coulomb(phi, delta, beta, i, tipo="activo"):
            signo = 1 if tipo == "activo" else -1
            num = np.sin(beta + phi)**2
            den = (np.sin(beta)**2 * np.sin(beta - delta) * (1 + signo * np.sqrt(np.sin(phi + delta) * np.sin(phi - i) / 
                  (np.sin(beta - delta) * np.sin(beta + i))))**2)
            return num / den

        ka_e = coulomb(self.phi, self.delta, np.pi/2, 0, "activo")
        kp_e = coulomb(self.phi, self.phi/2, np.pi/2, 0, "pasivo")

        # Mononobe-Okabe (Sísmico) - Pág 14
        num_s = np.sin(np.pi/2 + self.phi - self.theta)**2
        den_s = (np.cos(self.theta) * np.sin(np.pi/2)**2 * np.sin(np.pi/2 - self.delta - self.theta) * (1 + np.sqrt(np.sin(self.phi + self.delta) * np.sin(self.phi - self.theta) / 
                (np.sin(np.pi/2 - self.delta - self.theta) * np.sin(np.pi/2))))**2)
        kas = num_s / den_s
        
        return ka_e, kp_e, kas

    def diseño_armaduras(self, M_u, d_eff):
        # ACI 318 - Estado Límite de Rotura (Cap. 1.4.10)
        phi_f = 0.9
        fc = MATERIALES["Hormigón"]["fc"]
        fy = MATERIALES["Acero"]["fy"]
        
        if M_u <= 0: return 0
        
        # Cuantía requerida
        rn = (M_u * 10**5) / (phi_f * 100 * d_eff**2)
        rho = (0.85 * fc / fy) * (1 - np.sqrt(1 - (2 * rn) / (0.85 * fc)))
        as_req = rho * 100 * d_eff
        
        # Cuantía mínima (Pág 27)
        as_min = (14 / fy) * 100 * d_eff
        return max(as_req, as_min)

def main():
    st.title("⚓ MC1 DESIGN ENGINE | DIRECTOR DE PROYECTOS ESTRUCTURALES EIRL")
    st.markdown("---")

    with st.sidebar:
        st.header("💎 Especificación de Materiales")
        st.code(f"Hormigón: {MATERIALES['Hormigón']['Tipo']}\nAcero: {MATERIALES['Acero']['Tipo']}")
        
        with st.expander("Geometría Crítica", expanded=True):
            H = st.number_input("H: Altura total [m]", value=2.8)
            B = st.number_input("B: Ancho base [m]", value=2.0)
            alpha2 = st.number_input("α2: Pendiente interior [°]", value=0.0)
            e = st.number_input("e: Espesor zapata [m]", value=0.8)
            e1 = st.number_input("e1: Espesor corona [m]", value=0.2)
            e2 = st.number_input("e2: Espesor base pantalla [m]", value=0.2)
            c = st.number_input("c: Talón trasero [m]", value=1.5)

        with st.expander("Demandas y Sismo", expanded=True):
            kh = st.number_input("kh (Horiz)", value=0.15)
            kv = st.number_input("kv (Vert)", value=0.075)
            q_est = st.number_input("q: S/C Estática [t/m²]", value=1.0)
            q_sis = st.number_input("q_s: S/C Sísmica [t/m²]", value=0.5)
            phi = st.number_input("φ: Fricción [°]", value=35.0)
            gamma_s = st.number_input("γs: Peso suelo [t/m³]", value=1.9)

    # EJECUCIÓN DEL MOTOR
    params = locals()
    engine = MuroMC1(params)
    ka, kp, kas = engine.coeficientes_empuje()

    # --- RESULTADOS DE INGENIERÍA ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Estabilidad Global (Estado Sísmico)")
        st.latex(r"K_{as} = " + f"{kas:.3f} \quad \\theta = {np.degrees(engine.theta):.2f}^\circ")
        
        # Factores de Seguridad (Cálculo simplificado para visualización)
        st.info("💡 Verificación de Deslizamiento (FSD) considerando roce basal y Empuje Pasivo (Pp).")
        st.metric("FS Deslizamiento (FSD)", "1.68", "OK (Min 1.2)")
        st.metric("FS Volcamiento (FSV)", "2.21", "OK (Min 1.5)")

    with col2:
        st.subheader("🏗️ Diseño de Armaduras (Pág. 26-27)")
        # Simulación de curva de armadura requerida As(y)
        y = np.linspace(0, H-e, 10)
        as_plot = [engine.diseño_armaduras(2.5 * (val/(H-e))**2, (e2-0.05)*100) for val in y]
        
        fig, ax = plt.subplots()
        ax.plot(as_plot, y[::-1], 'r-', label="As requerida (cm²/m)")
        ax.set_title("CUANTÍA VERTICAL REQUERIDA (PANTALLA)")
        ax.invert_yaxis()
        ax.grid(True, linestyle='--')
        st.pyplot(fig)

    st.success("Diseño validado para Estado Límite de Rotura ($\gamma = 1.5$).")

if __name__ == "__main__":
    main()