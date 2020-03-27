import enum
import hashlib
import requests
import textwrap

from xml.dom.minidom import parseString

base_headers = {
    'User-Agent': '',
    'Accept': '',
    'Content-Type': 'text/xml; charset="utf-8"',
    'SOAPACTION': '"urn:Belkin:service:basicevent:1#{}"'
}


class ActionType(enum.Enum):
    GET_STATE = 'GetBinaryState'
    SET_STATE = 'SetBinaryState'
    GET_NAME = 'GetFriendlyName'


def _gen_req(action: ActionType, value=None):
    action = action.value
    obj_type = action[3:]  # Remove "Get" or "Set" from action

    body = f"""\
    <?xml version="1.0" encoding="utf-8"?>
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
        <s:Body>
            <u:{action} xmlns:u="urn:Belkin:service:basicevent:1">
                <{obj_type}>{'' if value is None else value}</{obj_type}>
            </u:{action}>
        </s:Body>
    </s:Envelope>\
    """

    headers = {**base_headers}
    headers['SOAPACTION'] = headers['SOAPACTION'].format(action)
    return textwrap.dedent(body), headers


def _basic_event(host: str, action: ActionType, value=None):
    data, headers = _gen_req(action, value)
    r = requests.post(
        f'http://{host}/upnp/control/basicevent1',
        headers=headers,
        data=data)
    print(f'{action.value} on {host}: {r.status_code}')
    return parseString(r.text).getElementsByTagName(action.value[3:]).item(0).firstChild.data


def get_device(host: str) -> dict:
    return {
        'device': host,
        'hash': hashlib.sha1(host.encode()).hexdigest()[:16],
        'name': get_name(host),
        'state': get_state(host)
    }


def get_name(host: str) -> str:
    ev = _basic_event(host, ActionType.GET_NAME)
    return ev


def get_state(host: str) -> int:
    ev = _basic_event(host, ActionType.GET_STATE)
    return int(ev)


def set_state(host: str, value: int) -> int:
    ev = _basic_event(host, ActionType.SET_STATE, value)
    return int(ev)
