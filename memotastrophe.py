import gc
import pprint
import textwrap
import weakref
from dataclasses import dataclass
from types import ModuleType

from prefect import flow, task

MB = 1024 * 1024


@dataclass
class Chonk:
    data: bytearray


the_chonk: weakref.ref | None = None


def print_referrers(
    label: str, o: object, depth: int = 0, seen: set[int] | None = None
):
    if o is None:
        print(f"{label}: None")
        return

    seen = seen if seen is not None else set()

    referrers = gc.get_referrers(o)
    seen.add(id(referrers))

    if label:
        print(f"{label}: {len(referrers)}")

    if depth < 5:
        iterator = iter(referrers)
        enumerator = enumerate(iterator)
        for i, r in enumerator:
            if id(r) in seen:
                continue

            seen.add(id(r))
            seen.add(id(referrers))
            seen.add(id(iterator))
            seen.add(id(enumerator))

            if isinstance(r, ModuleType):
                continue

            if depth == 0:
                print()
                print(f"************ referrer {i} ***************")

            print(
                textwrap.indent(
                    f"{type(r)} @ {hex(id(r))}\n{pprint.pformat(r)}",
                    prefix=" " * (4 * depth),
                )
            )
            print()

            # print_referrers("", r, depth + 1, seen)


@task
def parameter_task(chonk: Chonk):
    print_referrers("inside", chonk)
    pass


@flow
def parameter_flow():
    chonk = Chonk(data=bytearray(1024 * MB))

    global the_chonk
    the_chonk = weakref.ref(chonk)

    parameter_task(chonk)
    print_referrers("after", chonk)


@task
def result_task() -> Chonk:
    chonk = Chonk(data=bytearray(20))

    global the_chonk
    the_chonk = weakref.ref(chonk)

    return chonk


@flow
def result_flow():
    result_task()


# repro from https://github.com/PrefectHQ/prefect/issues/10952

import gc
import os
import sys

import psutil
from prefect import flow, task


@task(
    persist_result=False, cache_result_in_memory=False
)  # <----- Remove this line, and the memory is released -----
def my_task(df):
    pass


@flow
def my_sub_flow_1():
    print(
        f"Memory before task: {psutil.Process(os.getpid()).memory_info()[0] / float(1024*1024)}MiB"
    )
    df = bytearray(1024 * 1024 * 1024)  # 1024MiB of memory

    my_task(df)

    print(f"{sys.getrefcount(df)} references to df")
    del df  # release memory
    gc.collect()  # garbage collection not needed, just be certain
    print(
        f"Memory after task: {psutil.Process(os.getpid()).memory_info()[0] / float(1024*1024)}MiB"
    )


if __name__ == "__main__":
    print(
        f"Memory before flow: {psutil.Process(os.getpid()).memory_info()[0] / float(1024*1024)}MiB"
    )

    my_sub_flow_1()

    gc.collect()  # garbage collection not needed, just be certain
    print(
        f"Memory after flow: {psutil.Process(os.getpid()).memory_info()[0] / float(1024*1024)}MiB"
    )

    if the_chonk is not None:
        # print_referrers("after flow", the_chonk())
        gc.collect()
        print_referrers("after gc.collect", the_chonk())
