import os
import sys
import pwd
import socket
import json

auth_token = None

def rpc(name, args):
    sock = socket.socket(socket.AF_UNIX)
    sock.connect('/var/run/pam_ssh.sock')
    f = sock.makefile('r+')
    f.write(json.dumps([name, args]) + '\n')
    f.flush()
    resp = int(f.readline())
    return resp

def pam_sm_authenticate(pamh, flags, argv):
    global auth_token

    username = pamh.get_user()
    pw = pwd.getpwnam(username)
    if pw.pw_uid < 1000:
        return pamh.PAM_AUTH_ERR

    assert username == 'zlmch'
    auth_token = pamh.authtok
    if len(auth_token) > 1024:
        return pamh.PAM_AUTH_ERR

    if not auth_token:
        return pamh.PAM_AUTH_ERR

    code = rpc('auth', dict(user=username, auth_token=auth_token))

    if code == 0:
        return pamh.PAM_SUCCESS
    else:
        return pamh.PAM_AUTH_ERR

def pam_sm_setcred(pamh, flags, argv):
    return pamh.PAM_SUCCESS

def pam_sm_acct_mgmt(pamh, flags, argv):
    return pamh.PAM_SUCCESS

def pam_sm_open_session(pamh, flags, argv):
    user = pamh.get_user()
    pw = pwd.getpwnam(user)
    token = auth_token

    if pw.pw_uid < 1000:
        return pamh.PAM_SUCCESS

    code = rpc('open_session', dict(user=user,
                                    auth_token=auth_token))

    if code == 0:
        return pamh.PAM_SUCCESS
    else:
        return pamh.PAM_AUTH_ERR

def pam_sm_close_session(pamh, flags, argv):
    return pamh.PAM_SUCCESS

def pam_sm_chauthtok(pamh, flags, argv):
    return pamh.PAM_SUCCESS
