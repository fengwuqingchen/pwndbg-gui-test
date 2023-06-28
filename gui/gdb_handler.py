import logging
from typing import List

# These imports are broken here, but will work via .gdbinit
import gdb
from PySide6.QtCore import QObject, Slot, Signal
from pwndbg.commands.context import context_stack, context_regs, context_disasm, context_code, context_backtrace

import os
import fcntl

logger = logging.getLogger(__file__)


def is_target_running():
    # https://sourceware.org/gdb/onlinedocs/gdb/Threads-In-Python.html#Threads-In-Python
    return any([t.is_valid() for t in gdb.selected_inferior().threads()])


def get_fs_base() -> str:
    try:
        logger.debug("Getting fs_base from GDB")
        output: str = gdb.execute("info register fs_base", to_string=True)
        parts = output.split()
        if "fs_base" in output and len(parts) > 1:
            return f"FS  {parts[1]}"
        else:
            return ""
    except gdb.error:
        return ""


class GdbHandler(QObject):
    """A wrapper to interact with GDB/pwndbg via gdb.execute"""
    update_gui = Signal(str, bytes)

    def __init__(self):
        super().__init__()
        self.past_commands: List[str] = []
        self.context_to_func = dict(regs=context_regs, stack=context_stack, disasm=context_disasm, code=context_code,
                                    backtrace=context_backtrace)

    @Slot(str)
    def send_command(self, cmd: str, capture=True):
        """Execute the given command and then update all context panes"""
        try:
            response = gdb.execute(cmd, from_tty=True, to_string=capture)
        except gdb.error as e:
            logger.warning("Error while executing command '%s': '%s'", cmd, str(e))
            response = str(e) + "\n"
        if capture:
            self.update_gui.emit("main", response.encode())

        if not is_target_running():
            logger.debug("Target not running, skipping context updates")
            return
        # Update contexts
        for context, func in self.context_to_func.items():
            context_data: List[str] = func(with_banner=False)
            self.update_gui.emit(context, "\n".join(context_data).encode())

    @Slot(list)
    def execute_cmd(self, arguments: List[str]):
        """Execute the given command in gdb, without capturing"""
        cmd = " ".join(arguments)
        gdb.execute(cmd)

    @Slot(list)
    def set_file_target(self, arguments: List[str]):
        self.execute_cmd(["file"] + arguments)

    @Slot(list)
    def set_pid_target(self, arguments: List[str]):
        self.execute_cmd(["attach"] + arguments)

    @Slot(list)
    def set_source_dir(self, arguments: List[str]):
        self.execute_cmd(["dir"] + arguments)

    @Slot(list)
    def change_setting(self, arguments: List[str]):
        """Change a setting. Calls 'set' followed by the provided arguments"""
        logging.debug("Changing gdb setting with parameters: %s", arguments)
        gdb.execute("set " + " ".join(arguments))

    @Slot(int)
    def update_stack_lines(self, new_value: int):
        """Set pwndbg's context-stack-lines to a new value"""
        self.change_setting(["context-stack-lines", str(new_value)])
        context_data: List[str] = context_stack(with_banner=False)
        self.update_gui.emit("stack", "\n".join(context_data).encode())
