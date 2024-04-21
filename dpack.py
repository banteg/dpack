from typing import Literal

from pydantic import BaseModel, constr


class DpackType(BaseModel):
    typename: constr(pattern=r"[A-Z]\w*")
    artifact: dict[Literal["/"], str]


class DpackObject(BaseModel):
    objectname: str
    address: constr(pattern=r"0x[a-zA-Z0-9]{40}")
    typename: constr(pattern=r"[A-Z]\w*")
    artifact: dict[Literal["/"], str]


class Dpack(BaseModel):
    format: Literal["dpack-1"]
    network: str
    types: dict[str, DpackType]
    objects: dict[str, DpackObject]


if __name__ == "__main__":
    from rich import print

    print(Dpack.model_validate_json(open("weth_ropsten.dpack.json").read()))
