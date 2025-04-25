from .dto import DTO


class MoneyDTO(DTO):
    amount: int
    currency: str
