import time
import asyncio
from pathlib import Path
import subprocess
import arrow
from aiogram import Bot
from aiogram.types import Message, BufferedInputFile
from watchdog.observers import Observer
from watchdog.events import (
    FileSystemMovedEvent,
    FileSystemEventHandler,
    FileSystemEvent,
)
from local import local
from log import logger


class TGFilesystemMonitor:
    def __init__(
        self, bot_token: str, server_name: str, timezone: str, lang: str = "en"
    ) -> None:
        """
        The main class, which includes monitoring the file system with subsequent
        collection of a report and sending it via a Telegram bot.

        :param bot_token: Telegram Bot token `Obtained from @BotFather <https://t.me/BotFather>`
        :param server_name: Server name for identification
        :param lang: Script language
        """
        logger.debug("Initialization TGFilesystemMonitor")
        self.bot = Bot(bot_token)
        self.server_name = server_name
        self.lang = lang
        self._loop = asyncio.new_event_loop()
        self.observer = Observer()
        self.timezone = timezone
        logger.debug("TGFilesystemMonitor initialization completed")

    def __del__(self) -> None:
        """
        Delete class with closing bot session
        """

        self._loop.run_until_complete(self.bot.session.close())

    def _gen_filename(self, extension: str = "txt") -> str:
        """
        Generate filename string

        :param extension: Extension for filename string
        """

        time = arrow.utcnow().to(self.timezone)
        timestamp = time.int_timestamp
        return f"report_{self.server_name}_{time.format('YYYY-MM-DD-HH-mm-ss')}_{timestamp}.{extension}"

    def report(self, chat_id: int | str, caption: str | None = None) -> Message:
        """
        Generate and send report to chat via Telegram bot

        :param chat_id: Telegram chat for sending notification
        :param caption: Caption for notification
        """

        logger.debug("REPORT: Report collection started")
        # Set date and time report
        buffer = local[self.lang]["time"]
        time = arrow.utcnow().to(self.timezone).strftime("%A, %d %B %Y %H:%M:%S %z")
        logger.trace(f"REPORT: Current time:\n{time}")
        buffer += f"{time}\n\n\n"

        # Set caption (triggered event)
        if caption:
            logger.trace(f"REPORT: Triggered event:\n{caption}")
            buffer += f"{local[self.lang]['event']}{caption}\n\n"

        # Run command w
        output_w = subprocess.check_output(["w"]).decode()
        logger.trace(f"REPORT: Output command w:\n{output_w}")
        buffer += f"{local[self.lang]['command_w']}{output_w}\n\n"

        # Run command who
        output_who = subprocess.check_output(["who"]).decode()
        logger.trace(f"REPORT: Output command who:\n{output_who}")
        buffer += f"{local[self.lang]['command_who']}{output_who}\n\n"

        # Run command lastlog
        output_lastlog = subprocess.check_output(["lastlog"]).decode()
        logger.trace(f"REPORT: Output command lastlog:\n{output_lastlog}")
        buffer += f"{local[self.lang]['command_lastlog']}{output_lastlog}\n\n"

        # Run command last
        output_last = subprocess.check_output(["last"]).decode()
        buffer += f"{local[self.lang]['command_last']}{output_last}\n\n"

        # Read auth.log
        output_auth_log = subprocess.check_output(
            [
                "grep",
                "-Ei",
                "-A",
                "5",
                "-B",
                "5",
                "-e",
                "(ssh).*(session opened)",
                "/var/log/auth.log",
            ]
        ).decode()
        logger.trace(f"REPORT: Output auth.log file:\n{output_auth_log}")
        buffer += f"{local[self.lang]['file_auth']}{output_auth_log}\n\n"

        # Run command ss -tua
        output_ss = subprocess.check_output(["ss", "-tua"]).decode()
        logger.trace(f"REPORT: Output command ss:\n{output_ss}")
        buffer += f"{local[self.lang]['command_ss']}{output_ss}\n\n"

        # Run command ps aux --sort=-pid | grep -v ]$
        output_ps = subprocess.check_output(
            "ps aux --sort=-pid | grep -v ]$", shell=True
        ).decode()
        logger.trace(f"REPORT: Output command ps:\n{output_ps}")
        buffer += f"{local[self.lang]['command_ps']}{output_ps}\n\n"

        # Run command free -h
        output_free = subprocess.check_output(["free", "-h"]).decode()
        logger.trace(f"REPORT: Output command free:\n{output_free}")
        buffer += f"{local[self.lang]['command_free']}{output_free}\n\n"

        logger.debug("REPORT: Report collection completed")
        logger.debug("REPORT: Sending report to chat")
        message = self._loop.run_until_complete(
            self.bot.send_document(
                chat_id,
                BufferedInputFile(buffer.encode(), self._gen_filename()),
                caption=caption,
            )
        )
        logger.debug("REPORT: Report sent to chat")
        return message

    def start_monitor(self, monitor_path: Path, chat_id: int | str):
        logger.debug("MONITOR: Creating event handler")
        event_handler = TGFilesystemMonitorHandler(self, chat_id)
        self.observer.schedule(event_handler, monitor_path, True)
        logger.debug("MONITOR: Starting monitor")
        self.observer.start()
        logger.debug("MONITOR: Monitor started")
        try:
            while True:
                time.sleep(60 * 60)
        except KeyboardInterrupt:
            logger.debug("MONITOR: Catched KeyboardInterrupt. Stopping monitor")
            self.observer.stop()
            self.observer.unschedule_all()
        self.observer.join()
        logger.debug("MONITOR: Monitor stopped")


class TGFilesystemMonitorHandler(FileSystemEventHandler):
    def __init__(
        self, tgfsm: TGFilesystemMonitor, chat_id: int | str, *args, **kwargs
    ) -> None:
        """
        Custom FileSystemEventHandler which catch file system events and send
        a report

        :param tgfsm: instance of class TGFilesystemMonitor
        :param chat_id: Telegram chat for sending notification
        """

        self._tgfsm = tgfsm
        self.chat_id = chat_id
        super().__init__(*args, **kwargs)

    def on_any_event(self, event: FileSystemMovedEvent):
        logger.debug(f"MONITOR: Catched new file system event: {event}")
        match event.event_type:
            case "created":
                event_text = local[self._tgfsm.lang][f"event_{event.event_type}"]
                event_text = event_text.format(path=event.src_path)
            case "deleted":
                event_text = local[self._tgfsm.lang][f"event_{event.event_type}"]
                event_text = event_text.format(path=event.src_path)
            case "modified":
                event_text = local[self._tgfsm.lang][f"event_{event.event_type}"]
                event_text = event_text.format(path=event.src_path)
            case "moved":
                event_text = local[self._tgfsm.lang][f"event_{event.event_type}"]
                event_text = event_text.format(
                    src_path=event.src_path, dest_path=event.dest_path
                )
        logger.debug("MONITOR: Running a report due to an event")
        self._tgfsm.report(self.chat_id, event_text)
        logger.debug("MONITOR: The report was completed successfully")
