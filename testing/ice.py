from icecream import ic
ic.configureOutput(includeContext=True, prefix=' >>> Debug >>> ')
# ic.enable()  # Включить вывод
# ic.disable()  # Отключить вывод

a = 10
b = 20

ic(a, b, a+b)