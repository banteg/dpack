from ape.contracts.base import ContractInstance, ContractContainer
from pydantic import BaseModel

import dpack


class ApeDpack(BaseModel):
    dpack: dpack.Dpack

    @property
    def types(self) -> dict[str, ContractContainer]:
        return {
            name: ContractContainer(data.contract_type) for name, data in self.dpack.types.items()
        }

    @property
    def objects(self) -> dict[str, ContractInstance]:
        return {
            name: self.types[data.typename].at(data.address)
            for name, data in self.dpack.objects.items()
        }

    def __getitem__(self, name):
        """Shorthand subscription access for types"""
        if name in self.types:
            return self.types[name]
        raise KeyError()

    def __getattr__(self, name):
        """Shorthand attribute access for objects"""
        if name in self.objects:
            return self.objects[name]
        raise AttributeError()

    def __dir__(self):
        return super().__dir__() + sorted(self.objects.keys())

    def __repr__(self):
        return f"<ApeDpack types={list(self.types)} objects={list(self.objects)}>"


def load(path):
    return ApeDpack(dpack=dpack.load(path))
