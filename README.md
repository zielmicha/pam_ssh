pam_ssh
=======

Use SSH server to authenticate and provide /home directory for Linux client.

## Installation

```
cp pam_ssh.py /lib/security/
```

Customize config:

```
cp config.json.example config.json
nano config.json
```

### Debian/Ubuntu

```
cp ssh /usr/share/pam-configs/
pam-auth-update
```

### Non-Debian systems

Add to `/etc/pam.d/common-auth`:

```
auth  sufficient       pam_python.so pam_ssh.py use_first_pass
```

Add to `/etc/pam.d/common-session`:

```
session    requisite       pam_python.so pam_ssh.py
```

Usage
----------

Start daemon:

```
python daemon.py
```
