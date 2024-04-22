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

## use with ape

this library also provides an easy wrapper that loads up objects as ape contract instances, so you can interact with them right away.

```python
$ ape console --netwowrk ethereum:mainnet

from ape_tokens import tokens
import dpack.ape

uniswap = dpack.ape.load("examples/uniswap-v3.dpack.json")

uniswap.quoter.quoteExactInputSingle.call((tokens["WETH"], tokens["YFI"], '1 ether', 10000, 0))
```

## make a dpack with ape

ape also makes it easier to author dpacks, since you an leverage its capabilities to fetch the needed abis from an explorer.

see [this example](./examples/uniswap.py) to learn how it's done.
