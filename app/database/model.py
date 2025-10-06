from sqlalchemy import Column, Integer, String, Text, Date, Numeric, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Prepayment(Base):
    """
    Modelo que representa a tabela 'prepayments' no banco de dados.
    """
    __tablename__ = 'prepayments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_code = Column(String(100))
    aging_ar = Column(String(255))
    aging_cancelled = Column(String(255))
    cancelled_status = Column(String(100))
    cancelled_reason = Column(Text)
    customer_hl_name = Column(String(255))
    customer = Column(String(100))
    customer_name = Column(String(255))
    posting_date = Column(Date)
    net_due_date = Column(Date)
    amount_usd = Column(Numeric(15, 2))
    exch_rate = Column(Numeric(15, 6))
    amount_brl = Column(Numeric(15, 2))
    currency = Column(String(10))
    document_type = Column(String(100))
    reference_document = Column(String(100))
    contract_number = Column(String(100))
    accounting_document = Column(String(100))
    regional = Column(String(100))
    account_manager_name = Column(String(255))
    status = Column(String(100))
    analyst = Column(String(255))
    comments = Column(Text)
    prepayment_type = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self):
        return f"<Prepayment(id={self.id}, customer='{self.customer_name}', amount_brl={self.amount_brl})>"
