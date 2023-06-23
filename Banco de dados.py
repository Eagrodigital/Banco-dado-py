import sqlite3
import tkinter as tk
import tkinter as ttk
import qrcode
import pandas as pd
import os
from PIL import Image, ImageTk

# Verificar se o diretório "qrcodes" existe, caso contrário, criá-lo
if not os.path.exists("qrcodes"):
    os.makedirs("qrcodes")

# Criando a conexão com o banco de dados
conn = sqlite3.connect('animais.db')
c = conn.cursor()

# Criando a tabela de animais
c.execute('''CREATE TABLE IF NOT EXISTS animais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                especie TEXT,
                idade INTEGER,
                qr_code TEXT
            )''')
conn.commit()

# Função para cadastrar ou atualizar as informações de um animal
def cadastrar_atualizar_animal():
    nome = entry_nome.get()
    especie = entry_especie.get()
    idade = entry_idade.get()
    
    # Verificar se o animal já está cadastrado
    c.execute("SELECT id FROM animais WHERE nome=?", (nome,))
    result = c.fetchone()
    
    if result:
        # Atualizar as informações do animal
        animal_id = result[0]
        c.execute("UPDATE animais SET especie=?, idade=? WHERE id=?", (especie, idade, animal_id))
        conn.commit()
        
        # Exibir mensagem de atualização
        status_label.config(text=f"As informações do animal {nome} foram atualizadas.")
    else:
        # Inserir os dados do animal no banco de dados
        c.execute("INSERT INTO animais (nome, especie, idade) VALUES (?, ?, ?)", (nome, especie, idade))
        conn.commit()
        
        # Gerar o QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f"Nome: {nome}\nEspécie: {especie}\nIdade: {idade}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill='black', back_color='white')
        qr_img = qr_img.resize((200, 200))  # Redimensionar o QR code
        qr_img.save(f"qrcodes/{nome}.png")
        
        # Atualizar o QR code no banco de dados
        c.execute("UPDATE animais SET qr_code = ? WHERE nome = ?", (f"qrcodes/{nome}.png", nome))
        conn.commit()
        
        # Exibir mensagem de cadastro
        status_label.config(text=f"O animal {nome} foi cadastrado com sucesso.")
    
    # Limpar os campos do formulário
    entry_nome.delete(0, tk.END)
    entry_especie.delete(0, tk.END)
    entry_idade.delete(0, tk.END)

# Função para exibir os animais cadastrados em uma nova janela
def exibir_animais_cadastrados():
    # Consultar os animais cadastrados
    c.execute("SELECT nome, especie, idade, qr_code FROM animais")
    animais = c.fetchall()
    
    # Criar uma janela para exibir os animais cadastrados
    window = tk.Toplevel()
    window.title("Animais Cadastrados")
    
    # Criar o Listbox para exibir os animais
    listbox = tk.Listbox(window, width=60)
    listbox.pack()
    
    # Adicionar os animais ao Listbox
    for animal in animais:
        nome, especie, idade, qr_code = animal
        info = f"Nome: {nome}, Espécie: {especie}, Idade: {idade}, QR Code: {qr_code}"
        listbox.insert(tk.END, info)
    
    # Definir a opção de scroll no Listbox
    scrollbar = tk.Scrollbar(window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)


# Função para atualizar as informações de um animal selecionado
def atualizar_animal(animal_id):
    # Consultar as informações atuais do animal
    c.execute("SELECT nome, especie, idade FROM animais WHERE id=?", (animal_id,))
    result = c.fetchone()
    
    if result:
        nome, especie, idade = result
        
        # Criar uma nova janela para atualização das informações
        window = tk.Toplevel(root)
        window.title("Atualizar Animal")
        
        # Campos de entrada para atualização
        label_nome = tk.Label(window, text="Nome:")
        label_nome.grid(row=0, column=0, padx=5, pady=5)
        entry_nome = tk.Entry(window)
        entry_nome.insert(tk.END, nome)
        entry_nome.grid(row=0, column=1, padx=5, pady=5)
        
        label_especie = tk.Label(window, text="Espécie:")
        label_especie.grid(row=1, column=0, padx=5, pady=5)
        entry_especie = tk.Entry(window)
        entry_especie.insert(tk.END, especie)
        entry_especie.grid(row=1, column=1, padx=5, pady=5)
        
        label_idade = tk.Label(window, text="Idade:")
        label_idade.grid(row=2, column=0, padx=5, pady=5)
        entry_idade = tk.Entry(window)
        entry_idade.insert(tk.END, idade)
        entry_idade.grid(row=2, column=1, padx=5, pady=5)
        
        button_atualizar = tk.Button(window, text="Atualizar",
                                    command=lambda: atualizar_animal_banco(animal_id, entry_nome.get(), entry_especie.get(), entry_idade.get(), window))
        button_atualizar.grid(row=3, columnspan=2, padx=5, pady=5)

# Função para atualizar as informações do animal no banco de dados
def atualizar_animal_banco(animal_id, nome, especie, idade, window):
    c.execute("UPDATE animais SET nome=?, especie=?, idade=? WHERE id=?", (nome, especie, idade, animal_id))
    conn.commit()
    
    window.destroy()  # Fechar a janela de atualização
    exibir_animais_cadastrados()  # Atualizar a exibição dos animais cadastrados

# Função para criar a planilha no formato Excel
def criar_planilha_atualizar_qrcode():
    # Consultar os animais cadastrados
    c.execute("SELECT nome, especie, idade, qr_code FROM animais")
    animais = c.fetchall()
    
    # Criar o DataFrame
    df = pd.DataFrame(animais, columns=['Nome', 'Espécie', 'Idade', 'QR Code'])
    
    # Salvar a planilha no formato Excel
    df.to_excel('animais.xlsx', index=False)
    
    # Exibir mensagem de sucesso
    status_label.config(text="A planilha 'animais.xlsx' foi criada com sucesso.")

# Interface gráfica utilizando Tkinter
root = tk.Tk()
root.title("Cadastro de Animais")
root.geometry("300x300")

label_nome = tk.Label(root, text="Nome:")
label_nome.pack()
entry_nome = tk.Entry(root)
entry_nome.pack()

label_especie = tk.Label(root, text="Espécie:")
label_especie.pack()
entry_especie = tk.Entry(root)
entry_especie.pack()

label_idade = tk.Label(root, text="Idade:")
label_idade.pack()
entry_idade = tk.Entry(root)
entry_idade.pack()

button_cadastrar_atualizar = tk.Button(root, text="Cadastrar/Atualizar", command=cadastrar_atualizar_animal)
button_cadastrar_atualizar.pack()

button_exibir_animais = tk.Button(root, text="Exibir Animais Cadastrados", command=exibir_animais_cadastrados)
button_exibir_animais.pack()

button_planilha_qrcode = tk.Button(root, text="Criar Planilha e QR Codes", command=criar_planilha_atualizar_qrcode)
button_planilha_qrcode.pack()

status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()