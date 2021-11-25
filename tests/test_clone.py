import pytest
from brownie import chain, Wei, reverts, Contract


def test_clone(
    vault,
    strategy,
    strategist,
    rewards,
    keeper,
    gov,
    token,
    token_whale,
    borrow_token,
    borrow_whale,
    yvault,
    cloner,
):
    pd_provider = Contract("0xf3B0611e2E4D2cd6aB4bb3e01aDe211c3f42A8C3")
    a_provider = Contract(pd_provider.ADDRESSES_PROVIDER())
    lp = Contract(a_provider.getLendingPool())

    vault_usdc = Contract("0xEF0210eB96c7EB36AF8ed1c20306462764935607")
    usdc = Contract(vault_usdc.token())
    usdc_whale = "0x2dd7C9371965472E5A5fD28fbE165007c61439E1"

    clone_tx = cloner.cloneGeistLenderBorrower(
        vault,
        strategist,
        rewards,
        keeper,
        vault_usdc,
        True,
        True,
        "StrategyGeistLender" + token.symbol() + "BorrowerUSDC",
    )
    cloned_strategy = Contract.from_abi(
        "Strategy", clone_tx.events["Cloned"]["clone"], strategy.abi
    )

    cloned_strategy.setStrategyParams(
        strategy.targetLTVMultiplier(),
        strategy.warningLTVMultiplier(),
        strategy.acceptableCostsRay(),
        0,
        strategy.maxTotalBorrowIT(),
        strategy.isWantIncentivised(),
        True,  # USDC is not incentivised
        strategy.leaveDebtBehind(),
        strategy.maxLoss(),
        {"from": strategy.strategist()},
    )

    # should fail due to already initialized
    with reverts():
        strategy.initialize(vault, vault_usdc, "NameRevert", {"from": gov})

    vault.updateStrategyDebtRatio(strategy, 0, {"from": gov})
    vault.addStrategy(cloned_strategy, 10_000, 0, 2 ** 256 - 1, 0, {"from": gov})

    token.approve(vault, 2 ** 256 - 1, {"from": token_whale})
    vault.deposit(10 * (10 ** token.decimals()), {"from": token_whale})
    strategy = cloned_strategy
    print_debug(vault_usdc, strategy, lp)
    tx = strategy.harvest({"from": gov})
    assert vault_usdc.balanceOf(strategy) > 0
    print_debug(vault_usdc, strategy, lp)

    # Sleep for 2 days
    chain.sleep(60 * 60 * 24 * 2)
    chain.mine(1)

    # Send some profit to yvETH
    usdc.transfer(vault_usdc, 1_000 * (10 ** usdc.decimals()), {"from": usdc_whale})

    # TODO: check profits before and after
    strategy.harvest({"from": gov})
    print_debug(vault_usdc, strategy, lp)

    # We should have profit after getting some profit from yvETH
    assert vault.strategies(strategy).dict()["totalGain"] > 0
    assert vault.strategies(strategy).dict()["totalLoss"] == 0

    # Enough sleep for profit to be free
    chain.sleep(60 * 60 * 10)
    chain.mine(1)
    print_debug(vault_usdc, strategy, lp)

    # why do we have losses? because of interests
    with reverts():
        vault.withdraw()

    # so we send profits
    usdc.transfer(vault_usdc, 30_000 * (10 ** usdc.decimals()), {"from": usdc_whale})
    vault.withdraw({"from": token_whale})


def test_clone_of_clone(vault, strategist, rewards, keeper, strategy, cloner):
    vault_usdc = Contract("0xEF0210eB96c7EB36AF8ed1c20306462764935607")

    clone_tx = cloner.cloneGeistLenderBorrower(
        vault,
        strategist,
        rewards,
        keeper,
        vault_usdc,
        True,
        True,
        "StrategyGeistLenderWBTCBorrowerSNX",
    )
    cloned_strategy = Contract.from_abi(
        "Strategy", clone_tx.events["Cloned"]["clone"], strategy.abi
    )


def print_debug(yvSNX, strategy, lp):
    yvSNX_balance = yvSNX.balanceOf(strategy)
    yvSNX_pps = yvSNX.pricePerShare()
    totalDebtETH = lp.getUserAccountData(strategy).dict()["totalDebtETH"]

    print(f"yvSNX balance {yvSNX_balance} with pps {yvSNX_pps}")
    yvSNX_value = (yvSNX_balance * yvSNX_pps) / 1e18
    print(f"yvSNX value {yvSNX_value/1e18}SNX vs {totalDebtETH/1e18}ETH\n")
