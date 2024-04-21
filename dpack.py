from typing import Literal

import json
from pydantic import BaseModel, constr
import httpx
from ethpm_types import ContractType
import os
from functools import cache


IPFS_RPC_URL = os.environ.get("IPFS_RPC_URL", "http://127.0.0.1:5001")


@cache
def fetch_artifact(cid):
    resp = httpx.post(f"{IPFS_RPC_URL}/api/v0/cat", params={"arg": cid}).json()
    resp["abi"] = json.loads(resp["abi"])
    return resp


class DpackArtifact(BaseModel):
    artifact: dict[Literal["/"], str]

    @property
    def contract_type(self):
        payload = fetch_artifact(self.artifact["/"])
        return ContractType.model_validate(payload)


class DpackType(DpackArtifact):
    typename: constr(pattern=r"[A-Z]\w*")


class DpackObject(DpackArtifact):
    objectname: str
    address: constr(pattern=r"0x[a-zA-Z0-9]{40}")
    typename: constr(pattern=r"[A-Z]\w*")


class Dpack(BaseModel):
    format: Literal["dpack-1"]
    network: str
    types: dict[str, DpackType]
    objects: dict[str, DpackObject]


if __name__ == "__main__":
    from rich import print
    from rich.rule import Rule

    pack = Dpack.model_validate_json(open("weth_ropsten.dpack.json").read())
    print(pack)
    print(pack.types["WETH9"].contract_type)
    print(Rule("done"))
