import json
'''
-----------------------------------------------------------
Turn a string repr of json into dictionary object
-----------------------------------------------------------
Parameters:
    text: str
Returns:
    dictionary object of string
-----------------------------------------------------------
'''
def str_to_json(text: str) -> dict:
    text = text.replace("\n", " ")
    return json.loads(text)

