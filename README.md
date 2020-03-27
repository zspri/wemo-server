# wemo-server

A Flask server to find manage Belkin WeMo smart switches

## Requirements

- Python 3.8
- All requirements in requirements.txt
- Valid environment variables
 - `DEFAULT_AUTH_KEY`
 - `NET_SPACE`

The server periodically scans the addresses in `NET_SPACE` to find any devices
that respond to port 49153. Worker code is modified from
[iancmcc/ouimeaux](https://github.com/iancmcc/ouimeaux/blob/develop/client.py).

## Endpoints

By default, the server runs on port 80 and binds to any address.

Note: an Authorization header must be provided, with the content matching
`DEFAULT_AUTH_KEY`.

### GET `/devices`

Get details on all discovered devices.

Example response:
```json
{
    "_last_update": 1585269342.533981,
    "devices": [
        {
            "device": "192.168.0.12:49153",
            "hash": "431e98acb8e7e5e8",
            "name": "Desk Lamp",
            "state": 1
        },
        {
            "device": "192.168.0.19:49153",
            "hash": "5e09949a6ee030e3",
            "name": "Bedroom Lamp",
            "state": 1
        }
    ]
}
```

### GET `/devices/:hash`

Get details on a specific WeMo device.

Example response: `/devices/431e98acb8e7e5e8`
```json
{
    "device": "192.168.0.12:49153",
    "hash": "431e98acb8e7e5e8",
    "name": "Desk Lamp",
    "state": 1
}
```

### PATCH `/devices/:hash`

Turn a WeMo device on or off. Requires a "state" parameter that must be
either 0 or 1, representing the state that the switch should be changed to.

Example response: `/devices/431e98acb8e7e5e8?state=0`
```json
{
  "state": 0
}
```
