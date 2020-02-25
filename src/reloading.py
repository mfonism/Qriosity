"""
Shamelessly borrowed from the amazing watchgod library

https://github.com/samuelcolvin/watchgod/blob/master/watchgod/main.py
and
https://github.com/samuelcolvin/watchgod/blob/master/watchgod/watcher.py

Thank you, samuelcolvin!
"""
import os
import signal
from multiprocessing import Process

from watchgod import watch, DefaultDirWatcher


def _start_process(target, args, kwargs):
    process = Process(target=target, args=args, kwargs=kwargs or {})
    process.start()
    return process


def _stop_process(process):
    if process.is_alive():
        os.kill(process.pid, signal.SIGINT)
        process.join(5)
        if process.exitcode is None:
            os.kill(process.pid, signal.SIGKILL)
            process.join(1)


class DotPyWatcher(DefaultDirWatcher):
    def should_watch_file(self, entry):
        return entry.name.endswith((".py",))


class HotReloader:
    @staticmethod
    def run(
        path,
        target,
        *,
        args=(),
        kwargs=None,
        callback=None,
        watcher_cls=None,
        debounce=400,
        min_sleep=100
    ):
        """
        Run a function in a subprocess using `multiprocessing.Process`.

        restart it whenever file changes in path.
        """
        watcher = watch(
            path,
            watcher_cls=watcher_cls or DotPyWatcher,
            debounce=debounce,
            min_sleep=min_sleep,
        )
        process = _start_process(target=target, args=args, kwargs=kwargs)
        reloads = 0

        for changes in watcher:
            callback and callback(changes)
            _stop_process(process)
            process = _start_process(target=target, args=args, kwargs=kwargs)
            reloads += 1

        return reloads
