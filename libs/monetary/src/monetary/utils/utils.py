from ..money import Money


def is_positive(money: Money) -> bool:
    return money.amount > 0


def is_negative(money: Money) -> bool:
    return money.amount < 0


def sign(money: Money) -> str:
    if is_positive(money):
        return "+"
    elif is_negative(money):
        return "-"
    else:
        return "0"
