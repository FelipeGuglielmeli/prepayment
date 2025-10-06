import pandas as pd
import re
import numpy as np
from sqlalchemy.orm import Session
from app.database.model import Prepayment
from app.repositories.prepayment_repository import PrepaymentRepository

class PrepaymentService:
    def __init__(self, db_session: Session):
        self.repository = PrepaymentRepository(db_session)

    def _ler_excel(self, file_path: str) -> pd.DataFrame | None:
        """Função auxiliar para ler um arquivo Excel de forma segura."""
        try:
            return pd.read_excel(file_path)
        except Exception as e:
            print(f"AVISO: Não foi possível ler o arquivo '{file_path}'. Erro: {e}")
            return None

    def _formatar_colunas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Formata os nomes das colunas para o padrão snake_case."""
        novas_colunas = []
        for coluna in df.columns:
            nova_coluna = str(coluna).lower().strip()
            nova_coluna = re.sub(r'[^a-z0-9]+', '_', nova_coluna)
            novas_colunas.append(nova_coluna)
        df.columns = novas_colunas
        return df

    def _tratar_dados(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica as regras de limpeza e tratamento de dados no DataFrame principal."""
        df = df.iloc[:-3].copy()

        if 'customer' in df.columns:
            df['customer'] = pd.to_numeric(df['customer'], errors='coerce').astype('Int64').astype(str).replace('<NA>', None)

        if 'amount_brl' in df.columns:
            df['amount_brl'] = pd.to_numeric(df['amount_brl'], errors='coerce').fillna(0)
        if 'amount_usd' in df.columns:
            df['amount_usd'] = pd.to_numeric(df['amount_usd'], errors='coerce').fillna(0)
        
        
        if 'accounting_document' in df.columns:
            df['accounting_document'] = pd.to_numeric(df['accounting_document'], errors='coerce').astype('Int64')

        df['customer_hl_name'].replace('', np.nan, inplace=True)
        df['customer_hl_name'].fillna(df['customer_name'], inplace=True)

        df['status'].replace('', np.nan, inplace=True)
        df['status'].fillna('A INICIAR - AR', inplace=True)
        
        df = df.iloc[:-3]
        
        colunas_para_remover = ['region_sold_to', 'agent', 'agent_name', 'segment', 'sales_office_name']
        df.drop(columns=colunas_para_remover, inplace=True, errors='ignore')

        return df

    def classificar_prepay(self, main_file_path: str, status_files: dict[str, str]):
        """
        Orquestra todo o processo: ler, formatar, tratar, categorizar e salvar.
        'status_files' é um dicionário como: {'completely_canceled': 'caminho/do/arquivo.xlsx', ...}
        """
        print("Iniciando processamento e classificação...")
        
        main_df = self._ler_excel(main_file_path)
        if main_df is None:
            raise ValueError(f"Não foi possível ler o arquivo principal: {main_file_path}")
        
        main_df = self._formatar_colunas(main_df)
        main_df = self._tratar_dados(main_df)

        main_df['prepayment_type'] = 'standard_process'
        
        for status_key, file_path in status_files.items():
            print(f"Processando arquivo de status: '{status_key}'")
            status_df = self._ler_excel(file_path)
            if status_df is None:
                continue
            
            status_df = self._formatar_colunas(status_df)

            if 'accounting_document' in status_df.columns:
                status_df['accounting_document'] = pd.to_numeric(status_df['accounting_document'], errors='coerce').astype('Int64')
                status_ids = set(status_df['accounting_document'].dropna().unique())
                main_df.loc[main_df['accounting_document'].isin(status_ids), 'prepayment_type'] = status_key
            else:
                print(f"AVISO: Coluna 'accounting_document' não encontrada em '{file_path}'.")

        prepayments_to_save = []
        main_df = main_df.replace({pd.NaT: None})

        for _, row in main_df.iterrows():
            prepayment_obj = Prepayment(
                company_code=row.get('company_code'),
                aging_ar=row.get('aging_ar'),
                aging_cancelled=row.get('aging_cancelled'),
                cancelled_status=row.get('cancelled_status'),
                cancelled_reason=row.get('cancelled_reason'),
                customer_hl_name=row.get('customer_hl_name'),
                customer=row.get('customer'),
                customer_name=row.get('customer_name'),
                posting_date=row.get('posting_date'),
                net_due_date=row.get('net_due_date'),
                amount_usd=row.get('amount_usd'),
                exch_rate=row.get('exch_rate'),
                amount_brl=row.get('amount_brl'),
                currency=row.get('currency'),
                document_type=row.get('document_type'),
                reference_document=row.get('reference_document'),
                contract_number=row.get('contract_number'),
                accounting_document=row.get('accounting_document'),
                regional=row.get('regional'),
                account_manager_name=row.get('account_manager_name'),
                status=row.get('status'),
                analyst=row.get('analyst'),
                comments=row.get('comments'),
                prepayment_type=row.get('prepayment_type')
            )
            prepayments_to_save.append(prepayment_obj)
        
        if not prepayments_to_save:
            raise ValueError("Nenhum dado válido para salvar após o processamento.")

        print("Enviando dados para a camada de persistência...")
        num_saved = self.repository.save_bulk(prepayments_to_save)
        print(f"{num_saved} registros salvos com sucesso.")
        return num_saved, main_df
