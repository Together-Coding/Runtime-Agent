import hashlib
from dataclasses import dataclass


@dataclass
class User:
    user_id: int
    ip: str

    @property
    def key(self):
        md5 = hashlib.md5()
        md5.update(f'{self.user_id}{self.ip}'.encode())
        return md5.hexdigest()


@dataclass
class ConnectionInfo:
    user: User
    src: str  # user IP. Normally same with User.ip
    dest: str  # SSH hostname
    ssh_user: str
    port: int

    @property
    def key(self):
        md5 = hashlib.md5()
        md5.update(f'{self.user.key}{self.src}{self.dest}{self.ssh_user}{self.port}'.encode())
        return md5.hexdigest()

    def __str__(self):
        return f'<ConnectionInfo {self.user.user_id}, {self.src} to {self.ssh_user}@{self.dest}:{self.port}>'
