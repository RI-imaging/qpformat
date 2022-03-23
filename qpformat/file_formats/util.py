import hashlib

import numpy as np


def hash_obj(data, maxlen=5):
    hasher = hashlib.md5()
    tohash = obj2bytes(data)
    hasher.update(tohash)
    return hasher.hexdigest()[:maxlen]


def obj2bytes(data):
    tohash = []
    if isinstance(data, (tuple, list)):
        for item in data:
            tohash.append(obj2bytes(item))
    elif isinstance(data, str):
        tohash.append(data.encode("utf-8"))
    elif isinstance(data, bytes):
        tohash.append(data)
    elif isinstance(data, np.ndarray):
        tohash.append(data.tobytes())
    elif isinstance(data, int):
        tohash.append(bytes(data))
    else:
        msg = "No rule to convert to bytes: {}".format(data)
        raise NotImplementedError(msg)
    return b"".join(tohash)
