import dpack
from ape import Contract, networks
import tempfile
from pathlib import Path
from rich import print

# https://docs.uniswap.org/contracts/v3/reference/deployments/ethereum-deployments
uniswap_v3_deployment = {
    "factory": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
    "multicall": "0x1F98415757620B543A52E61c46B32eB19261F984",
    "multicall2": "0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696",
    "proxy_admin": "0xB753548F6E010e7e680BA186F9Ca1BdAB2E90cf2",
    "tick_lens": "0xbfd8137f7d1516D3ea5cA83523914859ec47F573",
    "nft_descriptor": "0x42B24A95702b9986e82d421cC3568932790A48Ec",
    "nonfungible_token_position_descriptor": "0x91ae842A5Ffd8d12023116943e72A606179294f3",
    "transparent_upgradeable_proxy": "0xEe6A57eC80ea46401049E92587E52f5Ec1c24785",
    "nonfungible_position_manager": "0xC36442b4a4522E871399CD717aBDD847Ab11FE88",
    "v3_migrator": "0xA5644E29708357803b5A882D272c41cC0dF92B34",
    "quoter": "0x61fFE014bA17989E743c5F6cB21bF9697530B21e",
    "swap_router": "0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45",
    "permit_2": "0x000000000022D473030F116dDEE9F6B43aC78BA3",
    "universal_router": "0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD",
    "staker": "0xe34139463bA50bD61336E0c446Bd8C0867c6fE65",
    "uni": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
    "pool": "0x8f8EF111B67C04Eb1641f5ff19EE54Cda062f163",
}


def main():
    pack = dpack.Dpack(network="mainnet")
    with tempfile.TemporaryDirectory() as artifacts:
        artifacts = Path(artifacts)
        for objectname, address in uniswap_v3_deployment.items():
            print(objectname, address)
            contract = Contract(address)
            type = contract.contract_type
            path = artifacts / f"{type.name}.json"
            path.write_text(type.model_dump_json(include={"name", "abi"}))
            pack.pack_object(path, typename=type.name, objectname=objectname, address=address)

    print(pack)
    save_path = Path("examples/uniswap-v3.dpack.json")
    pack.save(save_path)
    print(f"saved to {save_path}")


if __name__ == "__main__":
    with networks.parse_network_choice("ethereum:mainnet:geth"):
        main()
