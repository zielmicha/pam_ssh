import os
import sys
import pwd
import subprocess
import threading
import json
import socket
import pipes
import time

ENVIRON = {'PATH': '/bin:/usr/bin'}
config = json.load(open('config.json'))

open_session_lock = threading.Lock()

def auth_helper(username, token):
    cmd = ['ssh',
           '-o', 'StrictHostKeyChecking=no',
           '-o', 'PubkeyAuthentication=no',
           '-l' + username,
           config['ssh_host'], 'true']
    return run_ssh(cmd, token)

def mount_helper(username, token, pw):
    cmd = ['sshfs', '-f',
           '-o', 'reconnect,workaround=all',
           '-o', 'nonempty,allow_other',
           '-o', 'compression=yes',
           '-o', 'uid=%d,gid=%d' % (
               pw.pw_uid, pw.pw_gid),
           '%s@%s:' % (username, config['ssh_host']),
           pw.pw_dir]
    return run_ssh(cmd, token)

def run_ssh(cmd, token):
    ipipe, opipe = os.pipe()
    cmd = ['sshpass', '-d%d' % ipipe, '--'] + cmd
    proc = subprocess.Popen(cmd,
                            env=ENVIRON,
                            close_fds=False,
                            stdout=sys.stderr)
    os.write(opipe, token + '\n')
    os.close(opipe)
    return proc.wait()

def open_session(user, auth_token):
    pw = pwd.getpwnam(user)
    path = pw.pw_dir

    try:
        os.mkdir(path)
    except OSError:
        pass
    else:
        os.chown(path, pw.pw_uid, pw.pw_gid)

    if not ismount(path):
        f = lambda: mount_helper(user, auth_token, pw)
        threading.Thread(target=f).start()
        wait_for_mount(path)
        subprocess.check_call([
            'mount', '-t', 'tmpfs', 'cache',
            path + '/.cache'
        ])
        return 0
    else:
        return 0

def wait_for_mount(path, timeout=5):
    for i in xrange(10 * timeout):
        if ismount(path):
            return
        time.sleep(0.1)
    raise IOError('not mounted')

def ismount(path):
    for line in open('/proc/mounts'):
        if line.split()[1] == path:
            return True

def auth(user, auth_token):
    return auth_helper(user, auth_token)

def handle(sock):
    f = sock.makefile('r+')
    method, args = json.loads(f.readline())
    code = -1

    if method == 'open_session':
        with open_session_lock:
            code = open_session(**args)
    elif method == 'auth':
        code = auth(**args)

    print 'response', method, code
    f.write(str(code) + '\n')

def loop():
    ADDR = '/var/run/pam_ssh.sock'
    if os.path.exists(ADDR):
        os.remove(ADDR)
    sock = socket.socket(socket.AF_UNIX)
    sock.bind(ADDR)
    os.chmod(ADDR, 0o700)
    sock.listen(2)
    while True:
        child, addr = sock.accept()
        threading.Thread(target=handle, args=[child]).start()
        del child

if __name__ == '__main__':
    loop()
