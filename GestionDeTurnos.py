from datetime import datetime, timedelta

festivoscolombia_2023 = ["2023-01-01", "2023-01-09", "2023-03-20", "2023-04-02", "2023-04-06", "2023-04-07", "2023-04-09", "2023-05-01", "2023-05-22",
                         "2023-06-12", "2023-06-19", "2023-07-03", "2023-07-20", "2023-08-07", "2023-08-21", "2023-10-16", "2023-11-06", "2023-11-13", "2023-12-08", "2023-12-25"]


def validate_second_shift(first_shift, second_shift):
    if first_shift == "Dia" and second_shift in ["Dia", "Noche"]:
        return True
    elif first_shift == "Noche" and second_shift in ["Noche", "Descanso"]:
        return True
    elif first_shift == "Descanso" and second_shift in ["Descanso", "Dia"]:
        return True
    return False


def get_next_shift(shift):
    if shift == "Dia":
        return "Noche"
    elif shift == "Noche":
        return "Descanso"
    else:
        return "Dia"


def create_shift_sequence(first_shift, second_shift, days_count):
    if not validate_second_shift(first_shift, second_shift):
        return False

    sequence = [first_shift, second_shift]

    if first_shift == second_shift:
        if first_shift == "Dia":
            sequence.extend(["Noche", "Noche"])
        elif first_shift == "Noche":
            sequence.extend(["Descanso", "Descanso"])
        else:
            sequence.extend(["Dia", "Dia"])
    else:
        sequence.append(second_shift)

    while len(sequence) < days_count:
        next_shift = get_next_shift(sequence[-1])
        sequence.extend([next_shift, next_shift])

    return sequence[:days_count]


def group_shifts_by_year_and_month(shift_sequence, start_date):
    shifts_by_month = {}
    current_date = datetime.strptime(start_date, "%Y-%m-%d")

    for shift in shift_sequence:
        year_month_key = f"{current_date.year}-{current_date.month}"

        if year_month_key not in shifts_by_month:
            shifts_by_month[year_month_key] = []

        shifts_by_month[year_month_key].append(
            {"date": current_date.strftime("%Y-%m-%d"), "shift": shift})
        current_date += timedelta(days=1)

    return shifts_by_month


def es_festivo_o_domingo(fecha):
    fecha_datetime = datetime.strptime(fecha, "%Y-%m-%d")
    return fecha_datetime.strftime("%Y-%m-%d") in festivoscolombia_2023 or fecha_datetime.weekday() == 6


def calculate_sequence(start_date_str, end_date_str, first_shift, second_shift):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    if start_date > end_date:
        return "Error: La fecha de inicio debe ser anterior a la fecha de fin."

    days_count = (end_date - start_date).days + 1

    shift_sequence = create_shift_sequence(
        first_shift, second_shift, days_count)

    if shift_sequence:
        shifts_by_year_and_month = group_shifts_by_year_and_month(
            shift_sequence, start_date_str)
        return shifts_by_year_and_month
    else:
        return "Error: Secuencia de turnos inválida."


def contar_dias_festivos_y_turnos_trabajados(shifts_by_year_and_month):
    dias_festivos_y_turnos = []
    for year_month, shifts in shifts_by_year_and_month.items():
        for shift_info in shifts:
            if es_festivo_o_domingo(shift_info['date']) and shift_info['shift'] in ["Dia", "Noche"]:
                dia_y_turno = (shift_info['date'], shift_info['shift'])
                dias_festivos_y_turnos.append(dia_y_turno)

    return len(dias_festivos_y_turnos), dias_festivos_y_turnos


def calcular_horas_turno_con_festivos(turno, fecha):
    es_festivo = es_festivo_o_domingo(fecha)
    es_festivo_siguiente = es_festivo_o_domingo((datetime.strptime(
        fecha, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d"))

    horas_ordinarias_festivas = horas_ordinarias_no_festivas = 0
    horas_extra_diurnas_festivas = horas_extra_diurnas_no_festivas = 0
    horas_extra_nocturnas_festivas = horas_extra_nocturnas_no_festivas = 0
    recargo_nocturno_festivo = recargo_nocturno_ordinario = 0

    if turno == "Dia":
        if es_festivo:
            horas_ordinarias_festivas = 8  # De 6 a.m. a 2 p.m.
            horas_extra_diurnas_festivas = 4  # De 2 p.m. a 6 p.m.
        else:
            horas_ordinarias_no_festivas = 8  # De 6 a.m. a 2 p.m.
            horas_extra_diurnas_no_festivas = 4  # De 2 p.m. a 6 p.m.
    elif turno == "Noche":
        horas_ordinarias = 3  # De 6 p.m. a 9 p.m.
        horas_extra_nocturnas = 3  # De 9 p.m. a 12 a.m.
        recargo_nocturno = 8  # De 10 p.m. a 6 a.m.

        if es_festivo:
            horas_ordinarias_festivas = horas_ordinarias
            horas_extra_nocturnas_festivas = horas_extra_nocturnas
            recargo_nocturno_festivo = 2 if not es_festivo_siguiente else recargo_nocturno
        else:
            horas_ordinarias_no_festivas = horas_ordinarias
            horas_extra_nocturnas_no_festivas = horas_extra_nocturnas
            recargo_nocturno_ordinario = recargo_nocturno

        # Ajustar recargo nocturno si el día siguiente no es festivo
        if es_festivo and not es_festivo_siguiente:
            recargo_nocturno_festivo = 2  # De 10 p.m. a 12 a.m.
            recargo_nocturno_ordinario = 6  # De 12 a.m. a 6 a.m.

    return (horas_ordinarias_festivas, horas_ordinarias_no_festivas,
            horas_extra_diurnas_festivas, horas_extra_diurnas_no_festivas,
            horas_extra_nocturnas_festivas, horas_extra_nocturnas_no_festivas,
            recargo_nocturno_festivo, recargo_nocturno_ordinario)


def mostrar_distribucion_horas_por_secuencia(sequence_result):
    for year_month, shifts in sequence_result.items():
        print(f"\n{year_month}:")
        for shift_info in shifts:
            fecha = shift_info['date']
            turno = shift_info['shift']

            horas_distribucion = calcular_horas_turno_con_festivos(
                turno, fecha)

            print(f"  Fecha: {fecha}, Turno: {turno}")
            print("    Distribucion de Horas:")

            print(f"      Horas extras diurnas festivas: {
                  horas_distribucion[2]}")
            print(f"      Horas extras diurnas ordinarias: {
                  horas_distribucion[3]}")
            print(f"      Horas Extra Nocturnas Festivas: {
                  horas_distribucion[4]}")
            print(f"      Horas Extra Nocturnas No Festivas: {
                  horas_distribucion[5]}")
            print(f"      Horas extras de recargo nocturno festivo: {
                  horas_distribucion[6]}")
            print(f"      Horas extras de recargo nocturno ordinarias: {
                  horas_distribucion[7]}")


def verificar_limite_semanal_vigilantes(shifts_by_year_and_month):
    horas_por_turno = {"Dia": 12, "Noche": 12}  
    horas_semanales = 0
    semanas_excedidas = []

    for year_month, shifts in shifts_by_year_and_month.items():
        for shift_info in shifts:
            if shift_info['shift'] in ["Dia", "Noche"]:
                horas_semanales += horas_por_turno.get(shift_info['shift'], 0)

            fecha_objeto = datetime.strptime(shift_info['date'], "%Y-%m-%d")
            if fecha_objeto.weekday() == 6:
                if horas_semanales > 60:
                    semanas_excedidas.append(shift_info['date'])
                horas_semanales = 0

    return semanas_excedidas


def calcular_horas_quincena(shifts_by_year_and_month):
    total_horas = {

        'horas_extras_diurnas_festivas': 0, 'horas_extras_diurnas_ordinarias': 0,
        'horas_extras_nocturnas_festivas': 0, 'horas_extras_nocturnas_ordinarias': 0,
        'horas_extras_recargo_nocturno_festivas': 0, 'horas_extras_recargo_nocturno_ordinarias': 0
    }

    for year_month, shifts in shifts_by_year_and_month.items():
        for shift_info in shifts:
            horas_turno = calcular_horas_turno_con_festivos(
                shift_info['shift'], shift_info['date'])

            total_horas['horas_extras_diurnas_festivas'] += horas_turno[2]
            total_horas['horas_extras_diurnas_ordinarias'] += horas_turno[3]
            total_horas['horas_extras_nocturnas_festivas'] += horas_turno[4]
            total_horas['horas_extras_nocturnas_ordinarias'] += horas_turno[5]
            total_horas['horas_extras_recargo_nocturno_festivas'] += horas_turno[6]
            total_horas['horas_extras_recargo_nocturno_ordinarias'] += horas_turno[7]

    return total_horas


def calcular_sueldo(horas_quincena, dias_festivos_trabajados):
    sueldo_base = 1160000  # Salario mínimo
    subsidio_transporte = 140606  # Auxilio de transporte
    deduccion_salud = 46400  # 4% del salario mínimo
    deduccion_pension = 46400  # 4% del salario mínimo

    # Valores hora ordinaria y recargos
    valor_hora_ordinaria = 4833  # Basado en el salario mínimo
    recargo_hora_extra_diurna = 1.25  # 25%
    recargo_hora_extra_nocturna = 1.75  # 75%
    recargo_hora_extra_diurna_festiva = 2.00  # 100%
    recargo_hora_extra_nocturna_festiva = 2.50  # 150%
    recargo_nocturno = 1.35  # 35% para recargo nocturno ordinario
    recargo_festivo = 1.75  # 75% para recargo dominical o festivo
    recargo_nocturno_festivo = 2.10  # 35% nocturno + 75% festivo

    # Calcular el total devengado
    total_devengado = sueldo_base / 2
    total_devengado += valor_hora_ordinaria * recargo_hora_extra_diurna * \
        horas_quincena['horas_extras_diurnas_ordinarias']
    total_devengado += valor_hora_ordinaria * recargo_hora_extra_nocturna * \
        horas_quincena['horas_extras_nocturnas_ordinarias']
    total_devengado += valor_hora_ordinaria * recargo_hora_extra_diurna_festiva * \
        horas_quincena['horas_extras_diurnas_festivas']
    total_devengado += valor_hora_ordinaria * recargo_hora_extra_nocturna_festiva * \
        horas_quincena['horas_extras_nocturnas_festivas']
    total_devengado += valor_hora_ordinaria * recargo_nocturno * \
        horas_quincena['horas_extras_recargo_nocturno_ordinarias']
    total_devengado += valor_hora_ordinaria * \
        recargo_festivo * dias_festivos_trabajados
    total_devengado += valor_hora_ordinaria * recargo_nocturno_festivo * \
        horas_quincena['horas_extras_recargo_nocturno_festivas']

    # Calcular el sueldo final
    sueldo = total_devengado - deduccion_salud - \
        deduccion_pension + subsidio_transporte

    return sueldo


result = calculate_sequence("2023-01-01", "2023-01-16", "Noche", "Noche")

cantidad, dias_y_turnos_trabajados = contar_dias_festivos_y_turnos_trabajados(
    result)


mostrar_distribucion_horas_por_secuencia(result)

print("Numero de dias festivos trabajados:", cantidad)
print("Dias festivos y turnos trabajados:", dias_y_turnos_trabajados)
semanas_excedidas = verificar_limite_semanal_vigilantes(result)

if semanas_excedidas:
    print("Las siguientes semanas excedieron el límite de 60 horas:", semanas_excedidas)
else:
    print("No se excedio el limite de horas en ninguna semana.")
horas_quincena = calcular_horas_quincena(result)

print("Total de horas trabajadas en la quincena por categoria:")
for categoria, total in horas_quincena.items():
    print(f"{categoria}: {total} horas")

horas_quincena = calcular_horas_quincena(result)
cantidad_dias_festivos_trabajados, _ = contar_dias_festivos_y_turnos_trabajados(
    result)
sueldo_final = calcular_sueldo(
    horas_quincena, cantidad_dias_festivos_trabajados)

print(f"El sueldo final a recibir es: ${sueldo_final:,.2f}")
