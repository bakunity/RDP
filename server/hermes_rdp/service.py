from __future__ import annotations

import logging
import signal
import threading

from .api import create_api_server
from .bot import TelegramBot
from .config import load_config
from .db import Registry


LOG = logging.getLogger("hermes_rdp")


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    config = load_config()
    registry = Registry(
        config.db_path,
        config.port_start,
        config.port_end,
        config.command_timeout_seconds,
    )
    api_server = create_api_server(config, registry)
    bot = TelegramBot(config, registry)

    api_thread = threading.Thread(target=api_server.serve_forever, daemon=True)
    bot_thread = threading.Thread(target=bot.run, daemon=True)
    api_thread.start()
    bot_thread.start()

    stop_event = threading.Event()

    def stop_handler(signum, frame):
        LOG.info("received signal %s", signum)
        stop_event.set()

    signal.signal(signal.SIGTERM, stop_handler)
    signal.signal(signal.SIGINT, stop_handler)
    LOG.info("Hermes RDP started on HTTPS port %s", config.api_port)
    stop_event.wait()
    bot.stop()
    api_server.shutdown()
    api_server.server_close()


if __name__ == "__main__":
    main()
