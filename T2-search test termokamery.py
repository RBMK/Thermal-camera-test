import cv2
import tkinter as tk
import ttkbootstrap as tb  # Moderní vzhled
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import numpy as np
from datetime import datetime

def save_snapshot():
    # Vytvoří název: 07.06.26_220400.jpg
    timestamp = datetime.now().strftime("%d.%m.%y_%H%M%S")
    filename = f"{timestamp}.jpg"
    cv2.imwrite(filename, frame_rgb)
    status_label.config(text=f"Uloženo: {filename}")
    root.after(2000, lambda: status_label.config(text="Připraveno"))

def draw_thermal_markers_from_image(frame_colored, gray_resized):

    gray_gray = cv2.cvtColor(gray_resized, cv2.COLOR_BGR2GRAY)

    # 2. Hledáme extrémy v šedé
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(gray_gray)
    
    hottest_pos = minLoc
    coldest_pos = maxLoc
    
    # 3. Barvy a vykreslení...
    color_at_hot = frame_colored[hottest_pos[1], hottest_pos[0]]
    inv_color = (int(255 - color_at_hot[0]), int(255 - color_at_hot[1]), int(255 - color_at_hot[2]))
    color_at_cold = frame_colored[coldest_pos[1], coldest_pos[0]]
    inv_color_c = (int(255 - color_at_cold[0]), int(255 - color_at_cold[1]), int(255 - color_at_cold[2]))
    
    cv2.drawMarker(frame_colored, hottest_pos, inv_color, cv2.MARKER_CROSS, 20, 1)
    cv2.circle(frame_colored, coldest_pos, 10, inv_color_c, 1)
    
    return frame_colored

# Nastavení kamery
cap = cv2.VideoCapture(0)

def trigger_nuc():
    success = cap.set(27, 32768)
    status_label.config(text="Rekalibrace odeslána!" if success else "Chyba kalibrace")
    root.after(2000, lambda: status_label.config(text="Připraveno"))

# Inicializace aplikace s tmavým tématem 'superhero'
root = tb.Window(themename="superhero")
root.title("T2-Search Control Center")
root.geometry("1200x700")


# 1. Hlavní kontejner
main_container = tb.Frame(root)
main_container.pack(fill=BOTH, expand=True)

# 2. Levá strana pro video
video_frame = tb.Frame(main_container)
video_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
video_label = tb.Label(video_frame)
video_label.pack()

# Pravý panel - expand=False zajistí, že nebude brát víc místa než potřebuje, 
# pokud chcete, aby bral přesně to, co zbyde, použijte grid nebo upravte váhy
# Ale pro "roztáhnutí" stačí upravit váhu hlavního kontejneru:
main_container.columnconfigure(1, weight=10) # Pravý panel (index 1) se bude roztahovat

# 3. Pravá strana pro tabulku
right_panel = tb.Frame(main_container, width=300)
right_panel.pack(side=RIGHT, fill=BOTH, padx=5, pady=5)

status_label = tb.Label(right_panel, text="Připraveno", bootstyle="info")
status_label.pack(pady=5)

# Slovník map OpenCV
colormap_dict = {name: getattr(cv2, name) for name in dir(cv2) if name.startswith('COLORMAP_')}


# Combobox pro výběr
combo_label = tb.Label(right_panel, text="Vyberte paletu:")
combo_label.pack(pady=(10, 0))

colormap_combo = tb.Combobox(right_panel, values=list(colormap_dict.keys()), state="readonly")
colormap_combo.set("COLORMAP_RAINBOW") # Výchozí hodnota
colormap_combo.pack(fill=X, padx=20, pady=5)

# Checkbutton pro colormap
col_var = tk.BooleanVar(value=False)
col_check = tb.Checkbutton(right_panel, text="Černobílý základ", variable=col_var, bootstyle="round-toggle")
col_check.pack(pady=10)

# Checkbutton pro inverzi
invert_var = tk.BooleanVar(value=False)
invert_check = tb.Checkbutton(right_panel, text="Invertovat barvy", variable=invert_var, bootstyle="round-toggle")
invert_check.pack(pady=10)

# Checkbutton pro zaměřovač
zam_var = tk.BooleanVar(value=False)
zam_check = tb.Checkbutton(right_panel, text="Zaměřovač", variable=zam_var, bootstyle="round-toggle")
zam_check.pack(pady=10)

# Label pro zobrazení aktuální hodnoty
contrast_label = tb.Label(right_panel, text="Kontrast: 1.0")
contrast_label.pack(pady=(10, 0))

# Posuvník (Scale) - rozsah 0.2 až 5.0, výchozí 1.0
contrast_var = tk.DoubleVar(value=1.0)
contrast_scale = tb.Scale(right_panel, from_=0.2, to_=5.0, variable=contrast_var, 
                          command=lambda val: contrast_label.config(text=f"Kontrast: {float(val):.1f}"))
contrast_scale.pack(fill=X, padx=20, pady=5)

# Label pro zobrazení aktuální hodnoty
jas_label = tb.Label(right_panel, text="Jas: 0.0")
jas_label.pack(pady=(10, 0))

# Posuvník (Scale) - rozsah -600.0 až 300.0, výchozí 0.0
jas_var = tk.DoubleVar(value=0.0)
jas_scale = tb.Scale(right_panel, from_=-512.0, to_=256.0, variable=jas_var, 
                          command=lambda val: jas_label.config(text=f"Jas: {float(val):.1f}"))
jas_scale.pack(fill=X, padx=20, pady=5)

from tkinter import ttk
tree = ttk.Treeview(right_panel, columns=("Bod", "Teplota"), show='headings')
tree.heading("Bod", text="Bod")
tree.heading("Teplota", text="°C")
tree.column("Bod", width=80)
tree.pack(fill=BOTH, expand=True)

btn_nuc = tb.Button(right_panel, text="Uložit foto", 
                    command=save_snapshot)
btn_nuc.pack(side=LEFT, padx=20, expand=True, fill=X)

btn_nuc = tb.Button(right_panel, text="Spustit Rekalibraci (NUC)", 
                    command=trigger_nuc, bootstyle="danger-outline")
btn_nuc.pack(side=LEFT, padx=20, expand=True, fill=X)


def show_frame():
    global frame_rgb # Získáme přístup k aktuálnímu snímku
    ret, frame = cap.read()
    if ret:

        h, w = frame.shape[:2]
##        # 1. Získání surových bajtů z metadat
##        raw_footer_bytes = frame[h-5:h, :, :].tobytes()
        
        # 2. Převod bajtů na 16-bitová čísla (uint16)
        # Nyní pracujeme s polem, které má správnou délku
        #raw_footer = np.frombuffer(raw_footer_bytes, dtype=np.uint16)
        raw_footer = np.frombuffer(frame[h-5:h, :, :].tobytes(), dtype=np.uint16)

        # 1. Zpracování inverze
        # Pokud je zaškrtnuto, invertujeme snímek
        if not invert_var.get():
            frame = cv2.bitwise_not(frame)

        # 2. Úprava kontrastu a jasu
        # alpha = kontrast (1.0 = původní), beta = jas (0 = původní)
        alpha = contrast_var.get()
        beta = jas_var.get()*alpha 
        frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
        
        # 3. Očištění obrazu (přemazání černou barvou)
        frame[h-5:h, :, :] = 128
        
        # 3. Zvětšení čistého obrazu (3x Nearest)
        frame_resized = cv2.resize(frame, (w*3, (h-5)*3), interpolation=cv2.INTER_NEAREST)

        # Získání vybrané palety z comboboxu
        selected_map_name = colormap_combo.get()
        selected_map = colormap_dict.get(selected_map_name, cv2.COLORMAP_RAINBOW)

        # 4. Aplikace zvolené palety
        if col_var.get():
            frame_colored = frame_resized.copy()
        else:
            frame_colored = cv2.applyColorMap(frame_resized.copy(), selected_map)

        # Aplikace zaměřovačů
        frame_colored = draw_thermal_markers_from_image(frame_colored, frame_resized)

        # Otočíme barevnou osu (převrátíme pořadí barev v paletě)
        frame_colored = cv2.flip(frame_colored, 0)
        frame_colored = cv2.flip(frame_colored, 1)

        # 6. Vykreslení statického zaměřovače doprostřed
        if zam_var.get():
            
            # 6. Vykreslení statického zaměřovače doprostřed
            h_colored, w_colored = frame_colored.shape[:2]
            center_x, center_y = w_colored // 2, h_colored // 2
            
            # 1. Správné indexování [y, x]
            color_cen = frame_colored[center_y, center_x] 

            # 2. Bezpečný výpočet inverzní barvy (převod na int, aby nedošlo k přetečení)
            inv_b = int(255) - int(color_cen[0])
            inv_g = int(255) - int(color_cen[1])
            inv_r = int(255) - int(color_cen[2])
            inv_color = (inv_b, inv_g, inv_r)

            # 3. Aplikace
            # Vodorovná
            #cv2.line(frame_colored, (center_x - 16, center_y), (center_x + 16, center_y), (0, 0, 0), 4) 
            cv2.line(frame_colored, (center_x - 15, center_y), (center_x + 15, center_y), inv_color, 1)

            # Svislá
            #cv2.line(frame_colored, (center_x, center_y - 16), (center_x, center_y + 16), (0, 0, 0), 4) 
            cv2.line(frame_colored, (center_x, center_y - 15), (center_x, center_y + 15), inv_color, 1)

            # Středová tečka
            #cv2.circle(frame_colored, (center_x, center_y), 2, (0, 0, 0), -1) # Černý střed
            #cv2.circle(frame_colored, (center_x, center_y), 1, (255, 255, 255), -1) # Bílá tečka


        # 5. Zobrazení obrazu v Tkinter (převádíme už obarvený frame)
        frame_rgb = cv2.cvtColor(frame_colored, cv2.COLOR_BGR2RGB)
        
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)


        
   
        # Vyčištění tabulky
        for item in tree.get_children():
            tree.delete(item)

        REF_VAL = 55000

        tree.insert("", END, values=(f"počet: {len(raw_footer)}"))        

        prumerna_hodnota = np.mean(raw_footer[0:100])
        teplota_prumer = 20 + (REF_VAL - prumerna_hodnota) * 0.00025
        tree.insert("", END, values=(f"Průměr_T: {teplota_prumer:.1f}°C\n"))
        
        # Vybereme jen prvních 10 bodů, které se nejvíce mění (viz vaše měření)
        #for i in range(0, len(raw_footer)):
        for i in range(0, 100):
            
            # Místo původního výpočtu zkuste tento:
            # Předpokládáme, že "v klidu" je hodnota kolem 55 000 (pokojová teplota cca 20-25 °C)
            # S rukou hodnota klesne k cca 1000.

            # 1. Definujeme referenční bod (pokojová teplota)
             
            VAL = int(raw_footer[i])
            # 2. Inverzní výpočet:
            # Čím více se VAL liší od REF_VAL směrem dolů, tím je objekt teplejší
            teplota_celsius = 20 + (REF_VAL - VAL) * 0.00025
            # Zobrazíme jen pokud je hodnota v určitém rozsahu, který vás zajímá
            if -25 < teplota_celsius < 1000:
                
                # Koeficient 0.002 musíte doladit experimentálně (třeba i 0.005)            
                # Koeficient 0.04 je jen odhad, možná bude potřeba upravit offset

                tree.insert("", END, values=(i, f"{teplota_celsius:.1f}°C\n"))
       
    root.after(15, show_frame)
show_frame()
root.mainloop()

# Úklid při zavření
cap.release()
