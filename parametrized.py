from datetime import date

from prefect import flow
from pydantic import BaseModel


class Friend(BaseModel):
    name: str
    email: str
    birthdate: date


@flow
def add(x: int | float, y: int | float) -> int | float:
    return x + y


@flow
def objecty(friend1: Friend, friend2: Friend):
    print(repr(friend1))
    print(repr(friend2))
