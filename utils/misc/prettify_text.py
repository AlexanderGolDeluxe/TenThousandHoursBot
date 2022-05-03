
def prettify_hours(hours):
    if isinstance(hours, float) and not hours.is_integer():
        return f"{round(hours, 1)} часов"
    else:
        hours = str(int(hours))
        if (hours[-1] in {"2", "3", "4"} and
            not hours[-2:] in {"12", "13", "14"}):
            pretty_hours = hours + " часа"
        elif hours[-1] == "1" and not hours[-2:] == "11":
            pretty_hours = hours + " час"
        else:
            pretty_hours = hours + " часов"
        return pretty_hours