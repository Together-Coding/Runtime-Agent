from __future__ import annotations

import socket
import json
import asyncio
from enum import Enum
from typing import Dict, Set, Any, Optional
from collections import defaultdict

import paramiko
from paramiko import (
    SSHClient,
    AutoAddPolicy,
)
from paramiko.channel import Channel

from server import sio
from server.utils import ws_session
from server.utils.exceptions import SSHStopRetryException, SSHConnectionException
from server.models import User, ConnectionInfo
from server.websocket import InEvent, OutEvent

MAX_SSH_CONNECTION = 5  # Maximum number of SSH connection per user

# TODO for scalability, save to and load from DB
ssh_clients: Dict[str, Set[SSHWorker]] = defaultdict(set)  # (user-id, ip): {ssh-worker1, ...}


class WorkerStatus(Enum):
    DISCONNECTED = 0
    CONNECTING = 1  # Not used
    CONNECTED = 2


class Reason:
    SSH_AUTH_NOT_SUPPORT = 'Authentication methods `{}` does not supported'
    SSH_TOO_MANY = 'You are trying to connection too many connection'
    SSH_AUTH_FAIL = 'Cannot connect to the SSH server. Authentication failed.'
    SSH_FAIL = 'Cannot connect to the SSH server.'
    SSH_DOWN = 'SSH server down'
    SSH_CHAN_CLOSE = 'SSH channel closed'

    SERVER_DOWN = 'Server down'  # Normally on KeyboardInterrupt
    WS_DISCONNECTED = 'Websocket disconnected'


class SSHWorker:
    """
    The websocket connection from clients can be disconnected unintentionally.
    Thus, it would be more comfortable to users to keep ``SSHWorker`` alive and recycle
    it for the next connection.

    TODO: delete idle instance after n seconds of disconnection, and remove from ssh_clients map.
    """

    BUF_SIZE = 32 * 1024

    def __init__(self, sid: str, connection_info: ConnectionInfo, client: SSHClient):
        self.sid: str = sid
        self.connection_info: ConnectionInfo = connection_info

        self.client: SSHClient = client
        self.channel: Optional[Channel] = None
        self.ssh_retry = 5
        self.set_ssh_channel()

        self.status: WorkerStatus = WorkerStatus.DISCONNECTED
        self.awaitable_recv_client: Optional[asyncio.tasks.Task] = None
        self.awaitable_recv_ssh: Optional[asyncio.tasks.Task] = None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'{self.status}|{self.connection_info}|{self.client}|{self.channel}'

    @property
    def is_connected(self) -> bool:
        return self.status == WorkerStatus.CONNECTED

    @property
    def is_reusable(self) -> bool:
        return self.channel.active and not self.channel.closed

    def destruct(self):
        """ self-destruction """

        self.status = WorkerStatus.DISCONNECTED
        self.channel.close()
        self.client.close()
        self.stop_tasks('destruct')

    def set_ssh_channel(self):
        """
        Create ``paramiko.channel`` instance that might be closed in the middle
        of receiving messages
        """

        if not (self.channel is None or self.channel.closed):
            return

        try:
            self.channel = self.client.invoke_shell()
        except paramiko.SSHException:
            self.cleanup(Reason.SSH_DOWN, True)
            self.ssh_retry -= 1

            if self.ssh_retry < 0:
                raise SSHStopRetryException
            raise IOError

    def setup_recycle(self, sid: str, connection_info: ConnectionInfo):
        """
        setup variables for the next websocket user
        """
        self.sid = sid
        self.connection_info = connection_info
        # self.channel.sendall(b'\f')  # ctrl + l

        # (Workaround) Resize pty in order to show current pty screen.
        # Imagine that user executes `watch -n 1 "date". The next time the user reconnects the pty
        # without resizing, s/he will be shown only changed text not the whole one.
        import random
        self.resize_pty(width=80 + random.randint(0, 10),
                        height=24 + random.randint(0, 10),
                        width_pixels=0,
                        height_pixels=0)

    def resize_pty(self, width: int, height: int,
                   width_pixels: int = 0, height_pixels: int = 0):
        # TODO 유저의 터미널 크기 변경에 대해 적용. 터미널 선택 시에도 호출
        self.channel.resize_pty(width=width,
                                height=height,
                                width_pixels=width_pixels,
                                height_pixels=height_pixels)

    async def run(self):
        """ Run asynchronous tasks """
        self.awaitable_recv_ssh = asyncio.create_task(self.recv_from_ssh())

        try:
            await asyncio.gather(
                self.awaitable_recv_ssh,
            )
        except asyncio.CancelledError:
            return

    def stop_tasks(self, reason):
        """ Stop asynchronous tasks """
        if not self.awaitable_recv_ssh.done():
            self.awaitable_recv_ssh.cancel(reason)

    def sio_accepted(self, sid):
        self.sid = sid
        self.status = WorkerStatus.CONNECTED

    async def cleanup(self, reason: str, send_close: bool):
        if send_close and ws_session.is_connected(self.sid):
            await self._emit(OutEvent.SSH_DOWN, {'type': 'ssh closed', 'message': reason})

        self.status = WorkerStatus.DISCONNECTED

    async def recv_from_client(self, data):
        """
        Receive message from the client(browser) and forward that messages to
        the SSH server
        """

        try:
            # Ensure SSH connection
            self.set_ssh_channel()

            # Send to SSH server
            self.channel.sendall(data)
        except SSHStopRetryException:
            # Stop trying to reconnect SSH
            await self.cleanup(Reason.SSH_DOWN, True)
        except (IOError, socket.error, socket.timeout) as e:
            # SSH connection went wrong
            pass

    async def recv_from_ssh(self):
        """
        Receive message from SSH server and forward that messages to the
        client(browser)
        """

        reason = ''
        send_close = True
        while self.is_connected:
            await asyncio.sleep(0.01)
            try:
                self.set_ssh_channel()

                data = self.channel.recv(self.BUF_SIZE)
                if len(data) <= 0:
                    continue

                await self._emit(OutEvent.SSH_RELAY, data)
            except KeyboardInterrupt:
                reason = Reason.SERVER_DOWN
                break
            except (OSError, IOError):
                # including socket.timeout
                continue
            except SSHStopRetryException:
                reason = Reason.SSH_DOWN
                break
            except:
                reason = 'Unknown error'
                break

        await self.cleanup(reason, send_close)

    async def _emit(self, event: str, data: Any):
        await sio.emit(event, data, room=self.sid)


def ssh_connect(
    sid: str,
    user: User,
    hostname: str,
    username: str,
    auth_type: str,
    auth: str,
    port: int = 22
) -> SSHWorker:
    """
    Connect with SSH server running in the local machine, that is to run user's
    code.

    :param str sid: socket.io session ID
    :param User user: client data
    :param str hostname: SSH hostname (i.e IP address)
    :param str username: SSH username
    :param str auth_type: SSH authentication method (ex. password)
    :param str auth: SSH authentication payload (ex. raw password)
    :param int port: SSH port
    :return:
    """
    if auth_type != 'password':
        raise SSHConnectionException(Reason.SSH_AUTH_NOT_SUPPORT.format(auth_type))

    if len(ssh_clients[str(user)]) > MAX_SSH_CONNECTION:
        raise SSHConnectionException(Reason.SSH_TOO_MANY)

    # When there is already connected ssh client disconnected with the user,
    # reuse that ssh client.
    connection_info = ConnectionInfo(user=user, ssh_user=username,
                                     src=user.ip, dest=hostname,
                                     port=port)

    for worker in ssh_clients[connection_info.key].copy():
        if worker.status == WorkerStatus.DISCONNECTED:
            if worker.is_reusable:
                worker.setup_recycle(sid, connection_info)
                worker.sio_accepted(sid)
                return worker
            else:
                # Don't need to reuse the worker because of broken channel.
                worker.destruct()
                ssh_clients[connection_info.key].remove(worker)
                del worker

    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy)

    try:
        client.connect(hostname=hostname,
                       username=username,
                       password=auth,
                       port=port,
                       compress=True,
                       )

    except paramiko.AuthenticationException:
        raise SSHConnectionException(Reason.SSH_AUTH_FAIL)
    except Exception as e:
        raise SSHConnectionException(Reason.SSH_FAIL)

    ssh_worker = SSHWorker(sid, connection_info, client)
    ssh_worker.channel.settimeout(0)

    ssh_clients[connection_info.key].add(ssh_worker)
    return ssh_worker
