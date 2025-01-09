import requests
from bs4 import BeautifulSoup

base_url = "https://komunikacja.bialystok.pl"


def get_stops(line_number):
    params = {
        "page": "lista_przystankow",
        "nr": line_number,
    }

    response = requests.get(base_url, params=params)

    if response.ok:
        result = {}

        soup = BeautifulSoup(response.text, features="lxml")
        stop_list_tables = soup.find(id="lista_przystankow").find_all("table")
        if not stop_list_tables[0].tbody.contents:
            print("\033[31mNot a line:", line_number, "\033[00m")
            return
        for table in stop_list_tables:
            title = table.thead.tr.td.string.split(": ")[1].strip()
            # stops = []
            stops = [
                {"name": tr.td.a.contents[0].strip(), "url": tr.td.a.attrs["href"]}
                for tr in table.tbody.find_all("tr")
            ]
            # for tr in table.tbody.find_all("tr"):
            #     print(tr.td.a.contents)
            #     stops.append(
            #         {"name": tr.td.a.string.strip(), "url": tr.td.a.attrs["href"]}
            #     )
            #     print('================================')
            result[title] = stops

        return result
    else:
        print(
            "\033[31mRequest failed, returned status code",
            response.status_code,
            "\033[00m",
        )


def get_schedule(url):
    response = requests.get(base_url + url)

    if response.ok:
        weekday_departures = {}
        saturday_departures = {}
        holiday_departures = {}

        soup = BeautifulSoup(response.text, features="lxml")
        weekday_table = soup.find(id="rozklad_1").tbody.find_all(class_="c1")
        saturday_table = soup.find(id="rozklad_2").tbody.find_all(class_="c2")
        holiday_table = soup.find(id="rozklad_3").tbody.find_all(class_="c3")

        for hour in weekday_table:
            hour_number = hour.div.contents[0].string
            minutes = [
                minute.contents[0] for minute in hour.div.findChildren("span")[1:]
            ]
            weekday_departures[hour_number] = minutes
        for hour in saturday_table:
            hour_number = hour.div.contents[0].string
            minutes = [
                minute.contents[0] for minute in hour.div.findChildren("span")[1:]
            ]
            saturday_departures[hour_number] = minutes
        for hour in holiday_table:
            hour_number = hour.div.contents[0].string
            minutes = [
                minute.contents[0] for minute in hour.div.findChildren("span")[1:]
            ]
            holiday_departures[hour_number] = minutes

        return {
            "weekday": weekday_departures,
            "saturday": saturday_departures,
            "holiday": holiday_departures,
        }
    else:
        print(
            "\033[31mRequest failed, returned status code",
            response.status_code,
            "\033[00m",
        )


print("Wpisz linię")
line = input("\033[32m> ")
stops = get_stops(line)
print("\033[00m")

print("\033[43m", list(stops.keys())[0].center(48), "", list(stops.keys())[1].center(48), "\033[0m")
for i in range(max(len(stops[list(stops.keys())[0]]), len(stops[list(stops.keys())[1]]))):  # This is a mess
    print(
        '\033[43m a' + str(i + 1) + (" " if i < 9 else "") + ' \033[00m',
        stops[list(stops.keys())[0]][i]["name"].ljust(43, " ") if i < len(stops[list(stops.keys())[0]]) else " " * 43,
        '\033[43m b' + str(i + 1) + (" " if i < 9 else "") + ' \033[00m',
        stops[list(stops.keys())[1]][i]["name"] if i < len(stops[list(stops.keys())[1]]) else "",
    )

stop_choice = input("Wybierz przystanek (a/b + numer)\n\033[32m> ")
print("\033[00m")

if stop_choice[0] == "a":
    stop = stops[list(stops.keys())[0]][int(stop_choice[1:]) - 1]
elif stop_choice[0] == "b":
    stop = stops[list(stops.keys())[1]][int(stop_choice[1:]) - 1]
else:
    print("\033[31mNieprawidłowy wybór!\033[00m")
    exit()

print("\033[43m", line, "→", list(stops.keys())[0], "\033[00m", stop["name"])
print()
print(
    "\033[100m     dni robocze     \033[44m       soboty        \033[42m  niedziele i święta  \033[00m"
)
schedule = get_schedule(stop["url"])
hours = []
[
    hours.append(x)
    for x in list(schedule["weekday"].keys())
    + list(schedule["saturday"].keys())
    + list(schedule["holiday"].keys())
    if x not in hours
]
for hour in hours:
    print("\033[100m " + (" " if len(hour) == 1 else "") + hour, end=" \033[00m ")
    weekday_departures = schedule["weekday"].get(hour)
    print(
        " ".join(weekday_departures) + " " * (16 - len(" ".join(weekday_departures)))
        if weekday_departures
        else " " * 16,
        end="",
    )

    print("\033[44m " + (" " if len(hour) == 1 else "") + hour, end=" \033[00m ")
    saturday_departures = schedule["saturday"].get(hour)
    print(
        " ".join(saturday_departures) + " " * (16 - len(" ".join(saturday_departures)))
        if saturday_departures
        else " " * 16,
        end="",
    )

    print("\033[42m " + (" " if len(hour) == 1 else "") + hour, end=" \033[00m ")
    holiday_departures = schedule["holiday"].get(hour)
    print(
        " ".join(holiday_departures) + " " * (16 - len(" ".join(holiday_departures)))
        if holiday_departures
        else " " * 16,
        end="",
    )

    print()
