# app/repositories/prepayment_repository.py
from sqlalchemy.orm import Session

from app.database.model import Prepayment

class PrepaymentRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def save_bulk(self, prepayments: list[Prepayment]):
        try:
            self.db.add_all(prepayments)
            self.db.commit()
            return len(prepayments)
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao salvar em massa: {e}")
            raise e