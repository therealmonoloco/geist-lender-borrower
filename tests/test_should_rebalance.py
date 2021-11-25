def test_all_params_in_range_should_not_rebalance(GeistLibrary, borrow_token):
    assert (
        GeistLibrary.shouldRebalance(
            borrow_token,
            1e27,  # acceptable costs
            5_000,  # target LTV
            6_000,  # warning LTV
            1_000,  # total collateral ETH
            500,  # total debt ETH
        )
        == False
    )


def test_current_ltv_higher_than_warning_should_adjust(GeistLibrary, borrow_token):
    assert (
        GeistLibrary.shouldRebalance(
            borrow_token,
            1e27,  # acceptable costs
            5_000,  # target LTV
            6_000,  # warning LTV
            1_000,  # total collateral ETH
            601,  # total debt ETH
        )
        == True
    )


def test_high_borrow_cost_should_adjust(GeistLibrary, borrow_token):
    assert (
        GeistLibrary.shouldRebalance(
            borrow_token,
            0.0001 * 1e27,  # 0.01% max acceptable cost
            5_000,  # target LTV
            6_000,  # warning LTV
            1_000,  # total collateral ETH
            500,  # total debt ETH
        )
        == True
    )


def test_take_more_debt_should_adjust(GeistLibrary, borrow_token):
    # current ltv = debt / colateral - 39 so it does adjust (over 10 bps to the other side)
    assert (
        GeistLibrary.shouldRebalance(
            borrow_token,
            1e27,  # acceptable costs
            5_000,  # target LTV
            6_000,  # warning LTV
            1_000,  # total collateral ETH
            390,  # total debt ETH
        )
        == True
    )


def test_take_more_debt_under_rebalancing_band_should_not_adjust(
    GeistLibrary, borrow_token
):
    # current ltv = debt / colateral - 41 so it does not adjust (less than 10 bps to the other side)
    assert (
        GeistLibrary.shouldRebalance(
            borrow_token,
            1e27,  # acceptable costs
            5_000,  # target LTV
            6_000,  # warning LTV
            1_000,  # total collateral ETH
            410,  # total debt ETH
        )
        == False
    )
