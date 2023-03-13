import datetime


def get_age(yyyy: int, mm: int, dd: int) -> int:
    birth = datetime.date(yyyy, mm, dd)
    tuhday = datetime.date.today()
    age = round((tuhday - birth).days/365.25)
    return age


if __name__ == "__main__":
    #print("1989/04/20".split("/"))
    get_age(1991, 8, 3)
