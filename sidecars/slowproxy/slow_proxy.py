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

import socket
import threading
import time

HOST = "timedial"


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


def handle_client(client_sock: socket.socket, rport: int, baud: int) -> None:
    """Handles a new client connection by creating a remote connection and relaying data.

    Args:
        client_sock (socket.socket): Client socket connected to the emulator.
        rport: Remote TCP port
        baud: Baud rate
    """
    try:
        remote_sock: socket.socket = socket.create_connection((HOST, rport))
        print(f"Connected to remote {HOST}:{rport}")
        threading.Thread(target=throttle_relay, args=(client_sock, remote_sock, baud, "TX"), daemon=True).start()
        throttle_relay(remote_sock, client_sock, baud, "RX")
    finally:
        client_sock.close()


def start_tcp_server(lport: int, rport: int, baud: int) -> None:
    """Starts a TCP server to listen for incoming client connections.

    Args:
        lport: Local TCP port
        rport: Remote TCP port
        baud: Baud rate
    """
    server_sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("0.0.0.0", lport))
    server_sock.listen(5)
    print(f"[TCP] Listening on 0.0.0.0:{lport} at {baud} baud")

    def loop() -> None:
        while True:
            client_sock, addr = server_sock.accept()
            print(f"[TCP] Emulator connected from {addr}")
            threading.Thread(target=handle_client, args=(client_sock, rport, baud), daemon=True).start()

    threading.Thread(target=loop, daemon=True).start()


def main() -> None:
    """Main entry point for the serial emulator."""
    start_tcp_server(lport=1223, rport=23, baud=1200)
    # start_tcp_server(lport=1224, rport=24, baud=1200)

    start_tcp_server(lport=2423, rport=23, baud=2400)
    # start_tcp_server(lport=2424, rport=24, baud=2400)

    start_tcp_server(lport=9623, rport=23, baud=9600)
    # start_tcp_server(lport=9624, rport=24, baud=9600)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down.")


if __name__ == "__main__":
    main()
