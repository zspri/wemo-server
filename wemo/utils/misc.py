

def find_host_by_hash(devices: list, d_hash: str):
    matches = [d for d in devices if d['hash'] == d_hash]
    if len(matches) > 0:
        return matches[0]
    return None


def force_update_devices(devices: list, d_hash: str, new_state: int) -> list:
    for device in devices:
        if device['hash'] == d_hash:
            device['state'] = new_state
    return devices
