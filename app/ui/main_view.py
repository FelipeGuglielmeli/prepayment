from tkinter import filedialog, messagebox, ttk
from app.controller.prepayment_controller import PrepaymentController


class MainView:
    def __init__(self, root, controller: PrepaymentController):
        self.root = root
        self.controller = controller
        self.root.title("Menu Principal")
        self.root.geometry("600x550") # Aumentei um pouco a altura para o novo botão

        # --- Estrutura de Navegação entre Telas ---
        container = ttk.Frame(root)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (MenuScreen, PrepaymentScreen):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MenuScreen")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def get_controller(self):
        return self.controller

# --- Tela do Menu Principal ---
class MenuScreen(ttk.Frame):
    def __init__(self, parent, main_view_controller):
        super().__init__(parent)
        
        label = ttk.Label(self, text="Menu Principal", font=("Arial", 20, "bold"))
        label.pack(pady=40)
        
        style = ttk.Style()
        style.configure("Menu.TButton", font=("Arial", 12), padding=15)

        process_button = ttk.Button(
            self, 
            text="Processar PrePayment", 
            command=lambda: main_view_controller.show_frame("PrepaymentScreen"),
            style="Menu.TButton"
        )
        process_button.pack(pady=10)
        
# --- Tela do Processador de PrePayment ---
class PrepaymentScreen(ttk.Frame):
    def __init__(self, parent, main_view_controller):
        super().__init__(parent)
        self.main_view = main_view_controller
        self.controller = main_view_controller.get_controller()

        self.file_paths = {'main': '', 'status': {}}
        self.path_labels = {}

        back_button = ttk.Button(self, text="< Voltar ao Menu", command=lambda: main_view_controller.show_frame("MenuScreen"))
        back_button.pack(pady=10, anchor="nw", padx=10)

        ttk.Label(self, text="Selecione os ficheiros de Prepayment:", font=("Arial", 14, "bold")).pack(pady=10)
        self._create_file_selector("Principal (Carteira)", 'main')
        ttk.Separator(self, orient='horizontal').pack(fill='x', pady=15, padx=20)
        ttk.Label(self, text="Ficheiros de Status (Opcional):", font=("Arial", 12)).pack(pady=5)
        
        status_keys = ['completely_canceled', 'old_assignment', 'partially_cancelled', 'without_identification']
        for key in status_keys:
            self._create_file_selector(key.replace('_', ' ').title(), key, is_status=True)
        
        self.btn_processar = ttk.Button(self, text="Processar e Guardar", command=self.processar, state="disabled")
        self.btn_processar.pack(pady=25, ipady=10)

    def _create_file_selector(self, label_text, key, is_status=False):
        frame = ttk.Frame(self)
        frame.pack(fill='x', pady=5, padx=20)
        
        label = ttk.Label(frame, text=f"{label_text}:", width=30)
        label.pack(side="left", padx=5)

        path_label = ttk.Label(frame, text="Nenhum ficheiro", foreground="gray", width=40, anchor="w")
        path_label.pack(side="left", padx=5)

        if is_status:
            self.path_labels[key] = path_label
        else:
            self.path_labels['main'] = path_label

        def select_file():
            path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
            if path:
                filename = path.split('/')[-1]
                path_label.config(text=filename, foreground="blue")
                if is_status:
                    self.file_paths['status'][key] = path
                else:
                    self.file_paths['main'] = path
                self.check_process_button_state()
        
        button = ttk.Button(frame, text="Selecionar...", command=select_file)
        button.pack(side="right", padx=5)

    def check_process_button_state(self):
        if self.file_paths['main']:
            self.btn_processar.config(state="normal")
        else:
            self.btn_processar.config(state="disabled")
    
    def _clear_interface(self):
        self.file_paths = {'main': '', 'status': {}}
        for label in self.path_labels.values():
            label.config(text="Nenhum ficheiro", foreground="gray")
        self.check_process_button_state()
            
    def processar(self):
        main_file = self.file_paths['main']
        status_files = self.file_paths['status']
        
        self.btn_processar.config(state="disabled")
        self.main_view.root.update_idletasks()

        # ALTERAÇÃO: Capturar o DataFrame processado do controller
        success, message, processed_df = self.controller.process_spreadsheets(main_file, status_files)
        
        if success:
            messagebox.showinfo("Sucesso", message)
            
            # NOVO: Perguntar ao utilizador se deseja descarregar o ficheiro
            if messagebox.askyesno("Descarregar Excel", "Deseja descarregar a planilha com os dados categorizados?"):
                self.download_excel(processed_df)
            
            self._clear_interface()
        else:
            messagebox.showerror("Erro", message)
            
        self.check_process_button_state()

    def download_excel(self, df):
        """Abre a janela 'Guardar como' e guarda o DataFrame como um ficheiro Excel."""
        if df is None:
            messagebox.showwarning("Aviso", "Não há dados processados para descarregar.")
            return

        try:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Ficheiros Excel", "*.xlsx"), ("Todos os Ficheiros", "*.*")],
                title="Guardar Planilha Categorizada",
                initialfile="prepayment_categorizado.xlsx"
            )

            if save_path: # Se o utilizador não cancelar a janela
                df.to_excel(save_path, index=False)
                messagebox.showinfo("Sucesso", f"Planilha guardada com sucesso em:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Erro ao Guardar", f"Não foi possível guardar o ficheiro:\n{e}")

