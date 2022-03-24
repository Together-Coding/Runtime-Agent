import subprocess
from subprocess import TimeoutExpired
from typing import Optional

from server.utils.etc import rand_string
import configs


def change_password() -> Optional[str]:
    """
    Change OS user's password.
    When None is returned, the client must re-call this function
    """

    cmd = ['/usr/bin/passwd', configs.USERNAME]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    pw = rand_string(32)
    p.stdin.write(f'{pw}\n{pw}\n'.encode())
    p.stdin.flush()

    try:
        # Wait 5 seconds until process is over
        p.wait(5)
        print(p.returncode)
    except TimeoutExpired:
        p.kill()
        return None

    return pw
