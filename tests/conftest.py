import pytest
from brownie import config, chain, Wei
from brownie import Contract


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


@pytest.fixture(autouse=True)
def GeistLibrary(gov, GeistLenderBorrowerLib):
    yield GeistLenderBorrowerLib.deploy({"from": gov})


@pytest.fixture
def gov(accounts):
    yield accounts.at("0xC0E2830724C946a6748dDFE09753613cd38f6767", force=True)


@pytest.fixture
def user(accounts):
    yield accounts[0]


@pytest.fixture
def rewards(accounts):
    yield accounts[1]


@pytest.fixture
def guardian(accounts):
    yield accounts[2]


@pytest.fixture
def management(accounts):
    yield accounts[3]


@pytest.fixture
def strategist(accounts):
    yield accounts[4]


@pytest.fixture
def keeper(accounts):
    yield accounts[5]


@pytest.fixture
def amount(accounts, token, user):
    amount = 10_000 * 10 ** token.decimals()
    # In order to get some funds for the token you are about to use,
    # it impersonate an exchange address to use it's funds.
    reserve = accounts.at("0x5AA53f03197E08C4851CAD8C92c7922DA5857E5d", force=True)
    token.transfer(user, amount, {"from": reserve})
    yield amount


@pytest.fixture
def wftm():
    yield Contract("0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83")


@pytest.fixture
def vdwftm():
    yield Contract("0x53d01d351Fa001DB3c893388E43e3C630A8764F5")


@pytest.fixture
def lendingPool():
    yield Contract("0x9FAD24f572045c7869117160A571B2e50b10d068")


@pytest.fixture
def token(wftm):
    yield wftm


@pytest.fixture
def aToken(token, lendingPool):
    yield Contract(lendingPool.getReserveData(token).dict()["aTokenAddress"])


@pytest.fixture
def vdToken(borrow_token, lendingPool):
    yield Contract(
        lendingPool.getReserveData(borrow_token).dict()["variableDebtTokenAddress"]
    )


@pytest.fixture
def wftm_whale(accounts):
    yield accounts.at("0x5AA53f03197E08C4851CAD8C92c7922DA5857E5d", force=True)


@pytest.fixture
def dai_whale(accounts):
    yield accounts.at("0x27E611FD27b276ACbd5Ffd632E5eAEBEC9761E40", force=True)


@pytest.fixture
def yvault(request):
    vault = Contract("0x637eC617c86D24E421328e6CAEa1d92114892439")  # yvDAI
    vault.setDepositLimit(2 ** 256 - 1, {"from": vault.governance()})
    yield vault


@pytest.fixture
def borrow_token(yvault):
    yield Contract(yvault.token())


@pytest.fixture
def borrow_whale(dai_whale):
    yield dai_whale


@pytest.fixture
def token_whale(wftm_whale):
    yield wftm_whale


@pytest.fixture
def token_symbol(token):
    yield token.symbol()


@pytest.fixture
def wftm_amount(user, wftm):
    wftm_amount = 10 ** wftm.decimals()
    user.transfer(wftm, wftm_amount)
    yield wftm_amount


@pytest.fixture
def registry():
    yield Contract("0x727fe1759430df13655ddb0731dE0D0FDE929b04")


@pytest.fixture
def live_vault(registry, token):
    yield registry.latestVault(token)


@pytest.fixture
def vault(pm, gov, rewards, guardian, management, token):
    Vault = pm(config["dependencies"][0]).Vault
    vault = guardian.deploy(Vault)
    vault.initialize(token, gov, rewards, "", "", guardian, management, {"from": gov})

    vault.setDepositLimit(2 ** 256 - 1, {"from": gov})
    vault.setManagementFee(0, {"from": gov})
    vault.setPerformanceFee(0, {"from": gov})
    yield vault


incentivised = {
    "0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83": True,  # WFTM
    "0x8D11eC38a3EB5E956B052f67Da8Bdc9bef8Abf3E": True,  # DAI
}


@pytest.fixture
def token_incentivised(token):
    yield incentivised[token.address]


@pytest.fixture
def borrow_incentivised(borrow_token):
    yield incentivised[borrow_token.address]


@pytest.fixture
def strategy(vault, Strategy, gov, cloner):
    strategy = Strategy.at(cloner.original())
    vault.addStrategy(strategy, 10_000, 0, 2 ** 256 - 1, 0, {"from": gov})
    chain.mine()
    yield strategy


@pytest.fixture
def RELATIVE_APPROX():
    yield 1e-5


@pytest.fixture
def cloner(
    strategist,
    vault,
    GeistLenderBorrowerCloner,
    yvault,
    token_incentivised,
    borrow_incentivised,
    token,
    borrow_token,
):
    cloner = strategist.deploy(
        GeistLenderBorrowerCloner,
        vault,
        yvault,
        token_incentivised,
        borrow_incentivised,
        f"Strategy{token.symbol()}Lender{borrow_token.symbol()}Borrower",
    )

    yield cloner
