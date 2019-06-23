processlist = [
    {"name": "Counting", "command": "./testscript.sh", "autostart": False},
    {"name": "Stress", "command": "stress --cpu 1", "autostart": False},
	{"name": "Testit", "command": "/bin/bash -i -c testit", "autostart": False}, # The /bin/bash -i -c is necessary to be able to load aliases from e.g. bashrc
    {"name": "Gedit", "command": "gedit", "autostart": False}
]