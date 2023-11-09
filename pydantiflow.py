import pydantic
from prefect import flow, get_run_logger, task
from pydantic import BaseModel


class User(BaseModel):
    name: str
    email: str


@task
def log_user(user: User):
    logger = get_run_logger()
    logger.info("From task %r %r", user, user.model_dump())


@flow
def pydantiflow(user: User):
    logger = get_run_logger()
    logger.info("Running on pydantic==%s", pydantic.VERSION)
    logger.info("From flow %r %r", user, user.model_dump())
    log_user(user)
    log_user.submit(user).result()


if __name__ == "__main__":
    pydantiflow(User(name="Guidry", email="chris.g@prefect.io"))
