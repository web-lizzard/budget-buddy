from .dto import DTO


class MoneyDTO(DTO):
    amount: float
    currency: str
