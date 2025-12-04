# config.py
"""
Basic configuration for the Catch-and-Log honeypot.
Adjust ports and banners here if you need to.
"""

# Where logs go
LOG_DIR = "logs"
LOG_FILE = LOG_DIR + "/events.jsonl"

# Network settings
BIND_ADDR = "0.0.0.0"   # listen on all interfaces

TELNET_PORT = 2323      # high port so you don't need root
HTTP_PORT = 8080        # fake HTTP / admin page

# Telnet / SSH-like messages
TELNET_BANNER = (
    "Welcome to Embedded Device OS v1.0\r\n"
    "Unauthorized access is prohibited.\r\n\r\n"
)

TELNET_LOGIN_PROMPT = "login: "
TELNET_PASSWORD_PROMPT = "Password: "
TELNET_LOGIN_FAIL = "Login incorrect\r\n"
TELNET_WELCOME_MSG = (
    "Last login: Thu Jan  1 00:00:00 1970 from console\r\n"
    "Type 'help' for a list of commands. Type 'exit' to disconnect.\r\n"
)

TELNET_SHELL_PROMPT = "device$ "

