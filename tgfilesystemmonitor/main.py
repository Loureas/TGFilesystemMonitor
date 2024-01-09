import asyncio
import aiohttp
from __about__ import __version__, __description__, __authors__, __license__
from log import logger
from tgfsm import TGFilesystemMonitor, TGFilesystemMonitorHandler
from local import local

if __name__ == "__main__":
    from config import config

    logger.info(
        f"=== WELCOME TO THE TGFILESYSTEMMONITOR SCRIPT! VERSION {__version__} ==="
    )
    logger.info(f"=== {__description__} ===")
    logger.info(f"=== LICENSE: {__license__} ===")
    logger.info(f"=== AUTHORS: {', '.join(__authors__)} ===")
    tgfsm = TGFilesystemMonitor(
        config.bot_token, config.server_name, config.timezone, config.lang
    )
    logger.info(f'Received action "{config.action}"')
    match config.action:
        case "report":
            logger.info("Generating and sending report")
            tgfsm.report(config.chat_id)
            logger.success("Report has been sent successfully")
        case "monitor":
            logger.info("Starting monitor")
            tgfsm.start_monitor(config.monitor_path, config.chat_id)
        case "report-remote-auth":
            logger.info("Getting information about IP address")
            ip_address = config.pam_rhost
            user = config.pam_user
            loop = asyncio.get_event_loop()
            url = "https://ipinfo.io/"
            logger.debug(f"HTTP: Sending GET request to {url}")
            session = aiohttp.ClientSession()
            response = loop.run_until_complete(
                session.get(f"{url}{ip_address}", headers={"User-Agent": "curl/7.72.0"})
            )
            response = loop.run_until_complete(response.json())
            loop.run_until_complete(session.close())
            logger.debug("HTTP: Response received")
            logger.trace(f"HTTP: Response:\n{response}")
            logger.info("Information about IP address has been received successfully")
            logger.info("Generating and sending report")
            caption = local[config.lang]["event_auth"].format(
                server_name=config.server_name,
                user=user,
                src_ip=ip_address,
                src_hostname=response["hostname"],
                src_country=response["country"],
                src_region=response["region"],
                src_city=response["city"],
                src_zip_code=response["postal"],
                src_coordinates=response["loc"],
                src_provider=response["org"],
                src_timezone=response["timezone"],
            )
            tgfsm.report(config.chat_id, caption)
            logger.success("Report has been sent successfully")
    logger.info("Exit...")
