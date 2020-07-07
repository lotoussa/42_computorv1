import sys
import re


def my_sqrt(nb):
    minimum = 0
    maximum = nb if nb >= 1 else 1
    while maximum - minimum > 0.000000001:
        mid = (minimum + maximum) / 2
        if mid * mid < nb:
            minimum = mid
        else:
            maximum = mid
    return maximum


def ft_reduce_form(external):
    printer = ''
    for index_printer, (elem_pow, elem_num) in enumerate(external):
        if elem_pow == 0:
            printer += f"{elem_num}"
        elif elem_pow == 1:
            printer += f"{elem_num} * X"
        else:
            printer += f"{elem_num} * X^{elem_pow}"
        if index_printer + 1 < len(external):
            printer += ' + '
    printer += ' = 0'
    if printer == ' = 0':
        printer = '0 = 0'
    print(f"Reduced form:", re.sub("\+ -", "- ", printer))


def get_all_values(external_power):
    list_external_value = []
    for (key, value) in external_power.items():
        if value:
            list_external_value.append([key, value])
    list_external_value = sorted(list_external_value, key=lambda x: x[0])
    try:
        degree = list_external_value[-1][0]
    except IndexError:
        degree = 0
    return degree, list_external_value


def calc_element(i, external_power, power, number):
    if i == 0:
        try:
            external_power[power] = external_power.get(power, 0) + int(number)
        except ValueError:
            external_power[power] = external_power.get(power, 0) + float(number)
    else:
        try:
            external_power[power] = external_power.get(power, 0) - int(number)
        except ValueError:
            external_power[power] = external_power.get(power, 0) - float(number)


def add_sign_to_elements(input_equation):
    index_clear = 0
    cache_clear = 0
    cache_equation = ""
    for char in input_equation:
        if char != ' ':
            cache_equation += char
    input_equation = cache_equation
    cache_equation = ""
    cache_iter = 0
    input_equation = '/' + input_equation + '/'
    while index_clear < len(input_equation):
        if index_clear + 1 != len(input_equation) and input_equation[index_clear] in ['-', '+'] and \
                input_equation[index_clear + 1].isdigit() or input_equation[index_clear] in ['x', 'X', '^']:
            cache_clear = 1
        elif input_equation[index_clear] in ['-', '+', '='] or input_equation[index_clear] == '*' and cache_clear:
            cache_clear = 0
        elif input_equation[index_clear].isdigit():
            if cache_clear == 0:
                cache_equation = cache_equation + '+'
            while input_equation[index_clear].isdigit() or input_equation[index_clear] == '.':
                cache_iter = 1
                cache_equation = cache_equation + input_equation[index_clear]
                index_clear += 1
        if cache_iter:
            cache_iter = 0
            continue
        cache_equation = cache_equation + input_equation[index_clear]
        index_clear += 1
    return cache_equation[1:-1]


def formatting(input_equation):
    if input_equation:
        print('Input:', input_equation)
    if input_equation.count('/'):
        sys.exit('Syntax error.')
    input_equation = add_sign_to_elements(input_equation)
    equations = [
        equation.split('+')
        for equation in re.sub('x', 'X', re.sub('-', '+-', input_equation)).split('=')
    ]
    if len(equations) != 2:
        sys.exit('Syntax error.')
    for index, equation in enumerate(equations):
        equations[index] = [element for element in equation if element != '']
    return equations


def element_cleaning(k, side, element):
    if k + 1 < len(side) and element == '-':
        if side[k + 1][0] == '-':
            side[k + 1] = side[k + 1][1:]
        else:
            side[k + 1] = '-' + side[k + 1]
        return 1, 0, 0
    if element[-1] == '*':
        side[k + 1] = 'm' + side[k + 1]
        side.insert(k + 1, element[:-1])
        return 1, 0, 0
    if element.count('*') > 1:
        sep = element.split('*')
        num = 0
        pow = 0
        ret = []
        for uni in sep:
            if uni == '':
                return 1, 0, 0
            if num and pow:
                ret += ['m' + num + '*' + pow]
                num = 0
                pow = 0
            if uni[0] not in ['X', '^']:
                num = uni
                if num.count('X'):
                    ret += ['m' + num]
                    num = 0
                    pow = 0
            else:
                pow = uni
            if pow and not num:
                ret += ['m1*' + pow]
                pow = 0
        if num and pow:
            ret += ['m' + num + '*' + pow]
        elif num:
            ret += ['m' + num + '*X^0']
        if ret:
            ret[0] = ret[0][1:]
        side.insert(k, '')
        side[k + 1] = ret.pop(0)
        for ins_i, ins in enumerate(ret):
            side.insert(k + 2 + ins_i, ins)
        return 1, 0, 0
    if (element[0] == '-' and element[1:].isdigit()) or element.isdigit():
        element += '*X^0'
    if element[0] == 'X':
        element = '1*' + element
    if element[-1] == 'X':
        element += '^1'
    if '*' not in element:
        if 'X' in element:
            left, right = element.split('X')
            element = left + '*X' + right
        else:
            element += '*X^0'
    try:
        number, power = element.split('*')
    except:
        sys.exit('Syntax error.')
    if power[0] == 'X':
        if len(power) > 1 and power[1] != '^':
            power = 'X^' + power[1:]
    char, power = power.split('^')
    if number == '-':
        number = '-1'
    if not power:
        sys.exit('Syntax error.')
    return 0, power, number


def transform_power(power):
    try:
        power = int(power)
    except ValueError:
        try:
            power = float(power)
        except:
            sys.exit('Syntax error.')
    return power


def multiply_elements(number, power, cache):
    try:
        number = cache[0] * float(number[1:])
        power = cache[1] + power
    except:
        sys.exit('Syntax error.')
    return number, power


def equation_interpreter(equation):
    external_power = {}
    cache = []
    for i, side in enumerate(equation):
        side.append('0')
        for k, element in enumerate(side):
            ret, power, number = element_cleaning(k, side, element)
            if ret:
                continue
            power = transform_power(power)
            if number[0] == 'm':
                number, power = multiply_elements(number, power, cache)
            if k + 1 < len(side) and side[k + 1][0] != 'm':
                calc_element(i, external_power, power, number)
            cache = [float(number), power]
    return external_power


def get_abc(external_power):
    a = external_power.get(2.0, 0)
    b = external_power.get(1.0, 0)
    c = external_power.get(0.0, 0)
    return a, b, c


def solve_equation(a, b, c, degree):
    if degree > 2:
        print(f"The polynomial degree is strictly greater than 2, I can't solve.")
    elif degree == 0:
        if c == 0:
            print(f"All.")
        else:
            print(f"No solution.")
    elif degree == 1:
        if b == 0 and c == 0:
            print(f"The solution of the equation is:\n0 = 0.")
        elif b == 0:
            print(f"The equation is false.")
        else:
            print(f"The solution is:\n{-c / b}")
    else:
        delta = (b ** 2) - (4 * a * c)
        if a == 0:
            sys.exit("Not a quadratic equation. 'a' shouldn't be zero.")
        if delta > 0:
            delta = my_sqrt(delta)
            x1 = (-b - delta) / (2 * a)
            x2 = (-b + delta) / (2 * a)
            print(f"Discriminant is strictly positive, the two solutions are:\n{x1:.6f}\n{x2:.6f}")
        elif delta == 0:
            x1 = (-b) / (2 * a)
            print(f"The solution of the equation is:\n{x1:.6f}")
        elif delta < 0:
            delta = my_sqrt(delta * -1)
            print(f"Discriminant is negative, the two solutions are:\n({-b} ± {delta}i) / {2 * a}\nfor i^2 = -1")


def main():
    try:
        input_equation = str(sys.argv[1])
    except IndexError:
        sys.exit('Usage:\npython3 computorv1.py "equation"')

    # input_equation = "5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0"
    # input_equation = "5 * X^0 + 4 * X^1.5 - 9.3 * X^-2 = 1 * X^0"
    # input_equation = "42 * X^0 = 42 * X^0"
    # input_equation = "0 = 1"
    # input_equation = "5 + 4 * X + X^2= X^2"
    # input_equation = "2 * X^1 + 4 * X^0 = 10 * X^0"
    # input_equation = "8 * X^0 - 6 * X^1 + 0 * X^2 - 5.6 * X^3 = 3 * X^0"
    # input_equation = "5 * X^2 + 2 * X^1 + 1 * X^0 = 0 * X^0"
    # input_equation = '5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0'
    # input_equation = '4 * X^0 + 4 * X^1 - 9.3 * X^2 = 0'
    # input_equation = '5 * X^0 + 4 * X^1 = 4 * X^0'
    # input_equation = '1 * X^0 + 4 * X^1 = 0'
    # input_equation = '5 * X^0 - 6 * X^1 + 0 * X^2 - 5.6 * X^3 = 0'
    # input_equation = '5 + 4 * X^0 + X^2= X^2'
    # input_equation = '0*X^2-5*X^1-10*X^0=0'
    # input_equation = 'X2-5X-10=0'
    # input_equation = '- 5 * X^0 + - 4 * X^1 = 4 * X^0'
    # input_equation = '8 * X^0 - 6 * X^1 + 0 * X^2 - 5.6 * X^2 * 5 = 3 * X^0 + 5X / -2 +5  - -5 -9 - 70'
    # input_equation = ' - 6 * X^1 - 5.6 * X^2 * X^0 * 4 + 4X =  + 5* X^1 * 4X - 5 * X^0 *-2 +5  - -5 -9 - 70'
    # input_equation = '5* X^1 * 4X / 5 * X^0 /-2 +5  - -5 -9 - 70 = 0'
    # input_equation = '5X2 + 5 * X^5 = -1.25X5 - X3'
    # input_equation = ' - 6 * X^1 - 5.6 * X^2 * X^2 * 4 + 5X =  + 5X + -2 +5  -5 -9 * X^0 * 70 + 5 * X^2'
    # input_equation = '1 * X^1 * 1 * X^1 - 1 = 3'
    # input_equation = '5X0 + 8 * X^1 + 3 * X^2 * 2 * X^0 * 3 * X^0 + 4 * X * 5 * ^2 - 1000 = 0 * 1 + 20x3'
    # input_equation = '0 = 5X0 + 3 * X^2 * 2X0 * 2 * X^0 + 1 '
    # input_equation = 'x2 + 4x + 6.25 = 0'
    # input_equation = '8 * X^0 - 6 * X^1 + 0 * X^2 - 5.6 * X^2 * 5 - 8 = 3 * X^0 + 5X * - 2 +9  * -5 *-9 - 70'
    # input_equation = '+8 * X^0 - 6 * X^1 + +0 * X^2 - 5.6 * X^2 * +5 = +3 * X^0 + +5X * - 2 +5  - -5 -9 - +70'

    equations = formatting(input_equation)
    values = equation_interpreter(equations)
    a, b, c = get_abc(values)
    degree, list_external_value = get_all_values(values)
    ft_reduce_form(list_external_value)
    print(f"Polynomial degree: {degree}")
    solve_equation(a, b, c, degree)


if __name__ == "__main__":
    main()
