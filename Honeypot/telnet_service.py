# telnet_service.py
import socket
import threading
import time

import config
import logger


def _recv_line(conn, max_len=128, timeout=30.0):
    """
    Read bytes from the socket until newline or max_len.
    Returns a decoded string without \r\n.
    """
    conn.settimeout(timeout)
    data = b""
    try:
        while b"\n" not in data and len(data) < max_len:
            chunk = conn.recv(1)
            if not chunk:
                break
            data += chunk
    except (socket.timeout, ConnectionError):
        return ""

    return data.strip(b"\r\n").decode(errors="replace")


def _handle_shell(conn, src_ip, src_port, start_ts):
    """
    Simple fake shell loop: log commands and send canned responses.
    """
    conn.sendall(config.TELNET_WELCOME_MSG.encode())

    while True:
        try:
            conn.sendall(config.TELNET_SHELL_PROMPT.encode())
            cmd = _recv_line(conn)
        except ConnectionError:
            break

        if not cmd:
            break

        logger.log_event(
            "command",
            service="telnet",
            src_ip=src_ip,
            src_port=src_port,
            dst_port=config.TELNET_PORT,
            command=cmd,
        )

        cmd_lower = cmd.strip().lower()

        if cmd_lower in ("exit", "logout", "quit"):
            conn.sendall(b"logout\r\n")
            break
        elif cmd_lower == "help":
            msg = (
                "Available commands: help, ls, uname, whoami, exit\r\n"
            )
            conn.sendall(msg.encode())
        elif cmd_lower == "ls":
            # Fake directory listing
            msg = "bin  etc  tmp  var  home  config.txt\r\n"
            conn.sendall(msg.encode())
        elif cmd_lower == "uname":
            msg = "Linux embedded-device 3.2.0-4-686-pae i686\r\n"
            conn.sendall(msg.encode())
        elif cmd_lower == "whoami":
            msg = "root\r\n"
            conn.sendall(msg.encode())
        else:
            msg = f"{cmd}: command not found\r\n"
            conn.sendall(msg.encode())

    # session end
    duration = time.time() - start_ts
    logger.log_event(
        "session_closed",
        service="telnet",
        src_ip=src_ip,
        src_port=src_port,
        dst_port=config.TELNET_PORT,
        duration_seconds=duration,
    )


def _handle_client(conn, addr):
    src_ip, src_port = addr
    start_ts = time.time()

    logger.log_event(
        "connection_opened",
        service="telnet",
        src_ip=src_ip,
        src_port=src_port,
        dst_port=config.TELNET_PORT,
    )

    try:
        # Banner + login
        conn.sendall(config.TELNET_BANNER.encode())
        conn.sendall(config.TELNET_LOGIN_PROMPT.encode())
        username = _recv_line(conn)

        conn.sendall(config.TELNET_PASSWORD_PROMPT.encode())
        password = _recv_line(conn)

        logger.log_event(
            "login_attempt",
            service="telnet",
            src_ip=src_ip,
            src_port=src_port,
            dst_port=config.TELNET_PORT,
            username=username,
            password=password,
            success=False,  # always false; we never really log in
        )

        # Pretend login failed but still drop them into a shell
        conn.sendall(config.TELNET_LOGIN_FAIL.encode())

        _handle_shell(conn, src_ip, src_port, start_ts)

    except ConnectionError:
        # connection dropped abruptly
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


def run_telnet_service():
    """
    Main loop: bind to TELNET_PORT and spawn a thread for each connection.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((config.BIND_ADDR, config.TELNET_PORT))
    sock.listen(5)

    logger.log_event(
        "service_started",
        service="telnet",
        port=config.TELNET_PORT,
        bind_addr=config.BIND_ADDR,
    )

    print(f"[telnet] listening on {config.BIND_ADDR}:{config.TELNET_PORT}")

    try:
        while True:
            conn, addr = sock.accept()
            t = threading.Thread(target=_handle_client, args=(conn, addr), daemon=True)
            t.start()
    finally:
        sock.close()

