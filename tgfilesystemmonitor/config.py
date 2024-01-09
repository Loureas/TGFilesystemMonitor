"""
Read environment variables, arguments and
write values to immutable read-only Config class
"""
import os
from argparse import ArgumentParser
from pathlib import Path
from dataclasses import dataclass
from types import NoneType
from environs import Env

env = Env()
env.read_env()

args_parser = ArgumentParser(
    description=(
        "A script that monitors file system events and sends a report "
        "via Telegram (Available only on Unix-like systems)"
    ),
)
args_parser.add_argument(
    "servername", type=str, help="(required) -- server name for identification"
)
args_parser.add_argument(
    "chatid",
    type=str,
    help="(required) -- Telegram chat for sending notifications (username or id)",
)
args_parser.add_argument(
    "action",
    type=str,
    choices=("monitor", "report", "report-remote-auth"),
    help=(
        "(required) -- script operation mode: "
        "monitor - mode for monitoring file system events, "
        "report - sending a report via a Telegram bot with subsequent exit from the script, "
        "report-remote-auth - Reporting with remote authentication (designed for pam)"
    ),
)
args_parser.add_argument(
    "--monitor-path",
    type=Path,
    help='-- directory or file for monitor (required for action "monitor")',
)
args_parser.add_argument(
    "--log-path",
    type=Path,
    default=os.path.join(os.path.abspath(os.path.dirname(__file__)), "logs"),
    help="-- path to the directory with logging files (default: script directory)",
)
args_parser.add_argument(
    "--lang",
    type=str,
    choices=("en", "ru"),
    default="en",
    help='-- script language (default: "en")',
)
args_parser.add_argument(
    "--timezone",
    type=str,
    default="+00:00",
    help='-- timezone (default: "+00:00"). Example: +07:00, US/Pacific',
)
args_parser.add_argument(
    "--bot-token",
    type=str,
    help=(
        '-- bot token, otherwise read environment variable "TGFSM_BOT_TOKEN" '
        "(DO NOT USE IN INTERACTIVE SHELL!)"
    ),
)
args_parser.add_argument(
    "--log-level",
    type=str,
    choices=("TRACE", "DEBUG", "INFO"),
    default="INFO",
    help='-- minimal logging level (default: "INFO"): TRACE, DEBUG, INFO',
)
opts = args_parser.parse_args()
if opts.action == "monitor" and isinstance(opts.monitor_path, NoneType):
    args_parser.error('action "monitor" requires --monitor-path')
if opts.bot_token:
    bot_token = opts.bot_token
else:
    bot_token = env.str("TGFSM_BOT_TOKEN")


@dataclass(frozen=True)  # Make variables read-only
class Config:
    """
    Configuration class which includes configuration values

    :param bot_token: Telegram Bot token `Obtained from @BotFather <https://t.me/BotFather>`
    :param server_name: Server name for identification
    :param log_path: Path to the directory with logging files
    :param monitor_path: directory or file for monitor
    :param lang: Script language
    :param chat_id: Telegram chat for sending notifications
    :param action: Script operation mode
    :param timezone: Timezone
    :param pam_user: Logged user from PAM
    :param pam_rhost: Remote host from PAM
    :param log_level: Minimal logging level
    """

    bot_token: str = bot_token
    server_name: str = opts.servername
    log_path: Path = opts.log_path
    monitor_path: Path = opts.monitor_path
    lang: str = opts.lang
    chat_id: int | str = opts.chatid
    action: str = opts.action
    timezone: str = opts.timezone
    pam_user: str | None = env.str("PAM_USER", None)
    pam_rhost: str | None = env.str("PAM_RHOST", None)
    log_level: str = opts.log_level


config = Config()
