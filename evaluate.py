import os 
import csv
import math
import time
import logging


from main import main
from algorithm import ConstructionAlgorithm
from data import Instance

if __name__ == '__main__':

    f = '%(asctime)s|%(levelname)s|%(name)s|%(message)s'
    logging.basicConfig(level=logging.INFO, filename='algorithm.log', encoding='utf-8', format=f)
    formatter = logging.Formatter(f)
    logger = logging.getLogger()

    for h in logger.handlers:
                if isinstance(h, logging.FileHandler):
                    logger.removeHandler(h)
    handler = logging.FileHandler('algorithm.log', 'w')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    instance_number = 4
    instance_size = 10 * math.ceil(instance_number / 5)
    tabu_length = math.floor(math.sqrt(instance_size))
    f = f'realistic_{instance_size}_{instance_number}_solution.csv'
    result =  main(instance_number, tabu_length, f )


# if __name__ == '__main__':
#     with open('benchmark_Tommaso.csv', mode='w', newline='') as csv_file:
#         writer = csv.writer(csv_file)
#         writer.writerow(['','construction', '','', 'Tabu Search' ])
#         writer.writerow(['instance', 'time', 'employees', 'value', 'time', 'employees', 'value', 'moves tried', 'tabu length'])
#         for instance_number in range(1, 2):
#             instance_size = 10*math.ceil(instance_number/5)
#             best_solution = 10**20
#             # Initial solution
#             owd = os.getcwd()
#             os.chdir(r'./busdriver_instances')
#             instance = Instance.read_data(instance_size, instance_number)
#             os.chdir(owd)
#             # algorithm = Algorithm(instance)
#             start = time.process_time()
#             initial_solution = ConstructionAlgorithm(instance).apply()
#             initial_solution.evaluate(instance)
#             duration_initial = time.process_time() - start
#             initialEmployees = len(initial_solution.employees)
#             initialObjective = initial_solution.value
#             finalObjective, numberOfEmployees, duration, number_of_iterations, final_solution = main(initial_solution, instance_size, instance_number, 5)
#             if finalObjective < best_solution:
#                 best_solution = finalObjective
#                 # final_solution.print_to_file(f'realistic_{instance_size}_{instance_number}_solution.csv')
#             data = [f'realistic_{instance_size}_{instance_number}', duration_initial, initialEmployees, initialObjective,  duration, numberOfEmployees,  finalObjective,
#             number_of_iterations, '5']
#             writer.writerow(data)
#             print(f'realistic_{instance_size}_{instance_number}')
#             for tabu_length in [10, 20]:
#                 finalObjective, numberOfEmployees, duration, number_of_iterations, final_solution = main(initial_solution, instance_size, instance_number, tabu_length)
#                 if finalObjective < best_solution:
#                     best_solution = finalObjective
#                     # final_solution.print_to_file(f'realistic_{instance_size}_{instance_number}_solution.csv')
#                 data = ['', '', '', '',  duration, numberOfEmployees,  finalObjective,
#                             number_of_iterations, tabu_length]
#                 writer.writerow(data)
#                 print(f'realistic_{instance_size}_{instance_number}')
#             # writer.writerow([instance_size])
#                 # os.chdir("..")
