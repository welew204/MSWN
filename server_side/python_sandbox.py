from pprint import pprint
from collections import defaultdict

pract_dict = {"fun": 0, "times": 1, "are": 2, "lame": 3}
pract_dict2 = {"fun": 0, "times": 1, "are": 2, "lame": 3}
pract_list = [pract_dict, pract_dict2]
print(pract_list[0].keys())

join_pract = ",".join(pract_list[0].keys())
print(join_pract)
