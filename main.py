import tkinter as tk
from app.controller.prepayment_controller import PrepaymentController
from app.database.db import SessionLocal, init_db
from app.ui.main_view import MainView

def main():
    # 1. Inicializa o banco de dados (cria a tabela se não existir)
    init_db()
    
    # 2. Cria uma sessão de banco de dados para esta execução
    db_session = SessionLocal()

    # 3. Injeta as dependências: Controller precisa da sessão, View precisa do Controller
    controller = PrepaymentController(db_session)
    
    # 4. Configura e inicia a interface gráfica (Tkinter)
    root = tk.Tk()
    app = MainView(root, controller)
    root.mainloop()

    # 5. Fecha a sessão do banco quando a janela for fechada
    db_session.close()

if __name__ == "__main__":
    main()