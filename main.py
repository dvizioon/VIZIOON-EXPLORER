import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import webbrowser
import subprocess
import shutil

# Função para logar eventos na tela de logs
def adicionar_log(mensagem):
    text_logs.insert(tk.END, mensagem + "\n")
    text_logs.yview(tk.END)  # Auto-scroll para a última linha
    
# Função para exibir o texto "Sobre"
def exibir_sobre():
    sobre_janela = tk.Toplevel()
    sobre_janela.title("Sobre")
    sobre_janela.geometry("400x200")
    sobre_janela.iconbitmap("explorador.ico")
    
    texto_sobre = """
Este projeto foi desenvolvido por Daniel Estevão Martins Mendes como parte de um aprendizado prático sobre o funcionamento de um explorador de arquivos simples em Python.

A aplicação permite navegar por diretórios, visualizar arquivos, abrir e executar programas, além de criar, editar e apagar arquivos e pastas.
    """
    label_sobre = tk.Label(sobre_janela, text=texto_sobre, wraplength=350, justify="left")
    label_sobre.pack(padx=10, pady=10)

# Função para listar pastas e arquivos, com suporte a pesquisa
def listar_pastas_arquivos(diretorio, pesquisa=None):
    caminho_atual.set(diretorio)  # Atualiza o campo de entrada com o caminho atual
    tree.delete(*tree.get_children())  # Limpa a lista de pastas e arquivos
    adicionar_log(f"Listando conteúdo de: {diretorio}")
    for item in os.listdir(diretorio):
        item_path = os.path.join(diretorio, item)
        if pesquisa:
            if pesquisa.lower() not in item.lower():
                continue
        if os.path.isdir(item_path):  # Mostra pastas
            tree.insert("", "end", text=item + " (Pasta)", values=[item_path])
        else:  # Mostra arquivos
            tree.insert("", "end", text=item + " (Arquivo)", values=[item_path])

# Função para entrar em pastas ou abrir arquivos ao clicar duas vezes
def ao_clicar_duas_vezes(event):
    entrar_ou_editar()

# Função para abrir o menu de contexto ao clicar com o botão direito
def abrir_menu(event):
    selected_item = tree.focus()  # Verifica qual item foi selecionado
    caminho = tree.item(selected_item, "values")[0]

    # Limpa o menu para recarregar opções
    menu_contexto.delete(0, "end")

    # Se for uma pasta, mostrar apenas a opção de apagar
    if os.path.isdir(caminho):
        menu_contexto.add_command(label="Apagar", command=apagar_item)
    
    # Se for um arquivo, mostrar as opções de abrir, apagar e editar
    else:
        # Opção de abrir no navegador (para .html, .css, .js)
        if caminho.endswith(".html") or caminho.endswith(".css") or caminho.endswith(".js"):
            menu_contexto.add_command(label="Abrir no Navegador", command=lambda: abrir_no_navegador(caminho))

        # Opção de abrir normalmente (outros tipos de arquivos)
        menu_contexto.add_command(label="Abrir", command=lambda: abrir_arquivo(caminho))

        # Adiciona a opção de editar (para arquivos de texto ou código)
        menu_contexto.add_command(label="Editar", command=lambda: editar_arquivo(caminho))

        # Adiciona sempre a opção de deletar
        menu_contexto.add_command(label="Apagar", command=apagar_item)

    # Exibir menu de contexto
    menu_contexto.post(event.x_root, event.y_root)


# Função para abrir arquivos normalmente (executa o programa associado)
def abrir_arquivo(caminho):
    try:
        adicionar_log(f"Abrindo arquivo: {caminho}")
        os.startfile(caminho)  # Abre o arquivo com o programa associado no Windows
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível abrir o arquivo.\nErro: {str(e)}")
        adicionar_log(f"Erro ao abrir arquivo: {caminho}. Erro: {str(e)}")

# Função para abrir arquivos .html no navegador padrão
def abrir_no_navegador(caminho):
    try:
        adicionar_log(f"Abrindo no navegador: {caminho}")
        webbrowser.open(f"file://{caminho}")
        messagebox.showinfo("Sucesso", f"Arquivo {os.path.basename(caminho)} aberto no navegador.")
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível abrir o arquivo no navegador.\nErro: {str(e)}")
        adicionar_log(f"Erro ao abrir arquivo no navegador: {caminho}. Erro: {str(e)}")

# Função para entrar em uma pasta ou abrir um arquivo
def entrar_ou_editar():
    selected_item = tree.focus()  # Verifica qual item foi selecionado
    if not selected_item:
        return
    caminho = tree.item(selected_item, "values")[0]
    if os.path.isdir(caminho):
        historico_pastas.append(caminho)  # Adiciona a pasta atual ao histórico
        listar_pastas_arquivos(caminho)  # Lista as pastas dentro da nova pasta
    else:
        editar_arquivo(caminho)  # Se for arquivo, abre para edição

# Função para editar um arquivo
def editar_arquivo(caminho_arquivo):
    editor = tk.Toplevel()
    editor.title(f"Editando: {caminho_arquivo}")
    
    text_area = tk.Text(editor, wrap="word")
    text_area.pack(expand=True, fill="both")
    
    # Carrega o conteúdo do arquivo
    with open(caminho_arquivo, "r",encoding='utf-8') as f:
        conteudo = f.read()
        text_area.insert("1.0", conteudo)

    # Função para salvar o conteúdo do arquivo
    def salvar():
        with open(caminho_arquivo, "w" , encoding='utf-8') as f:
            f.write(text_area.get("1.0", "end-1c"))
        messagebox.showinfo("Salvo", f"Arquivo {os.path.basename(caminho_arquivo)} salvo com sucesso.")
        adicionar_log(f"Arquivo salvo: {caminho_arquivo}")
    
    # Botão de salvar
    btn_salvar = tk.Button(editor, text="Salvar", command=salvar, bg="#4CAF50", fg="white")
    btn_salvar.pack(pady=5)

# Função para voltar para a pasta anterior
def voltar():
    if len(historico_pastas) > 1:  # Verifica se há histórico de pastas
        historico_pastas.pop()  # Remove a pasta atual do histórico
        listar_pastas_arquivos(historico_pastas[-1])  # Lista a pasta anterior

# Função para criar uma nova pasta
def criar_pasta():
    nome_pasta = simpledialog.askstring("Criar Pasta", "Nome da nova pasta:")
    if nome_pasta:
        caminho_nova_pasta = os.path.join(historico_pastas[-1], nome_pasta)
        if not os.path.exists(caminho_nova_pasta):
            os.mkdir(caminho_nova_pasta)
            listar_pastas_arquivos(historico_pastas[-1])  # Atualiza a lista de pastas
            adicionar_log(f"Pasta criada: {caminho_nova_pasta}")
        else:
            messagebox.showerror("Erro", "A pasta já existe.")

# Função para criar um novo arquivo
def criar_arquivo():
    nome_arquivo = simpledialog.askstring("Criar Arquivo", "Nome do novo arquivo (com extensão .txt):")
    if nome_arquivo:
        caminho_novo_arquivo = os.path.join(historico_pastas[-1], nome_arquivo)
        if not os.path.exists(caminho_novo_arquivo):
            with open(caminho_novo_arquivo, "w") as f:
                f.write("")  # Cria um arquivo vazio
            listar_pastas_arquivos(historico_pastas[-1])  # Atualiza a lista de arquivos
            adicionar_log(f"Arquivo criado: {caminho_novo_arquivo}")
        else:
            messagebox.showerror("Erro", "O arquivo já existe.")


# Função para apagar uma pasta ou arquivo com barra de progresso
def apagar_item():
    selected_item = tree.focus()  # Verifica qual pasta ou arquivo foi selecionado
    if not selected_item:
        return
    caminho = tree.item(selected_item, "values")[0]

    if os.path.isdir(caminho):
        resposta = messagebox.askyesno("Confirmação", "Tem certeza que deseja apagar esta pasta e todo o conteúdo?")
        if resposta:
            try:
                # Calcula o total de arquivos para deletar (para a barra de progresso)
                total_itens = sum([len(files) for r, d, files in os.walk(caminho)])

                # Cria uma nova janela para mostrar a barra de progresso
                progress_window = tk.Toplevel()
                progress_window.title("Apagando pasta")
                tk.Label(progress_window, text="Apagando...").pack(pady=10)
                progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=300, mode="determinate")
                progress_bar.pack(pady=10)
                
                progress_bar["maximum"] = total_itens

                # Função para atualizar a barra de progresso
                def atualizar_barra_de_progresso(count):
                    progress_bar["value"] = count
                    progress_window.update_idletasks()

                # Função para apagar o conteúdo da pasta e atualizar a barra de progresso
                def apagar_pasta_recursivamente():
                    count = 0
                    for root, dirs, files in os.walk(caminho, topdown=False):
                        for file in files:
                            try:
                                os.remove(os.path.join(root, file))
                                count += 1
                                atualizar_barra_de_progresso(count)
                            except Exception as e:
                                adicionar_log(f"Erro ao apagar arquivo: {file}. Erro: {str(e)}")

                        for dir in dirs:
                            try:
                                shutil.rmtree(os.path.join(root, dir))
                                adicionar_log(f"Pasta removida: {dir}")
                            except Exception as e:
                                adicionar_log(f"Erro ao apagar pasta: {dir}. Erro: {str(e)}")

                    try:
                        shutil.rmtree(caminho)  # Remove a pasta principal
                        adicionar_log(f"Pasta apagada: {caminho}")
                    except OSError as e:
                        messagebox.showerror("Erro", "Não foi possível apagar a pasta.")
                        adicionar_log(f"Erro ao apagar pasta: {caminho}. Erro: {str(e)}")

                    progress_window.destroy()  # Fecha a janela de progresso após apagar

                # Inicia o processo de apagar com barra de progresso
                apagar_pasta_recursivamente()
                listar_pastas_arquivos(historico_pastas[-1])  # Atualiza a lista de pastas
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao apagar pasta. Erro: {str(e)}")
    else:
        try:
            os.remove(caminho)  # Remove o arquivo
            listar_pastas_arquivos(historico_pastas[-1])  # Atualiza a lista de arquivos
            adicionar_log(f"Arquivo apagado: {caminho}")
        except OSError as e:
            messagebox.showerror("Erro", "Não foi possível apagar o arquivo.")
            adicionar_log(f"Erro ao apagar arquivo: {caminho}. Erro: {str(e)}")


# Função para pesquisar arquivos e pastas
def pesquisar():
    termo_pesquisa = entry_pesquisa.get()  # Acessa a entrada de pesquisa
    listar_pastas_arquivos(historico_pastas[-1], pesquisa=termo_pesquisa)
    adicionar_log(f"Pesquisa realizada: {termo_pesquisa}")

# Função principal para criar a interface gráfica
def criar_janela():
    root = tk.Tk()
    root.title("Vizioon Explorer")
    root.geometry("900x600")  # Aumentei a altura da janela para ajustar melhor o layout
    root.iconbitmap("explorador.ico")
    
    global caminho_atual, entry_pesquisa  # Declare entry_pesquisa como global aqui

    caminho_atual = tk.StringVar()

    # Campo de entrada para exibir o caminho atual
    frame_caminho = tk.Frame(root)
    frame_caminho.pack(fill="x", padx=10, pady=5)
    
    label_caminho = tk.Label(frame_caminho, text="Caminho Atual:")
    label_caminho.pack(side="left")
    
    entry_caminho = tk.Entry(frame_caminho, textvariable=caminho_atual, state="readonly", width=80)
    entry_caminho.pack(fill="x", padx=10, pady=5)

    # Campo de pesquisa
    frame_pesquisa = tk.Frame(root)
    frame_pesquisa.pack(fill="x", padx=10, pady=5)

    entry_pesquisa = tk.Entry(frame_pesquisa, width=50)  # entry_pesquisa agora é global
    entry_pesquisa.pack(side="left", padx=5)
    
    btn_pesquisar = tk.Button(frame_pesquisa, text="Pesquisar", command=pesquisar, width=15, height=0)
    btn_pesquisar.pack(side="left",padx=5)

    # Layout da interface principal com treeview e tela de logs
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    # Criação da Treeview para listar as pastas e arquivos
    global tree
    tree = ttk.Treeview(main_frame)
    tree.heading("#0", text="Pastas e Arquivos", anchor="w")
    tree.pack(side="left", fill="both", expand=True)

    # Associando duplo clique para abrir pastas/arquivos
    tree.bind("<Double-1>", ao_clicar_duas_vezes)

    # Menu de contexto para clicar com o botão direito em arquivos
    global menu_contexto
    menu_contexto = tk.Menu(root, tearoff=0)

    # Adicionando clique com botão direito
    tree.bind("<Button-3>", abrir_menu)

    # Tela de logs ao lado direito
    frame_logs = tk.Frame(main_frame)
    frame_logs.pack(side="right", fill="y")

    global text_logs
    text_logs = tk.Text(frame_logs, state="normal", width=40)
    text_logs.pack(fill="y", expand=True)

    label_logs = tk.Label(frame_logs, text="Logs", font=("Helvetica", 10, "bold"))
    label_logs.pack(side="top")

    # Botões para interagir com as pastas e arquivos
    frame_botoes = tk.Frame(root)
    frame_botoes.pack(fill="x", padx=20, pady=20)  

    # Botões maiores com mais altura e largura
    btn_entrar_editar = tk.Button(frame_botoes, text="Entrar / Editar", command=entrar_ou_editar, bg="#4CAF50", fg="white", width=15, height=2)
    btn_entrar_editar.pack(side="left", padx=10)

    btn_voltar = tk.Button(frame_botoes, text="Voltar", command=voltar, bg="#2196F3", fg="white", width=15, height=2)
    btn_voltar.pack(side="left", padx=10)

    btn_criar_pasta = tk.Button(frame_botoes, text="Criar Pasta", command=criar_pasta, bg="#FFC107", fg="black", width=15, height=2)
    btn_criar_pasta.pack(side="left", padx=10)

    btn_criar_arquivo = tk.Button(frame_botoes, text="Criar Arquivo", command=criar_arquivo, bg="#FFC107", fg="black", width=15, height=2)
    btn_criar_arquivo.pack(side="left", padx=10)

    btn_apagar = tk.Button(frame_botoes, text="Apagar", command=apagar_item, bg="#F44336", fg="white", width=15, height=2)
    btn_apagar.pack(side="left", padx=10)

    # Adicionando o botão "Sobre"
    btn_sobre = tk.Button(frame_botoes, text="Sobre", command=exibir_sobre, bg="#607D8B", fg="white", width=15, height=2)
    btn_sobre.pack(side="left", padx=10)

    # Lista a pasta inicial (diretório atual)
    global historico_pastas
    historico_pastas = [os.getcwd()]  # Inicia no diretório atual
    listar_pastas_arquivos(historico_pastas[-1])

    root.mainloop()

# Inicia a aplicação
criar_janela()



