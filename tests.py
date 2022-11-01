def run_multiple_times(data_in_list: list):
    """Делает запрос определенное кол-во раз, по 200 контактов за раз"""
    import math
    range_list = len(data_in_list)
    if range_list > 200:
        how_many_times = math.ceil(range_list / 200)
        print('Сколько раз ' + str(how_many_times))
        start_range = 0
        end_range = range_list - ((how_many_times - 1) * 200)
        v = 0
        while how_many_times != 0:

            print('Start ' + str(start_range))
            print('End ' + str(end_range))
            v += 1
            main(data_in_list[start_range:end_range])

            start_range = end_range
            end_range += 200

            how_many_times -= 1
            print(how_many_times)



a = [i for i in range(401)]


def main(a):
    if 200 in a:
        print(f'его длинна {len(a)} и 200 в списке Из main {a}')
    else:
        print(f'его длинна {len(a)} и Из main {a}')
    print()


run_multiple_times(a)





