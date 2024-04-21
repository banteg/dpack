import dpack
import pytest


@pytest.fixture(scope="session")
def pack():
    yield dpack.load("tests/weth_ropsten.dpack.json")


def test_parse(pack):
    print(pack)
    assert "WETH9" in pack.types
    assert "weth" in pack.objects


def test_fetch(pack):
    contract_type = pack.types["WETH9"].contract_type
    print(contract_type)
    assert contract_type.selector_identifiers.keys() == {
        "name()",
        "approve(address,uint256)",
        "totalSupply()",
        "transferFrom(address,address,uint256)",
        "withdraw(uint256)",
        "decimals()",
        "balanceOf(address)",
        "symbol()",
        "transfer(address,uint256)",
        "deposit()",
        "allowance(address,address)",
        "Approval(address,address,uint256)",
        "Transfer(address,address,uint256)",
        "Deposit(address,uint256)",
        "Withdrawal(address,uint256)",
    }


def test_instance(pack):
    instance = pack.objects["weth"].contract_instance
    print(instance)
    assert instance.contract_type == "WETH9"
