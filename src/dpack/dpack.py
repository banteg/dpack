import json
import os
from functools import cache
from pathlib import Path
from typing import Literal

import httpx
from ethpm_types import ContractInstance, ContractType
from pydantic import BaseModel, constr

IPFS_RPC_URL = os.environ.get("IPFS_RPC_URL", "http://127.0.0.1:5001")
IpfsCid = constr(pattern=r"[bB][aA][fF][yY]?\w{48,}")


@cache
def fetch_artifact(cid):
    resp = httpx.post(f"{IPFS_RPC_URL}/api/v0/cat", params={"arg": cid}).json()
    if isinstance(resp["abi"], str):
        resp["abi"] = json.loads(resp["abi"])
    return resp


def upload_artifact(path: Path | str) -> IpfsCid:
    if isinstance(path, str):
        path = Path(path)
    assert path.is_file(), "provide a valid path"
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
        payload.setdefault("contractName", self.typename)
        return ContractType.model_validate(payload)

    @classmethod
    def from_path(cls, path: Path, **fields):
        cid = upload_artifact(path)
        return cls.model_validate(dict(artifact={"/": cid}, **fields))


class DpackType(DpackArtifact):
    typename: constr(pattern=r"[A-Z]\w*")


class DpackObject(DpackArtifact):
    objectname: constr(pattern=r"[a-z]\w*")
    address: constr(pattern=r"0x[a-zA-Z0-9]{40}")
    typename: constr(pattern=r"[A-Z]\w*")

    @property
    def contract_instance(self):
        return ContractInstance(
            contractType=self.typename, name=self.objectname, address=self.address
        )


class Dpack(BaseModel):
    format: Literal["dpack-1"] = "dpack-1"
    network: str
    types: dict[str, DpackType] = {}
    objects: dict[str, DpackObject] = {}

    def __getattr__(self, name):
        if name in self.objects:
            return self.objects[name].contract_instance
        raise AttributeError()

    def __dir__(self):
        return super().__dir__() + sorted(self.objects.keys())

    def pack_type(self, path: Path, typename: str):
        self.types[typename] = DpackType.from_path(path, typename=typename)
        return self

    def pack_object(self, path: Path, typename: str, objectname: str, address: str):
        if typename not in self.types:
            self.pack_type(path, typename)
        self.objects[objectname] = DpackObject.from_path(
            path, typename=typename, objectname=objectname, address=address
        )
        return self

    def save(self, path: str | Path):
        if isinstance(path, str):
            path = Path(path)
        path.write_text(self.model_dump_json(indent=2))


def load(path) -> Dpack:
    return Dpack.model_validate_json(open(path).read())
