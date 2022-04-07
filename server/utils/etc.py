import random
import string


def rand_string(length: int = 64, ascii_=True, digits=True, punctuation=True) -> str:
    """ Generate random string with selected characters """
    chars = ''
    if ascii_:
        chars += string.ascii_letters
    if digits:
        chars += string.digits
    if punctuation:
        # I guess some characters are not allowed or make a mess of the password.
        chars += r"!%()*+,-.:;<=>?@[]^_{|}~"

    return ''.join(random.sample(chars, length))
