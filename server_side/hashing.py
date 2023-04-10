import hashlib

'''from https://www.random.org/strings/'''
pepper = "AI6PWDnDKrQQer4Qmsdi"


def hash_password(string):
    p_string = pepper+string
    fpw = hashlib.sha512(p_string.encode('UTF-8'))
    hpw = fpw.hexdigest()
    return hpw


def compare_password(string, stored_hash):
    p_string = pepper+string
    fpw = hashlib.sha512(p_string.encode('UTF-8'))
    hpw = fpw.hexdigest()
    if hpw == stored_hash:
        return True
    return False


if __name__ == "__main__":
    trying = "fun_password"
    print(hash_password(trying))
    # should output: f06fce8d7026d3814c3012b11694245849b481c0a846b218b09b2e7dbd0d930d4a7ed8194ff24c366183f50cce9d67bbc9700012c11913424c420ba622e2d14e
