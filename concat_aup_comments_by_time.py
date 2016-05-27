
import re


def comment_aup(filename='text/02_Frederick_Taylor_2.aup'):
    """
    функция убирает пустые места в комментах
    """
    fileaup = open(filename, 'r')
    record = fileaup.read()
    pattern = re.compile('<label t="(?P<t>.*?)" t1="(?P<t1>.*?)" title="(?P<title>.*?)"')
    values = pattern.findall(record)

    # список всех отрезков и поделенные на 2
    dt = [abs((float(values[i][1]) - float(values[i+1][0])) / 2.0) for i in range(len(values)) if i + 2 <= len(values)]
    # изменяются t, t1 и начальные значения  tt, t1
    for i, (t, t1, title) in enumerate(values):
        tt, t1t1 = t, t1
        # замена значений
        t, t1 = float(t), float(t1)
        if i == 0:
            t1 += dt[i]
        # [1:-1] элементы
        elif i+1!=len(values):
            t -= dt[i-1]
            t1 += dt[i]
        else:
            t -= dt[i-1]
        # Замена новых значений t и t1
        record = re.sub('t="%s" t1="%s"' % (tt, t1t1), 't="%.4f" t1="%.4f"' % (t, t1), record)
    fileaup.close()
    fileaup = open(filename, 'w')
    fileaup.write(record)
    fileaup.close()

if __name__ == "__main__":
    comment_aup()