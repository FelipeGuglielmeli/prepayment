from sqlalchemy.orm import Session

from app.service.prepayment_service import PrepaymentService

class PrepaymentController:
    def __init__(self, db_session: Session):
        self.service = PrepaymentService(db_session)

    def process_spreadsheets(self, main_file_path: str, status_files: dict[str, str]):
        try:
            if not main_file_path:
                return False, "O arquivo principal 'CarteiraPrepayment' não foi selecionado."
            
            num_saved, processed_df = self.service.classificar_prepay(main_file_path, status_files)
            return True, f"{num_saved} registos foram processados e guardados com sucesso!", processed_df
        except Exception as e:
            return False, f"Ocorreu um erro durante o processamento: {e}", None
