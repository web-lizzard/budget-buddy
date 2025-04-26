from adapters.outbound.persistence.sql_alchemy.models import TransactionModel
from domain.aggregates.transaction import Transaction


def map_transaction_model_to_domain(model: TransactionModel) -> Transaction:
    """Maps TransactionModel SQLAlchemy object to Transaction domain aggregate."""
    return Transaction(
        id=model.id,
        category_id=model.category_id,
        user_id=model.user_id,
        amount=model.amount,
        transaction_type=model.transaction_type,
        occurred_date=model.occurred_date,
        description=model.description,
    )


def map_transaction_domain_to_model(domain: Transaction) -> TransactionModel:
    """Maps Transaction domain aggregate to TransactionModel SQLAlchemy object."""
    model = TransactionModel(
        id=domain.id,
        category_id=domain.category_id,
        user_id=domain.user_id,
        _amount_amount=domain.amount.amount,
        _amount_currency=domain.amount.currency,
        amount=domain.amount,
        transaction_type=domain.transaction_type,
        occurred_date=domain.occurred_date,
        description=domain.description,
    )
    return model
