## Remotes

Remotes are defined either in the global Tracker configuration file
(`~/.tracker/config.yaml`) or for project specific remotes; in the root of the
project directory (`[...]/tracker.yaml`).

Each remote is named under the `remotes` section key.

```yaml
remotes:
  remote-1:
    ...
  remote-2:
    ...
  remote-n:
    ...
```

### SSH Attributes

| `host` | Server host name or IP address (required string) |
| `port` | Server SSH port (number) By default, port 22 is used for SSH connections. |
| `user` | User used when connecting over SSH (string) By default, the active user name is used for SSH connections. |
| `tracker‑home` | Path to Tracker home on the remote server (string). |
