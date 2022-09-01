"""eois sequence functions"""

import json
from urllib import request

# import requests


def result_eois(seq: int) -> list[int]:
    """https://oeis.org/search?fmt=<json|text>&q=id:A<sequenceNumber>"""
    with request.urlopen(
        f"https://oeis.org/search?fmt=json&q=id:A{seq:-06d}&start=1"
    ) as res:
        data = json.loads(res.read().decode())
        results = data["results"]
        if len(results) != 1:
            raise KeyError
        print(f"{len(results)} results")
        result = results[0]
        print(result["data"])
        data = result["data"]
    return data
