from logging import Logger, LoggerAdapter, getLogger, basicConfig
from os import getenv
from typing import Dict, List
from rich.console import Console
from rich.logging import RichHandler


class LogHelper:
    logger: Logger = None
    log_adapter: LoggerAdapter = None
    progress = None

    tasks: Dict[str, Dict] = dict()

    def __init__(self):
        width = 150
        basicConfig(
            level=getenv('DJANGO_LOG_LEVEL', 'DEBUG'),  # "NOTSET",
            format="{asctime} {message}",
            style='{',
            datefmt="[%X]",
            handlers=[RichHandler(
                console=Console(width=width),
                locals_max_string=width
            )]
        )
        self.logger = getLogger("rich")
        self.console = Console()

    def set_extra(self, extra) -> LoggerAdapter:
        self.log_adapter = LoggerAdapter(self.logger, extra=extra)
        return self.log_adapter

    def print_exception(self, exc):
        return self.console.print_exception(extra_lines=5, show_locals=True)

    def add_tasks(self, tasks: List[str], total: int):
        for task in tasks:
            self.add_task(task=task, total=total)

    def add_task(self, task: str, total: int = 1):
        self.tasks[task] = {
            "id": self.progress.add_task(description=task, total=total),
            "total": total
        }
