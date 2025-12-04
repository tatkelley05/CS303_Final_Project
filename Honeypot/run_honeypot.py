# run_honeypot.py
import threading
import time

import logger
import telnet_service
import http_service


def main():
    logger.log_event("honeypot_started")

    telnet_thread = threading.Thread(
        target=telnet_service.run_telnet_service,
        daemon=True,
    )
    http_thread = threading.Thread(
        target=http_service.run_http_service,
        daemon=True,
    )

    telnet_thread.start()
    http_thread.start()

    print("[main] Catch-and-Log honeypot running.")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\n[main] Shutting down honeypot...")
        logger.log_event("honeypot_stopped")


if __name__ == "__main__":
    main()

