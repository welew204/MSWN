from pprint import pprint
from collections import defaultdict

def schema_factory():
    return {"dictionary": 1}

funtimez = defaultdict(schema_factory)

pprint(funtimez)

funtimez[1]
funtimez["farts"]

pprint(funtimez)
