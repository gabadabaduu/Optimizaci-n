import pandas as pd
from ortools.linear_solver import pywraplp
import os

os.chdir("C:\\Users\\GabyL\\analisisOpti")

# Cargar datos
demanda = pd.read_csv("demanda.csv")
capacidad = pd.read_csv("capacidad.csv")

# Crear el modelo
solver = pywraplp.Solver.CreateSolver('SCIP')

# Crear variables
num_empleados = 8
num_franjas = len(demanda)

trabaja = {}
pausa_activa = {}
almuerza = {}
nada = {}

for i in range(num_empleados):
    for j in range(num_franjas):
        trabaja[i, j] = solver.IntVar(0, 1, f'Trabaja_{i}_{j}')
        pausa_activa[i, j] = solver.IntVar(0, 1, f'PausaActiva_{i}_{j}')
        almuerza[i, j] = solver.IntVar(0, 1, f'Almuerza_{i}_{j}')
        nada[i, j] = solver.IntVar(0, 1, f'Nada_{i}_{j}')

# Restricciones
for i in range(num_empleados):
    
    # Restricción de mínimo 1 hora de trabajo continuo
    for j in range(num_franjas - 3):
        solver.Add(trabaja[i, j] + trabaja[i, j + 1] + trabaja[i, j + 2] + trabaja[i, j + 3] >= 1)

    # Restricción de máximo 2 horas de trabajo continuo
    for j in range(num_franjas - 8):
        solver.Add(trabaja[i, j] + trabaja[i, j + 1] + trabaja[i, j + 2] + trabaja[i, j + 3] +
                   trabaja[i, j + 4] + trabaja[i, j + 5] + trabaja[i, j + 6] + trabaja[i, j + 7] <= 2)

    # Restricción de almuerzo de 1 hora y media
    for j in range(num_franjas - 4):
        solver.Add(almuerza[i, j] + almuerza[i, j + 1] + almuerza[i, j + 2] + almuerza[i, j + 3] +
                   almuerza[i, j + 4] == 1)

    # Restricción de hora mínima y máxima para almuerzo
    solver.Add(almuerza[i, 6] + almuerza[i, 7] + almuerza[i, 8] == 1)
    solver.Add(almuerza[i, 11] + almuerza[i, 12] + almuerza[i, 13] == 1)
    solver.Add(almuerza[i, 14] + almuerza[i, 15] + almuerza[i, 16] == 1)

    # Jornada laboral de 8 horas
    solver.Add(sum(trabaja[i, j] for j in range(num_franjas)) == 8)

    # Estado Nada al inicio y final del día
    solver.Add(nada[i, 0] == 1)
    solver.Add(nada[i, num_franjas - 1] == 1)

    # Último estado debe ser Trabaja
    solver.Add(trabaja[i, num_franjas - 1] == 1)

    # Debe haber al menos 1 empleado trabajando en cada franja horaria
    solver.Add(sum(trabaja[i, j] for i in range(num_empleados)) >= 1)

    # Cualquier franja de trabajo debe durar entre 1 y 2 horas
    for j in range(num_franjas - 1):
        solver.Add(trabaja[i, j] + trabaja[i, j + 1] <= 1)

# Función objetivo
solver.Minimize(solver.Sum(demanda.iloc[j]["Clientes"] - sum(trabaja[i, j] for i in range(num_empleados))
                          for j in range(num_franjas)))

# Resolver el modelo
solver.Solve()

# Obtener resultados
horario_optimo = pd.DataFrame(columns=["Empleado", "Franja", "Estado"])
for i in range(num_empleados):
    for j in range(num_franjas):
        if trabaja[i, j].solution_value() == 1:
            estado = "Trabaja"
        elif pausa_activa[i, j].solution_value() == 1:
            estado = "Pausa Activa"
        elif almuerza[i, j].solution_value() == 1:
            estado = "Almuerza"
        else:
            estado = "Nada"
        horario_optimo = horario_optimo.append({"Empleado": f"E{i+1}", "Franja": j, "Estado": estado}, ignore_index=True)

# Guardar resultados en un archivo CSV
horario_optimo.to_csv("horario_optimo_parte1.csv", index=False)

