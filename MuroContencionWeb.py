import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

# 1. CONFIGURACIÓN DE ENTORNO ESTRUCTURAL LAB
st.set_page_config(page_title="Structural Lab | MC1 Design Engine", layout="wide")

class MuroMC1:
    """Motor de cálculo basado en Memoria VS-CS-01-A"""
    def __init__(self, params):
        self.H = params['H']      # Altura total [cite: 80, 99]
        self.B = params['B']      # Ancho base [cite: 81, 100]
        self.e = params['e']      # Espesor zapata [cite: 82, 101]
        self.c = params['c']      # Talón trasero [cite: 83, 102]
        self.e1 = params['e1']    # Espesor coronamiento [cite: 84, 103]
        self.e2 = params['e2']    # Espesor base pantalla [cite: 85, 104]
        self.alpha1 = np.radians(params['alpha1']) # Inclinación trasdós [cite: 86, 105]
        
        # Materiales [cite: 17-24]
        self.fy = 4200 # [kgf/cm2] -> A63-42H [cite: 89]
        self.fc = 250  # [kgf/cm2] -> H-30/G25 [cite: 90]
        self.gamma_c = 2.5 # [tonf/m3] [cite: 87]
        self.rec = 0.05 # Recubrimiento [m] [cite: 91]
        
        # Suelo y Sismo [cite: 121-135]
        self.gs = params['gs']
        self.phi = np.radians(params['phi'])
        self.delta = self.phi * (2/3) # [cite: 95]
        self.kh = params['kh']
        self.kv = params['kv']
        self.q_adm = params['q_adm']

    def get_mononobe_okabe(self):
        """Cálculo de Kas e incremento sísmico (Memoria pág. 14)"""
        theta = np.arctan(self.kh / (1 - self.kv)) # 
        i = 0 # Inclinación relleno [cite: 97]
        beta = np.pi/2 # Muro vertical
        
        num = np.sin(beta + self.phi - theta)**2
        den = (np.cos(theta) * np.sin(beta)**2 * np.sin(beta - self.delta - theta) * (1 + np.sqrt(np.sin(self.phi + self.delta)*np.sin(self.phi - i - theta)/
                          (np.sin(beta - self.delta - theta)*np.sin(beta + i))))**2)
        kas = num / den # 
        
        pas_total = 0.5 * self.gs * self.H**2 * (1 - self.kv) * kas # [cite: 385]
        return kas, pas_total, theta

    def calcular_flexion_muro(self):
        """Divide el muro en 10 puntos para diagramas M(y) (Memoria pág. 18)"""
        y_points = np.linspace(0, self.H - self.e, 11) # De arriba hacia abajo
        moments = []
        armaduras = []
        
        # Factor de mayoración gamma_may = 1.5 [cite: 759]
        gamma_may = 1.5
        
        for y in y_points:
            h_eff = (self.H - self.e) - y
            # Simplificación de empuje para el diagrama basal
            ka_local = (np.tan(np.pi/4 - self.phi/2))**2
            m_est = (1/6) * self.gs * ka_local * h_eff**3
            
            # Cálculo de espesor variable em(y) [cite: 757]
            em_y = self.e1 + (h_eff * np.tan(self.alpha1))
            
            # Diseño de armadura [cite: 762]
            mu = m_est * gamma_may * 10**5 # ton-m to kg-cm
            d = (em_y - self.rec) * 100 # m to cm
            
            # Fórmula de rotura simplificada ACI [cite: 762]
            if mu > 0:
                rn = mu / (0.9 * 100 * d**2)
                rho = (0.85 * self.fc / self.fy) * (1 - np.sqrt(1 - (2 * rn / (0.85 * self.fc))))
                as_nec = rho * 100 * d
            else:
                as_nec = 0
            
            as_min = (14 / self.fy) * 100 * d # 
            as_def = max(as_nec, as_min)
            
            moments.append(m_est)
            armaduras.append(as_def)
            
        return y_points, moments, armaduras

def main():
    st.sidebar.image("F1.jpg") if os.path.exists("F1.jpg") else st.sidebar.info("Cargar F1.jpg")
    
    # --- INPUTS TÉCNICOS ---
    with st.sidebar:
        st.header("🛠 Parámetros Geométricos [CAP 1.1]")
        H = st.number_input("H: Altura total [m]", value=2.8, step=0.1) # [cite: 80]
        B = st.number_input("B: Ancho base [m]", value=2.0, step=0.1)  # [cite: 81]
        e = st.number_input("e: Espesor zapata [m]", value=0.8, step=0.1) # [cite: 82]
        c = st.number_input("c: Talón trasero [m]", value=1.5, step=0.1) # [cite: 83]
        e1 = st.number_input("e1: Espesor coronamiento [m]", value=0.2, step=0.05) # [cite: 84]
        e2 = st.number_input("e2: Espesor base pantalla [m]", value=0.2, step=0.05) # [cite: 85]
        
        st.header("⚡ Sismo y Suelo [CAP 1.1.4/6]")
        kh = st.number_input("kh: Coef. Horizontal", value=0.15) # [cite: 134]
        kv = st.number_input("kv: Coef. Vertical", value=0.075) # [cite: 135]
        phi = st.number_input("phi: Fricción suelo [°]", value=35.0) # [cite: 121]
        gs = st.number_input("gs: Peso unitario [ton/m³]", value=1.9) # [cite: 93]
        q_adm = st.number_input("q_adm: Capacidad adm [ton/m²]", value=20.0) # [cite: 122]

    muro = MuroMC1(locals())
    
    # --- CÁLCULOS ---
    kas, pas_total, theta = muro.get_mononobe_okabe()
    y_pts, moments, armaduras = muro.calcular_flexion_muro()

    # --- UI PRINCIPAL ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Verificaciones de Estabilidad [CAP 1.3/1.4]")
        
        # Verificaciones en LaTeX [cite: 290, 301, 317]
        st.latex(r"K_{as} = " + f"{kas:.3f}")
        st.latex(r"FSD = \frac{F_{res}}{F_{sol}} \geq 1.2") # [cite: 435]
        st.latex(r"FSV = \frac{M_{res}}{M_{vol}} \geq 1.5") # [cite: 446]
        
        # Gráfico 1: Flexión [cite: 547]
        fig_m, ax_m = plt.subplots()
        ax_m.plot(moments, y_pts, 'r-x', label="Mm(Y)")
        ax_m.set_xlabel("Momento [tonf-m/m]")
        ax_m.set_ylabel("Altura Y [m]")
        ax_m.set_title("FLEXIÓN A LO ALTO DEL MURO")
        ax_m.grid(True)
        st.pyplot(fig_m)

    with col2:
        st.subheader("🏗 Diseño de Armaduras [CAP 1.4.10]")
        
        # Gráfico 2: Armadura [cite: 769]
        fig_a, ax_a = plt.subplots()
        ax_a.plot(armaduras, y_pts, 'b-o', label="As Requerida")
        ax_a.set_xlabel("Área de Acero [cm²/m]")
        ax_a.set_ylabel("Altura Y [m]")
        ax_a.set_title("ARMADURA REQUERIDA MURO")
        ax_a.grid(True)
        st.pyplot(fig_a)
        
        # Tabla de puntos de control
        df = pd.DataFrame({
            "Altura [m]": y_pts[::-1],
            "Momento [t-m]": moments[::-1],
            "As [cm²/m]": armaduras[::-1]
        })
        st.dataframe(df.style.highlight_max(axis=0))

if __name__ == "__main__":
    main()