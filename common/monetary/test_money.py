from .money import Money


def test_minting_money():
    money = Money.mint(3.2)

    assert money.current_amount == 320


def test_subtracting_moneys():
    m1 = Money.mint(20.2)
    m2 = Money.mint(10.5)

    result = m1 - m2

    assert result.current_amount == 970


def test_adding_moneys():
    m1 = Money.mint(20.2)
    m2 = Money.mint(10.5)

    result = m1 + m2

    assert result.current_amount == 3070


def test_dividing_by_num():
    m1 = Money.mint(20.2)

    result = m1 / 2

    assert result.current_amount == 1010
