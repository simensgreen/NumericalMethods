

def simple_iterations(matrix,
                      free_column: list,
                      await_e: float = None,
                      iterations: int = None,
                      level_of_detail: int = 3):
    """
    Решает СЛАУ методом простых итераций

    Args:
        matrix (Matrix): матрица, относительно которой требуется решение
        free_column (list): столбец свободных членов
        await_e (float): необходимая точность, например точность до 3 знака после точки - .001
        iterations (int): количество итераций, которое необходимо совершить
        level_of_detail (int): уровень детализации (меньше число - больше деталей)

    Yields:
        dict: данные о текущем шаге решения

    Raises:
        ArithmeticError: если главная диагональ матрицы не является доминирующей

    """
    if iterations is None:
        if await_e is None:
            await_e = (10 ** -8)
    matrix = matrix.копия()
    free_column = free_column.copy()
    answer = {}
    if level_of_detail < 2:
        answer.update({'Этап': 'Получены значения'})
        answer.update({'Матрица': matrix})
        answer.update({'Столбец свободных членов': free_column})
        yield answer
    if not matrix.преобладающая_ли_диагональ:
        raise ArithmeticError("Метод итераций работает только с матрицами с доминантной диагональю")
    # Извлечение главной диагонали, замещая значения нулями
    new_column = []
    for row_no, col_no in matrix:
        if row_no == col_no:
            new_column.append(matrix[row_no][col_no])
            matrix.матрица[row_no][col_no] = 0
    matrix = -matrix
    # Деление соответствующих строк на значения из диагонали
    for row_no, col_no in matrix:
        matrix.матрица[row_no][col_no] /= new_column[row_no]
    # Деление сободных членов на значения из диагонали
    free_column = [free_elem / diagonal_elem for free_elem, diagonal_elem in zip(free_column, new_column)]
    free_column = matrix.обернуть([free_column])
    if level_of_detail < 2:
        answer.update({'Этап': 'Из матрицы извлечена главная диагональ'})
        answer.update({'Матрица': matrix})
        answer.update({'Столбец свободных членов': free_column.матрица[0]})
        yield answer
    # Вычисление нормы (минимальная из двух)
    matrix_norms = (matrix.матричная_норма_1, matrix.матричная_норма_2)
    vector_norms = (free_column.векторная_норма_1, free_column.векторная_норма_2)
    norm_number = 1 if matrix.матричная_норма_1 <= matrix.матричная_норма_2 else 2
    if level_of_detail < 3:
        answer.update({'Этап': 'Вычислены необходимые нормы'})
        answer.update({'Нормы матрицы': matrix_norms})
        answer.update({'Нормы вектора': vector_norms})
        answer.update({'Номер выбранной нормы': norm_number})
        yield answer
    norma_beta = vector_norms[norm_number - 1]
    norma = matrix_norms[norm_number - 1]
    # Принимаем за начальный вектор вектор бета с шапкой
    free_column = free_column.вектор_в_список
    solution_vector = free_column.копия()
    # Добавление столбца свободных членов
    matrix.добавить_столбец(free_column.копия())
    # Добавление единицы нужно для нормальной работы цикла с матрицей с добавленным столбцом свободных членов
    solution_vector.append(1)
    # Входим в цикл
    delta = None
    epsilon = None
    iteration_counter = 0
    answer.pop('Этап', None)
    answer.pop('Нормы матрицы', None)
    answer.pop('Нормы вектора', None)
    answer.pop('Номер выбранной нормы', None)
    answer.pop('Матрица', None)
    answer.pop('Столбец свободных членов', None)
    while True:
        if level_of_detail < 3:
            answer.update({'Номер итерации': iteration_counter})
            answer.update({'Решение': solution_vector[:-1]})
            answer.update({'Дельта': delta})
            answer.update({'Эпсилон': epsilon})
            yield answer
        if iterations:
            if iteration_counter == iterations:
                break
        elif await_e > (norma ** (iteration_counter - 2)) / (1 - norma) / 10:
            break
        new_solution = []
        for row_no in range(matrix.количество_строк):
            container = 0
            for col_no in range(matrix.количество_столбцов):
                container += solution_vector[col_no] * matrix[row_no][col_no]
            # Только после заполнения нового вектора (обработана вся матрица), замняем вектор решений на новый на новый
            new_solution.append(container)
        new_solution.append(1)
        iteration_counter += 1
        epsilon = ((norma ** iteration_counter) / (1 - norma)) * norma_beta
        delta = max(map(lambda x: abs(x), [_ - __ for _, __ in zip(solution_vector, new_solution)]))
        # Вот и замена
        solution_vector = new_solution
    answer.pop('Дельта', None)
    answer.pop('Эпсилон', None)
    answer.pop('Номер итерации', None)
    if level_of_detail < 4:
        answer.update({'Решение': solution_vector[:-1]})
    yield answer


def zeidel_method(matrix,
                  free_column: list,
                  await_e: float = None,
                  iterations: int = None,
                  level_of_detail: int = 3):
    """
    Решает СЛАУ методом Зейделя

    Args:
        matrix (Matrix): матрица, относительно которой требуется решение
        free_column (list): столбец свободных членов
        await_e (float): необходимая точность, например точность до 3 знака после точки - .001
        iterations (int): количество итераций, которое необходимо совершить
        level_of_detail (int): (int): уровень детализации (меньше число - больше деталей)

    Yields:
        dict: данные о текущем шаге решения

    Raises:
        ArithmeticError: если главная диагональ матрицы не является доминирующей

    """
    if iterations is None:
        if await_e is None:
            await_e = (10 ** -8)
    matrix = matrix.копия()
    free_column = free_column.copy()
    answer = {}
    if level_of_detail < 2:
        answer.update({'Этап': 'Получены значения'})
        answer.update({'Матрица': matrix})
        answer.update({'Столбец свободных членов': free_column})
        yield answer
    if not matrix.преобладающая_ли_диагональ:
        raise ArithmeticError("Метод итераций работает только с матрицами с доминантной диагональю")
    # Извлечение главной диагонали, замещая значения нулями
    new_column = []
    for row_no, col_no in matrix:
        if row_no == col_no:
            new_column.append(matrix[row_no][col_no])
            matrix.матрица[row_no][col_no] = 0
    matrix = -matrix
    # Деление соответствующих строк на значения из диагонали
    for row_no, col_no in matrix:
        matrix.матрица[row_no][col_no] /= new_column[row_no]
    # Деление сободных членов на значения из диагонали
    free_column = [free_elem / new_elem for free_elem, new_elem in zip(free_column, new_column)]
    free_column = matrix.обернуть([free_column])
    if level_of_detail < 2:
        answer.update({'Этап': 'Из матрицы извлечена главная диагональ'})
        answer.update({'Матрица': matrix})
        answer.update({'Столбец свободных членов': free_column.матрица[0]})
        yield answer
    # Вычисление нормы (минимальная из двух)
    matrix_norms = (matrix.матричная_норма_1, matrix.матричная_норма_2)
    vector_norms = (free_column.векторная_норма_1, free_column.векторная_норма_2)
    norm_number = 1 if matrix.матричная_норма_1 <= matrix.матричная_норма_2 else 2
    if level_of_detail < 3:
        answer.update({'Этап': 'Вычислены необходимые нормы'})
        answer.update({'Нормы матрицы': matrix_norms})
        answer.update({'Нормы вектора': vector_norms})
        answer.update({'Номер выбранной нормы': norm_number})
        yield answer
    norma_beta = vector_norms[norm_number - 1]
    norma = matrix_norms[norm_number - 1]
    # Принимаем за начальный вектор вектор бета с шапкой
    free_column = free_column.вектор_в_список
    solution_vector = free_column.копия()
    # Добавление столбца свободных членов
    matrix.добавить_столбец(free_column.копия())
    # Добавление единицы нужно для нормальной работы цикла с матрицей с добавленным столбцом свободных членов
    solution_vector.append(1)
    # Входим в цикл
    delta = None
    epsilon = None
    iteration_counter = 0
    answer.pop('Этап', None)
    answer.pop('Нормы матрицы', None)
    answer.pop('Нормы вектора', None)
    answer.pop('Номер выбранной нормы', None)
    answer.pop('Матрица', None)
    answer.pop('Столбец свободных членов', None)
    while True:
        old_solution = solution_vector.копия()
        if level_of_detail < 3:
            answer.update({'Номер итерации': iteration_counter})
            answer.update({'Решение': solution_vector[:-1]})
            answer.update({'Дельта': delta})
            answer.update({'Эпсилон': epsilon})
            yield answer
        if iterations:
            if iteration_counter == iterations:
                break
        elif await_e > (norma ** (iteration_counter - 2)) / (1 - norma) / 10:
            break
        for row_no in range(matrix.количество_строк):
            container = 0
            for col_no in range(matrix.количество_столбцов):
                container += solution_vector[col_no] * matrix[row_no][col_no]
            # В строке ниже и кроется отличие: для дальнейших вычислений сразу используется полученный результат
            solution_vector[row_no] = container
        iteration_counter += 1
        epsilon = ((norma ** iteration_counter) / (1 - norma)) * norma_beta
        delta = max(map(lambda x: abs(x), [_ - __ for _, __ in zip(solution_vector, old_solution)]))
    answer.pop('Дельта', None)
    answer.pop('Эпсилон', None)
    answer.pop('Номер итерации', None)
    if level_of_detail < 4:
        answer.update({'Решение': solution_vector[:-1]})
    yield answer


def triple_diagonal(matrix, free_column, level_of_detail=3):
    """
    Решает СЛАУ методом Томаса (прогонки)

    Args:
        matrix (Matrix): матрица, относительно которой требуется решение
        free_column (list): столбец свободных членов
        level_of_detail (int): (int): уровень детализации (меньше число - больше деталей)

    Yields:
        dict: данные о текущем шаге решения

    Raises:
        ArithmeticError: если матрица не является трехдиагональной

    """

    def get_element(row, col):
        if 0 < row <= matrix.количество_строк and 0 < col <= matrix.количество_столбцов - 1:
            return matrix[row - 1][col - 1]
        else:
            return 0

    answer = {}
    matrix = matrix.копия()

    if level_of_detail < 2:
        answer.update({'Этап': 'Получены значения'})
        answer.update({'Матрица': matrix})
        answer.update({'Столбец свободных членов': free_column})
        yield answer
    if not matrix.трехдиагональная_ли:
        raise ArithmeticError("Метод прогонки работает только с трехдиагональной марицей")
    matrix.добавить_столбец(free_column)
    if level_of_detail < 2:
        answer.update({'Этап': 'Расширена матрица'})
        answer.update({'Матрица': matrix})
        answer.update({'Столбец свободных членов': free_column})
        yield answer
    p = [0]
    q = [0]
    # Прямой ход прогонки
    answer.pop('Этап', None)
    answer.pop('Матрица', None)
    answer.pop('Столбец свободных членов', None)
    if level_of_detail < 3:
        answer.update({'Прямая прогонка': '0 строка'})
        answer.update({'P0': p[0]})
        answer.update({'Q0': q[0]})
        yield answer
        answer.pop('Q0', None)
        answer.pop('P0', None)
    for row_no in range(1, matrix.количество_строк + 1):
        if level_of_detail < 3:
            answer.update({'Прямая прогонка': f'{row_no} строка'})
        a = get_element(row_no, row_no - 1)
        b = get_element(row_no, row_no)
        c = get_element(row_no, row_no + 1)
        d = matrix[row_no - 1][matrix.количество_столбцов - 1]
        new_p = -c / (b + a * p[row_no - 1])
        if level_of_detail < 2:
            answer.update({'a': a})
            answer.update({'b': b})
            answer.update({'c': c})
            answer.update({'d': d})
            answer.update({"Этап решения": f'P{row_no} = -c / (b + a * P{row_no - 1}) = '
                                           f'P{row_no} = {-c} / ({b} + {a} * {p[row_no - 1]}) = '
                                           f'{new_p}'})
        if level_of_detail < 3:
            answer.update({f'P{row_no}': new_p})
        p.append(new_p)
        new_q = (d - a * q[row_no - 1]) / (b + a * p[row_no if row_no < 2 else row_no - 1])
        if level_of_detail < 2:
            answer.update({"Этап решения": f'Q{row_no} = (d - a * Q{row_no - 1}) / '
                                           f'(b + a * P{row_no if row_no < 2 else row_no - 1}) = '
                                           f'({d} - {a} * {q[row_no - 1]}) / '
                                           f'({b} + {a} * {p[row_no if row_no < 2 else row_no - 1]}) = '
                                           f'{new_q}'})
        if level_of_detail < 3:
            answer.update({f'Q{row_no}': new_q})
        q.append(new_q)
        if level_of_detail < 3:
            yield answer
            answer.pop(f'Q{row_no}', None)
            answer.pop(f'P{row_no}', None)
    # Обратный ход прогонки
    answer.pop('a', None)
    answer.pop('b', None)
    answer.pop('c', None)
    answer.pop('d', None)
    answer.pop('Этап решения', None)
    answer.pop('Прямая прогонка', None)
    x = [0 for row_no in range(matrix.количество_строк + 1)]
    for row_no in range(matrix.количество_строк, 0, -1):
        if level_of_detail < 3:
            answer.update({'Обратная прогонка': f'{row_no} строка'})
        if row_no == matrix.количество_строк:
            if level_of_detail < 2:
                answer.update({f'Этап решения': f"X{row_no} = Q{row_no} = {q[row_no]}"})
            x[row_no] = q[row_no]
        else:
            # Этот if необходим из-за "кривых" индексов
            x[row_no] = q[row_no] + p[row_no] * x[row_no + 1]
            if level_of_detail < 2:
                answer.update({f'Этап решения': f"X{row_no} = Q{row_no} + P{row_no} * X{row_no + 1} = "
                                                f"{q[row_no]} + {p[row_no]} * {x[row_no + 1]} = {x[row_no]}"})
        if level_of_detail < 3:
            answer.update({f"X{row_no}": x[row_no]})
            yield answer
    answer.pop('Этап решения', None)
    answer.pop('Обратная прогонка', None)
    for _ in range(1, len(x)):
        answer.pop(f'X{_}', None)
    if level_of_detail < 4:
        answer.update({'Решение': x[1:]})
    yield answer


def auto_iterate(matrix, free_column: list) -> list:
    """
    Автоматический выбор лучшего алгоритма для решения СЛАУ

    Args:
        matrix (Matrix): матрица, относительно которой требуется решение
        free_column (list): столбец свободных членов

    Returns:
        list: решение СЛАУ

    """
    if matrix.трехдиагональная_ли:
        decision = triple_diagonal(matrix, free_column)
    else:
        decision = zeidel_method(matrix, free_column)
    solution = []
    for step in decision:
        solution = step.get('Решение')
    return solution
