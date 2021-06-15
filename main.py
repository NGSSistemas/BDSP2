import time
import logging
import sys
import os
import csv
import math

from data import Instance
from algorithm import Algorithm, ConstructionAlgorithm, TabuSearch
from solution import Solution
import config as conf
from IntervalVisualizer import IntervalVisualizer




def main(instance_number, tabu_tenure, solution_file=None):
    instance_size = 10 * math.ceil(instance_number / 5)
    owd = os.getcwd()
    os.chdir(r'./busdriver_instances')
    instance = Instance.read_data(instance_size, instance_number)
    os.chdir(owd)
    logger = logging.getLogger(__name__)
    # ---------------------- #
    # CONSTRUCTIVE ALGORITHM #
    # ---------------------- # 
    logger.info(f'Executing constructive algorithm on instance {instance_number}')
    start = time.process_time()
    initial_solution = ConstructionAlgorithm(instance).apply()
    duration = time.process_time() - start
    initial_solution.evaluate(instance)
    logger.info(f'Finished execution in {duration} with value {initial_solution.value}')    
    # initial_solution.print_objective()

    # -------------- #
    # READ FROM FILE #
    # -------------- # 

    # file = f'realistic_{instance_size}_{instance_number}_solution.csv' 
    # initial_solution = Solution.from_file(instance, file)
    # initial_solution.evaluate(instance)
    # initial_solution.print_objective()



    # ----------- #
    # TABU SEARCH #
    # ----------- # 

    start = time.process_time()
    tabu_search = TabuSearch(instance)
    best_objective, solution, number_of_iterations = tabu_search.apply(initial_solution, tabu_tenure)
    duration = time.process_time() - start
    solution = solution.removeEmptyEmployees()
    solution.evaluate(instance)
    # logger.info(f'Finished execution in {duration} with value {best_objective}')

    # solution.print_objective()
    # best_solution.print_to_file()


    # best_solution = algorithm.local_search(solution)
    # print('initial solution = ',solution.evaluation)
    # best_solution, best_evaluation = algorithm.best_improvement(solution)
    # print('best improvement = ', best_evaluation)
    # best_solution.evaluate(instance)
    # print(solution.move())
    # best_solution.print_objective()
    # solution.print_objective()
    if solution_file is not None:
        solution.print_to_file(solution_file)

    return solution.value, len(solution.employees), duration, number_of_iterations, solution


if __name__ == '__main__':

    f = '%(asctime)s|%(levelname)s|%(name)s|%(message)s'
    logging.basicConfig(level=logging.INFO, filename='algorithm.log', encoding='utf-8', format=f)
    