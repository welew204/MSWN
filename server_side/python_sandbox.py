import datetime

start_date = datetime.date.today()

print(type(start_date))
print(start_date)

start_date = start_date.strftime("%Y-%m-%d")

print(type(start_date))
print(start_date)

start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")

print(type(start_date))
print(start_date)
