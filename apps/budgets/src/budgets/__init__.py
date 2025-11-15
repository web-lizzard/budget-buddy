from monetary import Currency, Money
from monetary.utils import is_negative, is_positive, sign


def main() -> None:
    money_1 = Money.mint(100.0, Currency.USD)
    money_2 = Money.mint(200.0, Currency.USD)
    print(is_positive(money_1))
    print(is_negative(money_1))
    print(sign(money_1))
    print(money_1 + money_2)
    print(money_1 - money_2)
    print(money_1 * 2)
    print(money_1 / 2)
    print(money_1 == money_2)
    print(money_1 != money_2)
    print(money_1 < money_2)
    print(money_1 <= money_2)
    print(money_1 > money_2)
    print(money_1 >= money_2)
