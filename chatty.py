import random
import time
from datetime import timedelta
from logging import getLogger

import marvin
from marvin import ai_fn
from prefect import flow, get_run_logger, task
from prefect.tasks import task_input_hash
from pydantic import BaseModel

marvin.settings.llm_model = "openai/gpt-3.5-turbo"
marvin.settings.llm_temperature = 1.1


@ai_fn
def generate_software_components(package_prefix: str) -> list[str]:
    """Given the name of a Python package, generate a list of between 10 and 20
    realistic looking submodules of that package, in dotted notation.  The submodules
    should look like they come from a typical web or data engineering application.  The
    submodules should be unique, and may be nested up to 4 layers deep.  Don't include
    numbered modules like `utils2` or `utils3`.  Feel free to include cool sounding
    words on occasion, but don't overdo it.  The same word should not repeat in any of
    the submodules.

    The environment of this application is a typical cloud environment, using common
    open source technologies typical of a web or data engineering application.  Some
    components may be transactional and real-time, and others may be batch-oriented
    data warehousing and machine learning tasks.  The names of the components should
    sound like they are related to business or technical workflows that
    might be occurring in that environment.
    """
    ...


@task(
    cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1), refresh_cache=True
)
def get_software_components(package_prefix: str) -> list[str]:
    get_run_logger().info("Generating software components for %r", package_prefix)
    return generate_software_components(package_prefix)


class Log(BaseModel):
    level: str
    message: str
    duration: float


@ai_fn
def generate_log_lines(component_name: str) -> list[Log]:
    """Given the name of a Python package, generate between 20 and 100 lines of log
    output that look like they would come from that component of a typical web or data
    engineering application.  The application is built in Python and when it does have
    an error, it will will raise fairly typical Python exceptions with tracebacks.

    The messages of these log lines should be between 5 and 100 words long, with a mean
    of around 8.  The messages should represent the kinds of things developers usually
    include in their logs, like the start and stop of operations, ongoing progress
    updates and helpful debugging information.  The messages should be in English, and
    may also include structured values like user IDs, URLs, database IDs, financial
    transactions, and any other kind of general values that a developer would include in
    a log line.  Be specific with the kinds of operations that are happening and vary
    things up a little bit.  The name of the component should not be included in the log
    message itself.

    The environment of this application is a typical cloud environment, using common
    open source technologies typical of a web or data engineering application.  Some
    components may be transactional and real-time, and others may be batch-oriented data
    warehousing and machine learning tasks.

    The level should be one of INFO, WARNING, ERROR.  Distribute the messages so that
    most of the lines are INFO, a small portion are WARNING, and a very small portion
    are ERROR.  Many of the ERROR messages should look like random environmental
    failures, like network hiccups, database errors, filesystem failures, etc.  The rest
    should look like preventable Python exceptions, errors from external requests, or
    application logic errors.

    You don't always need to include WARNING and ERROR logs. After an ERROR, you can
    occasionally include something that looks like an automatic recovery, like a retry
    or a graceful degradation to other behavior, both other times, just make it look
    like the program crashed out there.

    With each log line, include a duration between 0.1 and 3.0 seconds with a mean of
    around 0.2 second to simulate the time it took to process the operation the log line
    is referencing.  Distribute the durations so that most lines are fast, and a few are
    a bit longer.
    """
    ...


@task(
    cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1), refresh_cache=True
)
def get_log_lines(component: str) -> list[tuple[str, str, float]]:
    get_run_logger().info("Generating log lines for %r", component)
    return [
        (log.level, log.message, log.duration) for log in generate_log_lines(component)
    ]


@flow
def chatty():
    components = get_software_components("coolness")
    for _ in range(100):
        component = random.choice(components)
        logger = getLogger(component)
        logs = get_log_lines(component)
        for level, message, duration in logs:
            time.sleep(max(min(duration, 3.0), 0.0))
            match (level):
                case "INFO":
                    logger.info(message)
                case "WARNING":
                    logger.info(message)
                case "ERROR":
                    logger.error(message)

            # cause a crash every once in a while
            if random.random() < 0.001:
                raise Exception(message)


if __name__ == "__main__":
    chatty()
