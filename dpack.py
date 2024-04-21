import json
import os
from functools import cache
from typing import Literal

import httpx
from ethpm_types import ContractInstance, ContractType
from pydantic import BaseModel, constr

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

    @property
    def contract_instance(self):
        return ContractInstance.model_validate(
            {
                "contractType": self.typename,
                "address": self.address,
                "name": self.objectname,
            }
        )


class Dpack(BaseModel):
    format: Literal["dpack-1"]
    network: str
    types: dict[str, DpackType]
    objects: dict[str, DpackObject]


def load(path) -> Dpack:
    return Dpack.model_validate_json(open(path).read())
