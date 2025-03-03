import tkinter as tk
from tkinter import ttk
import pyautogui
import threading
import time
import random
import keyboard  # Agora importando o teclado corretamente

# Lista de coordenadas
coordinates = []
loop_running = False
pending_points = []

# Função para capturar a posição do mouse e adicionar à lista
def capture_position(name):
    x, y = pyautogui.position()
    if len(pending_points) == 1:  # Segundo ponto de uma linha ou área
        x1, y1 = pending_points.pop()
        if name == "Linha":
            coordinates.append({"name": name, "type": "line", "points": [(x1, y1), (x, y)], "delay": 1, "hold_time": 0, "spacing": 10})
        elif name == "Area":
            coordinates.append({"name": name, "type": "area", "points": [(x1, y1), (x, y)], "delay": 1, "hold_time": 0, "spacing": 10})
    else:
        if name == "Click":
            coordinates.append({"name": name, "type": "click", "x": x, "y": y, "delay": 1, "hold_time": 0, "spacing": None})
        else:
            pending_points.append((x, y))
    update_coordinate_list()

# Atualiza a lista de coordenadas na interface
def update_coordinate_list():
    for idx, coord in enumerate(coordinates):
        delay_entry = frame_coordinates.grid_slaves(row=idx+1, column=2)
        hold_time_entry = frame_coordinates.grid_slaves(row=idx+1, column=3)
        spacing_entry = frame_coordinates.grid_slaves(row=idx+1, column=4)
        if delay_entry and hold_time_entry and spacing_entry:
            try:
                coord['delay'] = max(0, float(delay_entry[0].get()))
            except ValueError:
                coord['delay'] = 1
            try:
                coord['hold_time'] = max(0, float(hold_time_entry[0].get()))
            except ValueError:
                coord['hold_time'] = 0
            try:
                coord['spacing'] = max(0, float(spacing_entry[0].get())) if coord['type'] in ["line", "area"] else None
            except ValueError:
                coord['spacing'] = 10 if coord['type'] in ["line", "area"] else None

    for widget in frame_coordinates.winfo_children():
        widget.destroy()

    headers = ["Tipo", "Coordenadas", "Atraso", "Segurar Click", "Espaçamento", "Remover"]
    for col, header in enumerate(headers):
        lbl = tk.Label(frame_coordinates, text=header, font=("Arial", 10, "bold"))
        lbl.grid(row=0, column=col, padx=5, pady=5)

    for i, coord in enumerate(coordinates):
        lbl_name = tk.Label(frame_coordinates, text=coord['name'])
        lbl_name.grid(row=i+1, column=0, padx=5, pady=2, sticky="w")

        if coord['type'] == "click":
            details = f"{coord['x']} x {coord['y']}"
        elif coord['type'] == "line":
            p1, p2 = coord['points']
            details = f"Linha: {p1} -> {p2}"
        elif coord['type'] == "area":
            p1, p2 = coord['points']
            details = f"Área: {p1} -> {p2}"

        lbl_details = tk.Label(frame_coordinates, text=details)
        lbl_details.grid(row=i+1, column=1, padx=5, pady=2, sticky="w")

        delay_entry = ttk.Entry(frame_coordinates, width=5)
        delay_entry.insert(0, str(coord['delay']))
        delay_entry.grid(row=i+1, column=2, padx=5)

        hold_time_entry = ttk.Entry(frame_coordinates, width=5)
        hold_time_entry.insert(0, str(coord['hold_time']))
        hold_time_entry.grid(row=i+1, column=3, padx=5)

        spacing_entry = ttk.Entry(frame_coordinates, width=5)
        if coord['spacing'] is not None:
            spacing_entry.insert(0, str(coord['spacing']))
        spacing_entry.grid(row=i+1, column=4, padx=5)

        btn_remove = ttk.Button(frame_coordinates, text="x", command=lambda idx=i: remove_coordinate(idx))
        btn_remove.grid(row=i+1, column=5, padx=5)

        # Update values on change
        delay_entry.bind("<FocusOut>", lambda e, idx=i: update_delay(idx, delay_entry.get()))
        hold_time_entry.bind("<FocusOut>", lambda e, idx=i: update_hold_time(idx, hold_time_entry.get()))
        spacing_entry.bind("<FocusOut>", lambda e, idx=i: update_spacing(idx, spacing_entry.get()))

# Funções de atualização
def update_delay(index, value):
    try:
        delay = max(0, float(value))
        coordinates[index]['delay'] = delay if delay > 0 else 0.01
    except ValueError:
        coordinates[index]['delay'] = 1

def update_hold_time(index, value):
    try:
        coordinates[index]['hold_time'] = max(0, float(value))
    except ValueError:
        coordinates[index]['hold_time'] = 0

def update_spacing(index, value):
    try:
        if coordinates[index]['type'] in ["line", "area"]:
            coordinates[index]['spacing'] = max(0, float(value))
    except ValueError:
        coordinates[index]['spacing'] = 10

# Remove coordenada
def remove_coordinate(index):
    del coordinates[index]
    update_coordinate_list()

# Loop principal de cliques
def clicker_loop():
    global loop_running
    while loop_running:
        for coord in coordinates:
            if not loop_running:
                break

            if coord['type'] == "click":
                pyautogui.moveTo(coord['x'], coord['y'])
                if coord['hold_time'] > 0:
                    pyautogui.mouseDown()
                    time.sleep(coord['hold_time'])
                    pyautogui.mouseUp()
                else:
                    pyautogui.click()

            elif coord['type'] == "line":
                p1, p2 = coord['points']
                x1, y1 = p1
                x2, y2 = p2
                steps = max(abs(x2 - x1), abs(y2 - y1))
                spacing = coord['spacing'] if coord['spacing'] else 10
                for step in range(steps + 1):
                    if not loop_running:
                        break
                    x = x1 + (x2 - x1) * step // steps
                    y = y1 + (y2 - y1) * step // steps
                    if step % spacing == 0:  # Pular o número de pixels especificado
                        pyautogui.moveTo(x, y)
                        pyautogui.click()

            elif coord['type'] == "area":
                p1, p2 = coord['points']
                x1, y1 = min(p1[0], p2[0]), min(p1[1], p2[1])
                x2, y2 = max(p1[0], p2[0]), max(p1[1], p2[1])
                x = random.randint(x1, x2)
                y = random.randint(y1, y2)
                pyautogui.moveTo(x, y)
                if coord['hold_time'] > 0:
                    pyautogui.mouseDown()
                    time.sleep(coord['hold_time'])
                    pyautogui.mouseUp()
                else:
                    pyautogui.click()

            if coord['delay'] > 0:
                time.sleep(coord['delay'])

# Inicia ou encerra o loop
def toggle_loop():
    global loop_running
    if loop_running:
        loop_running = False
        print("Loop interrompido.")
    else:
        loop_running = True
        threading.Thread(target=clicker_loop, daemon=True).start()
        print("Loop iniciado.")

# Ações dos atalhos
def set_click():
    capture_position("Click")

def set_line():
    capture_position("Linha")

def set_area():
    capture_position("Area")

# Atualiza as coordenadas do mouse em tempo real
def update_mouse_position():
    while True:
        x, y = pyautogui.position()
        color = "blue" if x >= 0 and y >= 0 else "red"
        lbl_mouse_position.config(text=f"Coordenadas atuais: {x}, {y}", fg=color)
        time.sleep(0.1)

# Configuração da interface
def setup_gui():
    global frame_coordinates, lbl_mouse_position
    root = tk.Tk()
    root.title("Mouse Automation")
    root.geometry("800x600")

    lbl_explanation = tk.Label(root, text="F5: Área | F6: Linha | F7: Clique | F8: Iniciar/Parar", font=("Arial", 12))
    lbl_explanation.pack(pady=10)

    lbl_mouse_position = tk.Label(root, text="Coordenadas atuais: 0, 0", font=("Arial", 10))
    lbl_mouse_position.pack(pady=10)

    frame_coordinates = tk.Frame(root)
    frame_coordinates.pack(pady=20)

    # Teclas de atalho
    keyboard.add_hotkey("F7", set_click)
    keyboard.add_hotkey("F6", set_line)
    keyboard.add_hotkey("F5", set_area)
    keyboard.add_hotkey("F8", toggle_loop)

    # Thread para atualizar as coordenadas
    threading.Thread(target=update_mouse_position, daemon=True).start()

    root.mainloop()

setup_gui()
