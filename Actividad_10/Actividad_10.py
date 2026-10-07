import tkinter as tk
from tkinter import ttk, messagebox
import re
from itertools import product

# ==========================================
# MOTOR FORMAL - MÓDULO A: COMPILADOR DSL
# ==========================================

# Definición Léxica mediante RegEx (Tokens)
TOKEN_REGEX = [
    ('ACCION_DISP', r'\bAGREGAR\b'),
    ('ACCION_CORTE', r'\b(PICAR|CORTAR)\b'),
    ('ACCION_HOMO', r'\bMEZCLAR\b'),
    ('ACCION_TERM', r'\b(CALENTAR|HORNEAR)\b'),
    ('ACCION_FIN', r'\bSERVIR\b'),
    ('NUM', r'\d+(\.\d+)?'),
        # POR ESTO:
    ('UNIDAD', r'\b(gr|ml|piezas|tazas|cucharadas|minutos)\b|°C|°'),

    ('CONJ', r'\bde\b'),
    ('ID', r'[a-zA-ZáéíóúÁÉÍÓÚñÑ]+'),
    ('WS', r'\s+'),
]

def lexer(linea):
    tokens = []
    pos = 0
    while pos < len(linea):
        match = None
        for token_type, regex in TOKEN_REGEX:
            match = re.match(regex, linea[pos:])
            if match:
                text = match.group(0)
                if token_type != 'WS':  # Ignorar espacios en blanco
                    tokens.append((token_type, text))
                pos += len(text)
                break
        if not match:
            return None, f"Error Léxico: Carácter ilegal '{linea[pos]}'"
    return tokens, None

def mapear_accion_hardware(tipo_token):
    mapeo = {
        'ACCION_DISP': 'sys_dispense',
        'ACCION_CORTE': 'sys_blade_cut',
        'ACCION_HOMO': 'sys_mix_spin',
        'ACCION_TERM': 'sys_thermal_heat',
        'ACCION_FIN': 'sys_serve_output'
    }
    return mapeo.get(tipo_token, 'sys_unknown')

def compilar_receta(texto_receta):
    lineas = texto_receta.strip().split('\n')
    codigo_objeto = []
    errores = []
    
    for idx, linea in enumerate(lineas):
        num_linea = idx + 1
        linea_limpia = linea.strip()
        if not linea_limpia:
            continue
            
        tokens, err_lex = lexer(linea_limpia)
        if err_lex:
            errores.append(f"Línea {num_linea}: {err_lex}")
            continue
            
        # --- Análisis Sintáctico y Generación de Código ---
        # Caso 1: Instrucción Estándar (Acción + Cantidad + Unidad + de + Ingrediente)
        if len(tokens) >= 5 and tokens[0][0] in ['ACCION_DISP', 'ACCION_CORTE', 'ACCION_HOMO', 'ACCION_TERM']:
            if tokens[1][0] == 'NUM' and tokens[2][0] == 'UNIDAD' and tokens[3][0] == 'CONJ':
                ingrediente = " ".join([t[1] for t in tokens[4:]])
                subrutina = mapear_accion_hardware(tokens[0][0])
                
                codigo_objeto.append(f"; --- Línea {num_linea} ---")
                codigo_objeto.append(f"MOV R1, {tokens[1][1]}       ; Cargar cantidad ({tokens[2][1]})")
                codigo_objeto.append(f"MOV R2, '{ingrediente}' ; Cargar parámetro semántico")
                codigo_objeto.append(f"CALL {subrutina}")
            else:
                errores.append(f"Línea {num_linea}: Error Sintáctico. Estructura esperada: ACCIÓN [cantidad] [unidad] de [ingrediente]")
        
        # Caso 2: Instrucción de Término Exclusiva (SERVIR)
        elif len(tokens) == 1 and tokens[0][0] == 'ACCION_FIN':
            subrutina = mapear_accion_hardware(tokens[0][0])
            codigo_objeto.append(f"; --- Línea {num_linea} ---")
            codigo_objeto.append(f"CALL {subrutina}")
            codigo_objeto.append("HALT")
            
        else:
            errores.append(f"Línea {num_linea}: Error Sintáctico. Sentencia no reconocida por la gramática formal.")
            
    return codigo_objeto, errores

# ==========================================
# MOTOR FORMAL - MÓDULO B: CONJUNTOS Y LENGUAJES
# ==========================================

def parsear_conjunto(texto):
    # Divide por comas y limpia espacios
    elementos = [e.strip() for e in texto.split(',') if e.strip()]
    return set(elementos)

def clasificar_elemento(elemento):
    # Números Naturales N
    if re.fullmatch(r'\d+', elemento):
        return 'N'
    # Números Enteros Z
    if re.fullmatch(r'-?\d+', elemento):
        return 'Z'
    # Números Racionales Q
    if re.fullmatch(r'-?\d+\.\d+', elemento) or re.fullmatch(r'-?\d+/\d+', elemento):
        return 'Q'
    # Símbolos No Numéricos
    return 'S'

def calcular_kleene(alfabeto, max_len=3):
    # Genera la cerradura de Kleene hasta longitud k=3
    cadenas = ['ε']
    for l in range(1, max_len + 1):
        for p in product(alfabeto, repeat=l):
            cadenas.append("".join(p))
    return cadenas

# ==========================================
# INTERFAZ GRÁFICA DE USUARIO (GUI)
# ==========================================

class AppComputacionFormal(tk.Tk):  # <--- CORREGIDO: Sin espacio
    def __init__(self):
        super().__init__()
        self.title("Plataforma de Teoría Matemática de la Computación")
        self.geometry("850x650")
        
        # Panel de Pestañas
        tab_control = ttk.Notebook(self)
        
        self.tab_a = ttk.Frame(tab_control)
        self.tab_b = ttk.Frame(tab_control)
        
        tab_control.add(self.tab_a, text='Módulo A: Compilador DSL')
        tab_control.add(self.tab_b, text='Módulo B: Conjuntos y Lenguajes')
        tab_control.pack(expand=1, fill="both")
        
        self.inicializar_tab_a()
        self.inicializar_tab_b()
        
    def inicializar_tab_a(self):
        lbl = tk.Label(self.tab_a, text="Compilador de Recetario Técnico (DSL)", font=("Helvetica", 14, "bold"))
        lbl.pack(pady=10)
        
        # Layout con Paneles Divididos
        paneles = tk.Frame(self.tab_a)
        paneles.pack(expand=True, fill="both", padx=10, pady=5)
        
        # Entrada de Texto
        frame_izq = tk.Frame(paneles)
        frame_izq.pack(side="left", expand=True, fill="both", padx=5)
        tk.Label(frame_izq, text="Código Fuente (Receta):").pack(anchor="w")
        self.txt_fuente = tk.Text(frame_izq, width=40, height=20, font=("Courier", 11))
        self.txt_fuente.pack(expand=True, fill="both")
        
        # Receta por defecto para la demostración reglamentaria
        receta_demo = (
            "AGREGAR 500 gr de harina\n"
            "CORTAR 2 piezas de cebolla\n"
            "MEZCLAR 5 minutos de ingredientes\n"
            "CALENTAR 180 °C de horno\n"
            "SERVIR"
        )
        self.txt_fuente.insert("1.0", receta_demo)
        
        # Salida del Ensamblador / Errores
        frame_der = tk.Frame(paneles)
        frame_der.pack(side="right", expand=True, fill="both", padx=5)
        tk.Label(frame_der, text="Código Objeto (Ensamblador) / Diagnósticos:").pack(anchor="w")
        self.txt_salida = tk.Text(frame_der, width=40, height=20, font=("Courier", 11), bg="#f0f0f0")
        self.txt_salida.pack(expand=True, fill="both")
        
        btn_compilar = tk.Button(self.tab_a, text="Compilar Receta", command=self.ejecutar_compilacion, bg="#4CAF50", fg="white", font=("Helvetica", 11, "bold"))
        btn_compilar.pack(pady=10)
        
    def ejecutar_compilacion(self):
        self.txt_salida.delete("1.0", tk.END)
        fuente = self.txt_fuente.get("1.0", tk.END)
        
        codigo, errores = compilar_receta(fuente)
        
        if errores:
            self.txt_salida.insert(tk.END, "=== DIAGNÓSTICO DE ERRORES SINTÁCTICOS ===\n\n")
            for err in errores:
                self.txt_salida.insert(tk.END, f"{err}\n")
        else:
            self.txt_salida.insert(tk.END, "=== COMPILACIÓN EXITOSA ===\n\n")
            for linea in codigo:
                self.txt_salida.insert(tk.END, f"{linea}\n")

    def inicializar_tab_b(self):
        # Contenedor con Scroll
        canvas = tk.Canvas(self.tab_b)
        scrollbar = ttk.Scrollbar(self.tab_b, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # --- SUBMÓDULO B1: ÁLGEBRA DE CONJUNTOS ---
        lbl_b1 = tk.Label(scroll_frame, text="B.1. Álgebra de Conjuntos (Elementos separados por coma)", font=("Helvetica", 12, "bold"))
        lbl_b1.pack(anchor="w", pady=5)
        
        f_conj = tk.Frame(scroll_frame)
        f_conj.pack(fill="x", pady=5)
        
        tk.Label(f_conj, text="Conjunto A:").grid(row=0, column=0, sticky="w")
        self.ent_a = tk.Entry(f_conj, width=50)
        self.ent_a.grid(row=0, column=1, padx=5, pady=2)
        self.ent_a.insert(0, "1, 2, -3, 4.5, hola, de")
        
        tk.Label(f_conj, text="Conjunto B:").grid(row=1, column=0, sticky="w")
        self.ent_b = tk.Entry(f_conj, width=50)
        self.ent_b.grid(row=1, column=1, padx=5, pady=2)
        self.ent_b.insert(0, "1, 2, 8, de, adiós")
        
        # --- SUBMÓDULO B3: CLAUSURA DE KLEENE ---
        lbl_b3 = tk.Label(scroll_frame, text="B.3. Cerradura de Kleene Σ* (Alfabeto separado por comas)", font=("Helvetica", 12, "bold"))
        lbl_b3.pack(anchor="w", pady=15)
        
        f_kl = tk.Frame(scroll_frame)
        f_kl.pack(fill="x")
        tk.Label(f_kl, text="Alfabeto Σ:").grid(row=0, column=0, sticky="w")
        self.ent_sigma = tk.Entry(f_kl, width=30)
        self.ent_sigma.grid(row=0, column=1, padx=5)
        self.ent_sigma.insert(0, "a, b")
        
        # Botón de Procesamiento General
        btn_procesar = tk.Button(scroll_frame, text="Calcular Operaciones Formales", command=self.ejecutar_modulo_b, bg="#2196F3", fg="white", font=("Helvetica", 11, "bold"))
        btn_procesar.pack(pady=15)
        
        # Cuadro de Resultados Integrales
        tk.Label(scroll_frame, text="Resultados Computacionales del Módulo B:").pack(anchor="w")
        self.txt_resultados_b = tk.Text(scroll_frame, width=80, height=20, font=("Courier", 10), bg="#f9f9f9")
        self.txt_resultados_b.pack(fill="both", expand=True)

    def ejecutar_modulo_b(self):
        self.txt_resultados_b.delete("1.0", tk.END)
        
        # Obtener y parsear conjuntos
        set_a = parsear_conjunto(self.ent_a.get())
        set_b = parsear_conjunto(self.ent_b.get())
        sigma = [e.strip() for e in self.ent_sigma.get().split(',') if e.strip()]
        
        # Cálculos de Álgebra B.1
        card_a, card_b = len(set_a), len(set_b)
        union = set_a.union(set_b)
        inter = set_a.intersection(set_b)
        diff_ab = set_a.difference(set_b)
        diff_ba = set_b.difference(set_a)
        diff_sim = set_a.symmetric_difference(set_b)
        cont_ab = set_a.issubset(set_b)
        cont_ba = set_b.issubset(set_a)
        
        # Clasificación Numérica B.2 (Sobre Conjunto A)
        clases = {'N': [], 'Z': [], 'Q': [], 'S': []}
        for item in set_a:
            tipo = clasificar_elemento(item)
            clases[tipo].append(item)
            
        # Kleene B.3
        cadenas_kleene = calcular_kleene(sigma, max_len=3)
        
        # --- Renderizar Resultados en Pantalla ---
        res = []
        res.append("=====================================================================")
        res.append("         RESULTADOS MATEMÁTICOS DEL MÓDULO B")
        res.append("=====================================================================\n")
        
        res.append("--- B.1. Álgebra de Conjuntos ---")
        res.append(f" Cardinalidad: |A| = {card_a}, |B| = {card_b}")
        res.append(f" Unión (A ∪ B): {{{', '.join(union)}}}")
        res.append(f" Intersección (A ∩ B): {{{', '.join(inter)}}}")
        res.append(f" Diferencia (A \\ B): {{{', '.join(diff_ab)}}}")
        res.append(f" Diferencia (B \\ A): {{{', '.join(diff_ba)}}}")
        res.append(f" Diferencia Simétrica (A Δ B): {{{', '.join(diff_sim)}}}")
        res.append(f" Inclusión A ⊆ B: {cont_ab}")
        res.append(f" Inclusión B ⊆ A: {cont_ba}\n")
        
        res.append("--- B.2. Clasificación Numérica de Disyuntos (Sobre Conjunto A) ---")
        res.append(f" Naturales (N): {{{', '.join(clases['N'])}}}")
        res.append(f" Enteros (Z) sin N: {{{', '.join(clases['Z'])}}}")
        res.append(f" Racionales (Q) sin Z: {{{', '.join(clases['Q'])}}}")
        res.append(f" Símbolos No Numéricos (S): {{{', '.join(clases['S'])}}}")
        res.append("")
        
        res.append("--- B.3. Clausura Estricta de Kleene (Σ*) hasta |w| <= 3 ---")
        res.append(f" Cadenas generadas ({len(cadenas_kleene)} palabras):")
        res.append(f" {', '.join(cadenas_kleene)}\n")
        
        res.append(" Gramática Regular Derecha Equivalente G = (V_N, V_T, P, S):")
        res.append("  V_N = {S}, V_T = {" + ", ".join(sigma) + "}")
        res.append("  Reglas de Production P:")
        for t in sigma:
            res.append(f"   S -> {t}S | {t}")
        res.append("   S -> ε")
        
        self.txt_resultados_b.insert(tk.END, "\n".join(res))

if __name__ == "__main__":
    app = AppComputacionFormal()  # <--- CORREGIDO: Sin espacio
    app.mainloop()
