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


def test_getattr(pack):
    assert pack.weth == pack.objects["weth"].contract_instance


def test_dir(pack):
    print(dir(pack))
    assert {"weth", "weth9"} & set(dir(pack))


@pytest.mark.parametrize("pack_type", [True, False])
def test_builder(pack, pack_type):
    builder = dpack.Dpack(network="ropsten")
    if pack_type:
        builder.pack_type(typename="WETH9", path="tests/weth-ropsten-artifact.json")
    for name in ["weth", "weth9"]:
        builder.pack_object(
            typename="WETH9",
            path="tests/weth-ropsten-artifact.json",
            objectname=name,
            address="0xc778417E063141139Fce010982780140Aa0cD5Ab",
        )
    assert builder.model_dump() == pack.model_dump()


def test_builder_chaining(pack):
    built = (
        dpack.Dpack(network="ropsten")
        .pack_type(typename="WETH9", path="tests/weth-ropsten-artifact.json")
        .pack_object(
            typename="WETH9",
            path="tests/weth-ropsten-artifact.json",
            objectname="weth",
            address="0xc778417E063141139Fce010982780140Aa0cD5Ab",
        )
        .pack_object(
            typename="WETH9",
            path="tests/weth-ropsten-artifact.json",
            objectname="weth9",
            address="0xc778417E063141139Fce010982780140Aa0cD5Ab",
        )
    )
    assert built.model_dump() == pack.model_dump()
