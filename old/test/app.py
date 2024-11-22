import tkinter as tk
from PIL import Image, ImageTk

def carregar_logo(caminho_logo, largura, altura):
    img = Image.open(caminho_logo)
    img = img.resize((int(largura), int(altura)), Image.LANCZOS)
    return ImageTk.PhotoImage(img)

def criar_retangulo_arredondado(canvas, x1, y1, x2, y2, r, **kwargs):
    canvas.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r, start=90, extent=90, **kwargs)  # Canto superior esquerdo
    canvas.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r, start=0, extent=90, **kwargs)  # Canto superior direito
    canvas.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2, start=180, extent=90, **kwargs)  # Canto inferior esquerdo
    canvas.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2, start=270, extent=90, **kwargs)  # Canto inferior direito
    canvas.create_rectangle(x1 + r, y1, x2 - r, y2, **kwargs)  # Parte central
    canvas.create_rectangle(x1, y1 + r, x2, y2 - r, **kwargs)  # Partes laterais

# Janela principal
root = tk.Tk()
root.title("NHPT+")
root.geometry("1920x1080")
root.resizable(False, False)

canvas = tk.Canvas(root, width=1920, height=1080, bg="#f4f8fc", highlightthickness=0)
canvas.pack()

# Header
canvas.create_rectangle(0, 0, 1920, 137.9, fill="#ffffff", outline="")

# Logo
logo_img = carregar_logo("C:/PBL_S4/app/static/logo.png", 297.4, 90)
canvas.create_image(108, 24, anchor="nw", image=logo_img)

# Botão
criar_retangulo_arredondado(canvas, 689.2, 44.6, 689.2 + 167, 44.6 + 48.8, 51, fill="#7ad3ff", outline="")

# Ícone no botão
icon_img = carregar_logo("C:/PBL_S4/app/static/logo.png", 25.4, 23.1)
canvas.create_image(714.9, 57.4, anchor="nw", image=icon_img)

# Texto no botão
canvas.create_text(749.6, 57.4, anchor="nw", text="Home", font=("Arial", 20), fill="black")

# Divisor
canvas.create_line(108, 137.9, 108 + 1704, 137.9, fill="#c4c4c4", width=2)

# Loop principal
root.mainloop()








import tkinter as tk
from PIL import Image, ImageTk

def carregar_logo(caminho_logo, largura, altura):
    img = Image.open(caminho_logo)
    img = img.resize((int(largura), int(altura)), Image.LANCZOS)
    return ImageTk.PhotoImage(img)

def criar_retangulo_arredondado(canvas, x1, y1, x2, y2, r, **kwargs):
    canvas.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r, start=90, extent=90, **kwargs)
    canvas.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r, start=0, extent=90, **kwargs)
    canvas.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2, start=180, extent=90, **kwargs)
    canvas.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2, start=270, extent=90, **kwargs)
    canvas.create_rectangle(x1 + r, y1, x2 - r, y2, **kwargs)
    canvas.create_rectangle(x1, y1 + r, x2, y2 - r, **kwargs)

# Janela principal
root = tk.Tk()
root.title("NHPT+")
root.geometry("1920x1080")
root.resizable(True, True)

# Captura as dimensões da tela do usuário
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Fatores de escala
scale_x = screen_width / 1920
scale_y = screen_height / 1080

# Canvas ajustado ao tamanho da tela
canvas = tk.Canvas(root, width=screen_width, height=screen_height, bg="#f4f8fc", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Header
header_height = 137.9 * scale_y
canvas.create_rectangle(0, 0, screen_width, header_height, fill="#ffffff", outline="")

# Logo redimensionada
logo_width = 297.4 * scale_x
logo_height = 90 * scale_y
logo_x = 108 * scale_x
logo_y = 24 * scale_y
logo_img = carregar_logo("C:/PBL_S4/app/static/logo.png", logo_width, logo_height)
canvas.create_image(logo_x, logo_y, anchor="nw", image=logo_img)

# Botão (but1)
but1_x = 689.2 * scale_x
but1_y = 44.6 * scale_y
but1_width = 167 * scale_x
but1_height = 48.8 * scale_y
but1_radius = 51 * scale_x
criar_retangulo_arredondado(
    canvas,
    but1_x,
    but1_y,
    but1_x + but1_width,
    but1_y + but1_height,
    but1_radius,
    fill="#7ad3ff",
    outline="",
)

# Ícone no botão
icon_width = 25.4 * scale_x
icon_height = 23.1 * scale_y
icon_x = 714.9 * scale_x
icon_y = 57.4 * scale_y
icon_img = carregar_logo("C:/PBL_S4/app/static/logo.png", icon_width, icon_height)
canvas.create_image(icon_x, icon_y, anchor="nw", image=icon_img)

# Texto no botão
text_x = 749.6 * scale_x
text_y = 57.4 * scale_y
canvas.create_text(
    text_x,
    text_y,
    anchor="nw",
    text="Home",
    font=("Arial", int(20 * scale_y)),  # Redimensiona o tamanho da fonte
    fill="black",
)

# Divisor
divisor_x = 108 * scale_x
divisor_y = 137.9 * scale_y
divisor_width = 1704 * scale_x
canvas.create_line(divisor_x, divisor_y, divisor_x + divisor_width, divisor_y, fill="#c4c4c4", width=int(2 * scale_y))

# Loop principal
root.mainloop()
