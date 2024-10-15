#Nombre:
#Juan Pablo Charry Ramirez 

class Proceso:
    def __init__(self, etiqueta, burst_time, arrival_time, queue, priority):
        # Inicializamos un proceso con sus atributos principales
        self.etiqueta = etiqueta  # Identificador del proceso
        self.burst_time = burst_time  # Tiempo que requiere el proceso para completarse
        self.remaining_time = burst_time  # Tiempo restante (se usa para RR)
        self.arrival_time = arrival_time  # Momento en que el proceso llega al sistema
        self.queue = queue  # Cola a la que pertenece (nivel de prioridad)
        self.priority = priority  # Prioridad del proceso
        self.wait_time = 0  # Tiempo total de espera del proceso
        self.completion_time = 0  # Tiempo en que el proceso se completa
        self.response_time = None  # Tiempo de respuesta (primera vez que se ejecuta)
        self.turnaround_time = 0  # Tiempo total desde la llegada hasta que termina el proceso

    def __repr__(self):
        # Representación del proceso para depuración y pruebas
        return f"Proceso({self.etiqueta}, BT={self.burst_time}, AT={self.arrival_time}, Q={self.queue}, Pr={self.priority})"


class Cola:
    def __init__(self, tipo, quantum=None):
        # Inicializa una cola con su tipo de algoritmo y el quantum (si aplica)
        self.tipo = tipo  # Tipo de algoritmo (RR, FCFS)
        self.procesos = []  # Lista de procesos que pertenecen a esta cola
        self.quantum = quantum  # Quantum para Round Robin (RR), si aplica

    def agregar_proceso(self, proceso):
        # Agrega un proceso a la cola
        self.procesos.append(proceso)

    def ejecutar_rr(self, quantum, tiempo_actual):
        # Implementa la planificación Round Robin (RR) para la cola
        if not self.procesos:
            return tiempo_actual
        while self.procesos:
            proceso = self.procesos.pop(0)  # Obtener el primer proceso de la cola
            if proceso.response_time is None:
                # Si es la primera vez que el proceso se ejecuta, establecer el tiempo de respuesta
                proceso.response_time = max(0, tiempo_actual - proceso.arrival_time)
            if proceso.remaining_time > quantum:
                # Si el proceso necesita más tiempo que el quantum, restar el quantum y reinsertarlo en la cola
                proceso.remaining_time -= quantum
                tiempo_actual += quantum
                self.procesos.append(proceso)
            else:
                # Si el proceso puede completarse en este ciclo, actualizar tiempos
                tiempo_actual += proceso.remaining_time
                proceso.remaining_time = 0
                proceso.completion_time = tiempo_actual
                proceso.turnaround_time = proceso.completion_time - proceso.arrival_time
                proceso.wait_time = proceso.turnaround_time - proceso.burst_time
        return tiempo_actual

    def ejecutar_fcfs(self, tiempo_actual):
        # Implementa la planificación First Come First Served (FCFS) para la cola
        if not self.procesos:
            return tiempo_actual
        for proceso in self.procesos:
            if proceso.response_time is None:
                # Si es la primera vez que el proceso se ejecuta, establecer el tiempo de respuesta
                proceso.response_time = max(0, tiempo_actual - proceso.arrival_time)
            tiempo_actual += proceso.burst_time
            proceso.completion_time = tiempo_actual
            proceso.turnaround_time = proceso.completion_time - proceso.arrival_time
            proceso.wait_time = proceso.turnaround_time - proceso.burst_time
        self.procesos.clear()  # Limpiar la cola después de procesar todos los procesos
        return tiempo_actual

    def ejecutar(self, tiempo_actual):
        # Decide qué tipo de planificación ejecutar según el tipo de cola (RR o FCFS)
        if self.tipo == 'RR':
            return self.ejecutar_rr(self.quantum, tiempo_actual)
        elif self.tipo == 'FCFS':
            return self.ejecutar_fcfs(tiempo_actual)


class MLQScheduler:
    def __init__(self):
        # Inicializa el planificador MLQ con una lista de colas
        self.colas = []  # Las colas se agregarán a esta lista

    def agregar_cola(self, cola):
        # Agrega una cola al planificador MLQ
        self.colas.append(cola)

    def planificar(self):
        # Ejecuta las colas en el orden de prioridad
        tiempo_actual = 0  # El tiempo actual en el que el sistema está operando
        for cola in self.colas:
            # Ejecuta cada cola en el orden en que se añadieron
            tiempo_actual = cola.ejecutar(tiempo_actual)


# Lectura del archivo de entrada
def leer_entrada(nombre_archivo):
    # Lee los procesos desde un archivo y los devuelve como una lista de objetos Proceso
    procesos = []
    with open(nombre_archivo, 'r') as archivo:
        for linea in archivo:
            if linea.startswith("#") or not linea.strip():
                continue  # Ignorar comentarios y líneas vacías
            datos = linea.split(";")
            etiqueta, bt, at, q, pr = datos[0], int(datos[1]), int(datos[2]), int(datos[3]), int(datos[4])
            proceso = Proceso(etiqueta, bt, at, q, pr)
            procesos.append(proceso)
    return procesos


# generar_salida.py
def generar_salida(procesos, nombre_salida):
    # Genera el archivo de salida con los resultados de la planificación
    with open(nombre_salida, 'w') as archivo:
        archivo.write("# etiqueta; BT; AT; Q; Pr; WT; CT; RT; TAT\n")
        
        total_wt = 0  # Tiempo total de espera
        total_ct = 0  # Tiempo total de completado
        total_rt = 0  # Tiempo total de respuesta
        total_tat = 0  # Tiempo total de turnaround time
        num_procesos = len(procesos)
        
        for proceso in procesos:
            # Escribir cada proceso con sus tiempos calculados
            archivo.write(f"{proceso.etiqueta};{proceso.burst_time};{proceso.arrival_time};"
                          f"{proceso.queue};{proceso.priority};{proceso.wait_time};"
                          f"{proceso.completion_time};{proceso.response_time};{proceso.turnaround_time}\n")
            # Acumulando los valores para cada métrica
            total_wt += proceso.wait_time
            total_ct += proceso.completion_time
            total_rt += proceso.response_time
            total_tat += proceso.turnaround_time

        # Promedios de las métricas
        promedio_wt = total_wt / num_procesos
        promedio_ct = total_ct / num_procesos
        promedio_rt = total_rt / num_procesos
        promedio_tat = total_tat / num_procesos

        archivo.write(f"\nWT={promedio_wt:.1f}; CT={promedio_ct:.1f}; "
                      f"RT={promedio_rt:.1f}; TAT={promedio_tat:.1f};\n")


# Funcion Main
if __name__ == "__main__":
    # Crear el planificador MLQ con el esquema seleccionado: RR(3), RR(5), FCFS
    mlq_scheduler = MLQScheduler()

    # Configurar las colas
    mlq_scheduler.agregar_cola(Cola('RR', quantum=3))  # Cola 1: Round Robin con quantum 3
    mlq_scheduler.agregar_cola(Cola('RR', quantum=5))  # Cola 2: Round Robin con quantum 5
    mlq_scheduler.agregar_cola(Cola('FCFS'))  # Cola 3: First Come First Served

    # Leer los procesos desde el archivo
    procesos = leer_entrada('mlq010.txt')

    # Asignar los procesos a las colas según su atributo 'queue'
    for proceso in procesos:
        if proceso.queue == 1:
            mlq_scheduler.colas[0].agregar_proceso(proceso)
        elif proceso.queue == 2:
            mlq_scheduler.colas[1].agregar_proceso(proceso)
        elif proceso.queue == 3:
            mlq_scheduler.colas[2].agregar_proceso(proceso)

    # Ejecutar la planificación
    mlq_scheduler.planificar()

    # Generar el archivo de salida
    generar_salida(procesos, 'salida_mlq.txt')
