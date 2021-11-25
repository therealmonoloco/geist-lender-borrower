from brownie import chain, Wei, Contract


def test_rewards(
    vault,
    strategy,
    gov,
    token,
    token_whale,
    aToken,
    vdToken,
    yvault,
    token_incentivised,
    borrow_incentivised,
    borrow_token,
    borrow_whale,
):
    ic = get_incentives_controller(
        aToken, vdToken, token_incentivised, borrow_incentivised
    )
    aToken = aToken
    vdToken = vdToken

    token.approve(vault, 2 ** 256 - 1, {"from": token_whale})
    vault.deposit(500_000 * (10 ** token.decimals()), {"from": token_whale})

    assert ic.claimableReward(strategy, [aToken])[0] == 0
    assert ic.claimableReward(strategy, [vdToken])[0] == 0
    assert ic.claimableReward(strategy, [aToken, vdToken]) == (0, 0)

    chain.sleep(1)
    strategy.harvest({"from": gov})
    assert yvault.balanceOf(strategy) > 0

    chain.sleep(2 * 24 * 3600)  # 48 hours later
    chain.mine(1)

    aTokenRewards = ic.claimableReward(strategy, [aToken])[0]
    vdTokenRewards = ic.claimableReward(strategy, [vdToken])[0]
    if token_incentivised:
        assert aTokenRewards > 0
    if borrow_incentivised:
        assert vdTokenRewards > 0
    assert ic.claimableReward(strategy, [aToken, vdToken]) == (
        aTokenRewards,
        vdTokenRewards,
    )

    chain.sleep(1)
    strategy.harvest({"from": gov})
    aTokenRewards = ic.claimableReward(strategy, [aToken])[0]
    vdTokenRewards = ic.claimableReward(strategy, [vdToken])[0]
    assert aTokenRewards == 0
    assert vdTokenRewards == 0

    # Send some profit to yvault
    borrow_token.transfer(
        yvault, 20_000 * (10 ** borrow_token.decimals()), {"from": borrow_whale}
    )

    assert strategy.harvestTrigger(Wei("1 ether")) == True

    accumulatedRewards = ic.claimableReward(strategy, [vdToken, aToken])
    if borrow_incentivised or token_incentivised:
        assert sum(accumulatedRewards) > 0

    chain.sleep(1)
    print(ic.claimableReward(strategy, [vdToken, aToken]))

    tx = strategy.harvest({"from": gov})

    print(ic.claimableReward(strategy, [vdToken, aToken]))

    if borrow_incentivised or token_incentivised:
        assert sum(ic.claimableReward(strategy, [vdToken, aToken])) == 0

    # Send some profit to yvault
    borrow_token.transfer(
        yvault, 20_000 * (10 ** borrow_token.decimals()), {"from": borrow_whale}
    )

    assert tx.events["Harvested"]["profit"] > 0

    chain.sleep(1)
    tx = strategy.harvest({"from": gov})
    assert tx.events["Harvested"]


def get_incentives_controller(aToken, vdToken, token_incentivised, borrow_incentivised):
    if token_incentivised:
        ic = Contract(aToken.getIncentivesController())
        return ic
    elif borrow_incentivised:
        ic = Contract(vdToken.getIncentivesController())
        return ic

    return
