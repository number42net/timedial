"""TimeDial project.

Copyright (c) Martin Miedema
Repository: https://github.com/number42net/timedial

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import os
import socket
import threading
import time

parser = argparse.ArgumentParser(description="Emulate a slow serial connection with configurable settings.")
parser.add_argument("--host", "-H", type=str, default="localhost", help="Remote host to connect to (default: localhost)")
parser.add_argument("--lport", "-L", type=int, default=2323, help="Local TCP port to listen on (default: 2323)")
parser.add_argument("--rport", "-R", type=int, default=23, help="Remote port to connect to (default: 23)")
parser.add_argument("--baud", "-b", type=int, default=2400, help="Baud rate for serial emulation (default: 2400)")
parser.add_argument("--socket", "-u", type=str, default=None, help="Path to a Unix socket file to listen on")

args = parser.parse_args()


def throttle_relay(src: socket.socket, dst: socket.socket, baud: int, direction: str) -> None:
    """Relays data from one socket to another with throttling to simulate baud rate.

    Args:
        src (socket.socket): Source socket to read from.
        dst (socket.socket): Destination socket to send to.
        baud (int): Baud rate for throttling.
        direction (str): String label for the direction of relay (e.g., 'TX' or 'RX').
    """
    try:
        while True:
            data: bytes = src.recv(1)
            if not data:
                break
            dst.sendall(data)
            time.sleep(1 / (baud // 10))
    except (ConnectionResetError, BrokenPipeError):
        pass
    finally:
        try:
            dst.shutdown(socket.SHUT_WR)
        except OSError:
            pass


def handle_client(client_sock: socket.socket, args: argparse.Namespace) -> None:
    """Handles a new client connection by creating a remote connection and relaying data.

    Args:
        client_sock (socket.socket): Client socket connected to the emulator.
        args (argparse.Namespace): Parsed command-line arguments containing relay settings.
    """
    try:
        remote_sock: socket.socket = socket.create_connection((args.host, args.rport))
        print(f"Connected to remote {args.host}:{args.rport}")
        threading.Thread(target=throttle_relay, args=(client_sock, remote_sock, args.baud, "TX"), daemon=True).start()
        throttle_relay(remote_sock, client_sock, args.baud, "RX")
    finally:
        client_sock.close()


def start_tcp_server(args: argparse.Namespace) -> None:
    """Starts a TCP server to listen for incoming client connections.

    Args:
        args (argparse.Namespace): Parsed command-line arguments including port and baud rate.
    """
    server_sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("127.0.0.1", args.lport))
    server_sock.listen(5)
    print(f"[TCP] Listening on 127.0.0.1:{args.lport} at {args.baud} baud")

    def loop() -> None:
        while True:
            client_sock, addr = server_sock.accept()
            print(f"[TCP] Emulator connected from {addr}")
            threading.Thread(target=handle_client, args=(client_sock, args), daemon=True).start()

    threading.Thread(target=loop, daemon=True).start()


def start_socket_server(args: argparse.Namespace) -> None:
    """Starts a Unix domain socket server to emulate serial communication.

    Args:
        args (argparse.Namespace): Parsed command-line arguments including socket path and baud rate.
    """
    path = args.socket
    if os.path.exists(path):
        os.remove(path)

    unix_sock: socket.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    unix_sock.bind(path)
    unix_sock.listen(5)
    print(f"[UNIX] Listening on {path} at {args.baud} baud")

    def loop() -> None:
        while True:
            client_sock, _ = unix_sock.accept()
            print("[UNIX] Emulator connected")
            threading.Thread(target=handle_client, args=(client_sock, args), daemon=True).start()

    threading.Thread(target=loop, daemon=True).start()


def main() -> None:
    """Main entry point for the serial emulator.

    Starts TCP and optionally Unix socket servers based on arguments,
    and runs indefinitely until interrupted.
    """
    start_tcp_server(args)
    if args.socket:
        start_socket_server(args)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        if args.socket and os.path.exists(args.socket):
            os.remove(args.socket)


if __name__ == "__main__":
    main()
