import base64
import hashlib
import hmac
from collections import OrderedDict
from hashlib import sha256
from urllib import parse


def hex_encode_md5_hash(data):
    if not data:
        data = "".encode("utf-8")
    else:
        data = data.encode("utf-8")
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()


def get_signature(method: str, url: str, ak: str, sk: str, params: dict):
    """
    计算签名
    :param url: 签名url地址，如 /api/test
    :param ak: access_key_id
    :param sk:  secure_key
    :param params: url 中参数
    :param method: method GET POST PUT DELETE
    :return: 添加签名后的 url
    """

    url += "/" if not url.endswith("/") else ""
    params["access_key_id"] = ak
    sorted_param = OrderedDict()
    keys = sorted(params.keys())
    for key in keys:
        if isinstance(params[key], list):
            sorted_param[key] = sorted(params[key])
        else:
            sorted_param[key] = params[key]

    url_param = parse.urlencode(sorted_param, safe='/', quote_via=parse.quote, doseq=True)
    string_to_sign = method + "\n" + url + "\n" + url_param + "\n" + hex_encode_md5_hash("")

    h = hmac.new(sk.encode(encoding="utf-8"), digestmod=sha256)
    h.update(string_to_sign.encode(encoding="utf-8"))
    sign = base64.b64encode(h.digest()).strip()
    signature = parse.quote_plus(sign.decode())
    signature = parse.quote_plus(signature)
    url_param += "&signature=%s" % signature
    return url_param
