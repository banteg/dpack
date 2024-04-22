# dpack-py ☀️

a python port of [dpack](https://github.com/ricobank/dpack/tree/master) evm packaging format.

dpack allows you to share the entire deployment with all the appropriate addresses and artifacts needed to interact with evm contracts.

the library provides a low-level implementation, as well as bindings for [ape](https://github.com/apeworx/ape).

## install

```sh
pip install dpack-py
```

since dpack uses ipfs pointers, it requires you running an ipfs daemon. see [ipfs docs](https://docs.ipfs.tech/install/command-line/#install-official-binary-distributions) for how to install it.

you can set an `IPFS_RPC_URL` environment variable if you use a remote ipfs node.

## developing

to set up the extra libraries useful for development:

```sh
uv venv
make dev
```

## load a dpack
use `dpack.load` to load a dpack from a local file. it will lazily fetch the needed artifacts from ipfs when you access the corresponding contract types and objects.

both `types` and `objects` expose a `contract_type` property decoded by `ethpm-types` into a [python model](https://github.com/ApeWorX/ethpm-types/blob/66eb1b277a42f25ef3da0c5fac5ded6b74fc3462/ethpm_types/contract_type.py#L241). it allows easy abi lookups like shown below.

```python
import dpack

pack = dpack.load("examples/uniswap-v3.dpack.json")

pack.types['UniswapV3Factory'].contract_type.selector_identifiers
```

`objects` also expose a `contract_instance` property (not the same as in ape) that allows looking up contract `typename` and `address`.

```python
pack.objects['factory'].address
# or use a shorthand attribute access
pack.factory.address
```

## make a dpack

to make a dpack, use `pack_type` and `pack_object` methods. packing types is optional as you can just pack your named objects and the library will take care of packing unique contract types automatically.

```python
import dpack

pack = (
    dpack.Dpack(network="sepolia")
    .pack_object(
        path="tests/weth-ropsten-artifact.json",
        typename="WETH9",
        objectname="weth",
        address="0xfFf9976782d46CC05630D1f6eBAb18b2324d6B14",
    )
)
```

to save a dpack to a json file, simply call `save` with a file path.

```python
pack.save('weth.sepolia.dpack.json')
```

you may pack as many objects and types as you wish, but note that the current version of the format (`dpack-1`) specifies the network at top level, so you cannot make multichain dpacks yet.

## use dpack in ape

this library also provides an easy wrapper that loads up objects as ape contract instances, so you can interact with them right away.

`types` are exposed as a provider-aware wrapper [ContractContainer](https://github.com/ApeWorX/ape/blob/c2f1bc48c1afe3297a63e4e820dbfb751b90c932/src/ape/contracts/base.py#L1238). `objects` are ready-to-use [ContractInstance](https://github.com/ApeWorX/ape/blob/c2f1bc48c1afe3297a63e4e820dbfb751b90c932/src/ape/contracts/base.py#L815).

types can be also accessed with a subscript shorthand like `pack["MyType"]`. you can an address to a type with `.at(address)`, which returns a `ContractInstance`.

objects can be also accessed with an attribute shorthand like `pack.my_contract`.

```python
$ ape console --netwowrk ethereum:mainnet

import dpack.ape

pack = dpack.ape.load('examples/uniswap-v3.dpack.json')
# <ApeDpack types=['UniswapV3Factory', 'UniswapInterfaceMulticall', 'Multicall2', 'ProxyAdmin', 'TickLens', 'NFTDescriptor', 'NonfungibleTokenPositionDescriptor', 'NonfungiblePositionManager', 'V3Migrator', 'QuoterV2', 'SwapRouter02', 'Permit2', 'UniversalRouter', 'UniswapV3Staker', 'Uni', 'UniswapV3Pool'] objects=['factory', 'multicall', 'multicall2', 'proxy_admin', 'tick_lens', 'nft_descriptor', 'nonfungible_token_position_descriptor', 'transparent_upgradeable_proxy', 'nonfungible_position_manager', 'v3_migrator', 'quoter', 'swap_router', 'permit_2', 'universal_router', 'staker', 'uni', 'pool']>

# attribute access is shorthand for objects
pack.factory
# <UniswapV3Factory 0x1F98431c8aD98523631AE4a59f267346ea31F984>

# subscript access is shorthand for types
pack['UniswapV3Pool']
# <UniswapV3Pool>

# you can apply types with .at(address)
[pack['UniswapV3Pool'].at(log['pool']) for log in pack.factory.PoolCreated[:3]]
# [<UniswapV3Pool 0x1d42064Fc4Beb5F8aAF85F4617AE8b3b5B8Bd801>, <UniswapV3Pool 0x6c6Bc977E13Df9b0de53b251522280BB72383700>, <UniswapV3Pool 0x7BeA39867e4169DBe237d55C8242a8f2fcDcc387>]
```

## make a dpack with ape

ape also makes it easier to author dpacks, since you an leverage its capabilities to fetch the needed abis from an explorer.

see [this example](./examples/uniswap.py) to learn how it's done.
