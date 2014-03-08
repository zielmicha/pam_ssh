pam_ssh
=======

Use SSH server to authenticate and provide /home directory for Linux client.

Installation
----------

```
cp pam_ssh.py /lib/security
```

Add to `/etc/pam.d/common-auth`:

```
auth  sufficient       pam_python.so pam_ssh.py use_first_pass
```

Add to `/etc/pam.d/common-session`:

```
session    requisite       pam_python.so pam_ssh.py
```

Customize config:

```
cp config.json.example config.json
nano config.json
```

Usage
----------

Start daemon:

```
python daemon.py
```