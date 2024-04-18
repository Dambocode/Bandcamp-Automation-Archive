import os
import json


def logResponse(name, response, body_type="json"):
    """
    Logs the response from the server.
    """
    try:
        os.mkdir(name)
    except FileExistsError:
        pass
    with open(name + "/headers" + ".json", "w+") as f:
        json.dump(response.text, f, indent=4)
    with open(name + "/body" + f".{body_type}", "w+") as f:
        if body_type == "json":
            json.dump(response.text, f, indent=4)
        else:
            f.write(response.text)

    return response
