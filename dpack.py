import json
import os
from functools import cache
from typing import Literal

import httpx
from ethpm_types import ContractInstance, ContractType
from pydantic import BaseModel, constr
from pathlib import Path

IPFS_RPC_URL = os.environ.get("IPFS_RPC_URL", "http://127.0.0.1:5001")
IpfsCid = constr(pattern=r"[bB][aA][fF][yY]?\w{48,}")


@cache
def fetch_artifact(cid):
    resp = httpx.post(f"{IPFS_RPC_URL}/api/v0/cat", params={"arg": cid}).json()
    resp["abi"] = json.loads(resp["abi"])
    return resp


def upload_artifact(path: Path) -> IpfsCid:
    resp = httpx.post(
        f"{IPFS_RPC_URL}/api/v0/add",
        params={"cid-version": 1},
        files={"file": path.open("rb")},
    )
    return resp.json()["Hash"]


class DpackArtifact(BaseModel):
    artifact: dict[Literal["/"], IpfsCid]

    @property
    def contract_type(self):
        payload = fetch_artifact(self.artifact["/"])
        return ContractType.model_validate(payload)

    @classmethod
    def from_path(cls, *, path, **fields):
        cid = upload_artifact(path)
        return cls.model_validate(dict(artifact={"/": cid}, **fields))


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

    def __getattr__(self, name):
        if name in self.objects:
            return self.objects[name].contract_instance

    def __dir__(self):
        return super().__dir__() + sorted(self.objects.keys())


class PackBuilder(BaseModel):
    network: str
    types: dict[str, Path] = {}
    objects: dict[str, dict] = {}

    def pack_type(self, *, typename, artifact):
        self.types[typename] = Path(str(artifact))
        return self

    def pack_object(self, *, typename, artifact, objectname, address):
        if typename not in self.types:
            self.types[typename] = Path(str(artifact))
        self.objects[objectname] = {"typename": typename, "address": address}
        return self

    def build(self):
        pack = Dpack(format="dpack-1", network=self.network, types={}, objects={})
        for type, path in self.types.items():
            pack.types[type] = DpackType.from_path(path=path, typename=type)
        for obj, data in self.objects.items():
            pack.objects[obj] = DpackObject.from_path(
                path=self.types[data["typename"]],
                objectname=obj,
                address=data["address"],
                typename=data["typename"],
            )

        return pack


def load(path) -> Dpack:
    return Dpack.model_validate_json(open(path).read())


def builder(network) -> PackBuilder:
    return PackBuilder(network=network)
