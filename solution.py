import csv
import os
import numpy as np
import time
from sortedcontainers import SortedList
from IntervalVisualizer import IntervalVisualizer


import config as conf
from data import Instance, BusLeg
from typing import List
from employee import Employee


class Solution:

    def __init__(self, employees: List[Employee]) -> None:
        self.employees = {employee.id: employee for employee in employees}
        self.value = 0
        self.change = 0

    def copy(self):
        employees_copy = [e.copy() for e in self.employees.values()]
        output = Solution(employees_copy)
        output.value = self.value
        return output

    def evaluate(self, instance: Instance) -> float:
        """ Evaluate the current solution.

        :return: the sum of every employee objective
        """
        self.value = 0
        for key, employee in self.employees.items():
            # self.evaluation += sum(employee.evaluate().values())
            self.value += employee.evaluate()
        return self.value

    def print_objective(self) -> None:
        print('\nCONSTRAINTS:')
        hard_constraints = 0
        soft_constraints = 0
        print('\nPROPERTIES:')
        for key, e in self.employees.items():
            print(' '+e.name+':')
            print('  bus_chain_penalty:', int(e.state.bus_penalty))
            print('  drive_time:', e.state.drive_time)
            print('  span:', e.state.total_time)
            print('  tour_changes:', e.state.change)
            print('  ride_time:', e.state.ride)
            print('  drive_penalty:', e.state.drive_penalty)
            print('  rest_penalty:', e.state.rest_penalty)
            print('  work_time:', e.state.work_time)
            print('  shift_split:', e.state.split)
        print('\nCONSTRAINTS:')
        for key, e in self.employees.items():
            print(f'  {e.name}: MultiValue({e.state.MultiValue})')
            hard_constraints += e.state.MultiValue[0]
            soft_constraints += e.state.MultiValue[1]
            for constraint in e.state.constraints:
                constraint.print_con()
        MultiValue = {0: hard_constraints, 1: soft_constraints}
        print(f' \nvalue: MultiValue:({MultiValue})')

    def print_to_file(self, file) -> None:
        """ Print the solution into the given file
            The output format is a binary matrix n x l where:
                n is the number of employee
                l is the number of bus legs (ordered by start time)
                the element (i,j) is 1 if leg j is assigned to employee i, 0 otherwise.
        """
        path = r'./solutions'
        if not os.path.exists(path):
            os.mkdir(path)
        os.chdir(r'./solutions')
        l = len(self.employees[1].instance.legs)
        n = len(self.employees)
        data = [[0 for _ in range(l)] for _ in range(n)]
        with open(file, 'w', newline='') as f:
            writer = csv.writer(f)
            for key, employee in self.employees.items():
                for leg in self.employees[1].instance.legs:
                    if leg in employee.bus_legs:
                        j = self.employees[1].instance.legs.index(leg)
                        data[key-1][j] = 1
                writer.writerow(data[key-1])
        f.close()

    def visualize(self):
        for i, e in self.employees.items():
            a = e.state.start_shift + 2*60
            b = e.state.end_shift - 2*60
            if e.working_constraints.break30 is True and e.working_constraints.first15 is True:
                for k, value in enumerate(e.bus_legs[:-1]):
                    if e.bus_legs[k].id is None:
                        continue
                    leg_i = e.bus_legs[k]
                    leg_j = e.bus_legs[k+1]
                    i = leg_i.end_pos
                    j = leg_j.start_pos
                    r = e.passive_ride(i, j)
                    if r > 0:
                        ride = BusLeg(None, 'R', leg_j.start - r, leg_j.start, 0, 0)
                        ride.name = 'ride'
                        e.bus_legs.add(ride)
                    if leg_i.end < e.state.start_shift + 2*60:
                        end_break = int(min(a, leg_j.start - r))
                        if end_break - leg_i.end >= 15:
                            paid = BusLeg(None, 'P', leg_i.end, end_break, 0, 0)
                            paid.name = 'paid'
                            e.bus_legs.add(paid)
                    if leg_j.start > e.state.end_shift - 2*60:
                        start_break = max(e.state.end_shift - 2*60, leg_i.end)
                        if leg_j.start - start_break >= 15:
                            paid = BusLeg(None, 'P', start_break, leg_j.start, 0, 0)
                            paid.name = 'paid'
                            e.bus_legs.add(paid)
                    if e.state.start_shift + 2*60 < leg_i.end and leg_j.start - r < e.state.end_shift - 2*60:
                        end_break = int(min(e.state.start_shift + 2*60, leg_j.start -r))
                        if leg_j.start- leg_i.end >= 15:
                            unpaid = BusLeg(None, 'U', leg_i.end, leg_j.start-r,  0, 0)
                            unpaid.name = 'U'
                            e.bus_legs.add(unpaid)
            #
            if e.state.start_shift != e.state.start_fs:
                start = BusLeg(None, 'S', e.state.start_shift, e.state.start_fs, 0, 0)
                start.name = 'Start'
                e.bus_legs.add(start)
            if e.state.end_shift != e.state.end_ls:
                end = BusLeg(None, 'E', e.state.end_ls, e.state.end_shift, 0, 0)
                end.name = ''
                e.bus_legs.add(end)
        def hover(interval):
            if getattr(interval, 'tour', None) == 'S':
                string = '<b>Start work​​​​​</b><br>' \
                    'Time: %{​​​​​start}​​​​​ - %{​​​​​end}​​​​​<br>'
                string = string.replace('\u200b', '')
                return string
            if getattr(interval, 'tour', None) == 'R':
                string = '<b>Ride time</b><br>' \
                        'Time: %{​​​​​start}​​​​​ - %{​​​​​end} ​​​​​   (drive: %{​​​​​drive}​​​​​)<br>'
                string = string.replace('\u200b', '')
                return string
            if getattr(interval, 'tour', None) == 'U':
                string = '<b>Unpaid​​​​​</b><br>' \
                        'Time: %{​​​​​start}​​​​​ - %{​​​​​end}​​​​​\
                            (drive: %{​​​​​drive}​​​​​)<br>'
                string = string.replace('\u200b', '')
                return string
            if getattr(interval, 'tour', None) == 'P':
                string = '<b>Paid​​​​​</b><br>' \
                        'Time: %{​​​​​start}​​​​​ - %{​​​​​end} \
                            (len: %{​​​​​drive}​​​​​)​​​​​<br>'
                string = string.replace('\u200b', '')
                return string
            if getattr(interval, 'tour', None) == 'E':
                string = '<b>End work​​​​​</b><br>' \
                        'Time: %{​​​​​start}​​​​​ - %{​​​​​end}<br>'
                string = string.replace('\u200b', '')
                return string

            if getattr(interval, 'tour', None) is not None:
                string = '<b>Bus leg %{​​​​​id}​​​​​</b><br>' \
                        'Time: %{​​​​​start}​​​​​ - %{​​​​​end}​​​​​ \
                        (drive: %{​​​​​drive}​​​​​)<br>' \
                        'Tour: %{​​​​​tour}​​​​​ <br>' \
                        'Positions: %{​​​​​start_pos}​​​​​ - %{​​​​​end_pos}​​​​​'
                string = string.replace('\u200b', '')
                return string
            else:
                string = '<b>%{​​​​​name}​​​​​</b><br>' \
                    'Time: %{​​​​​start}​​​​​ - %{​​​​​end}​​​​​'
                string = string.replace('\u200b', '')
                return string
        visualizer = IntervalVisualizer(axis=IntervalVisualizer.AXIS_HOURS)
        visualizer.create(self.employees, 'Results', 'tour', hover, 'tour').show()

    @staticmethod
    def from_file(instance: Instance, file):
        """Read a solution from the given file."""
        path = r'./solutions'
        file = path+'/'+file
        with open(file, 'r') as f:    
            f = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
            matrix = list(f) 
            matrix = [[int(matrix[i][j]) for j in range(len(matrix[0]))] for i in range(len(matrix))]
        employees = []
        numberOfLegs = len(instance.legs)
        for i in range(len(matrix)):
            employees.append(Employee(i+1, instance))
            # for key, leg in instance.legs:
            #     print(leg.id)
            for col in range(numberOfLegs):
                if matrix[i][col] == 1:
                    employees[i].bus_legs.add(instance.legs[col])    
        employees = sorted(employees, key=lambda x: x.bus_legs[0].start)        
        for i, employee in enumerate(employees):
            employee.id = i + 1
            employee.name = 'E' + str(i+1)
        solution = Solution(employees)
        return solution

    def execute_move(self, i: int, j: int, leg: BusLeg) -> float:
        """ Execute the move  [e_i, e_j, leg].

        :param i:   Index of first employee e1
        :param j:   Index of second employee e2
        :param leg: Leg that is removed from i, and added to j 
        :return: the new evaluation after executing the move
        if new_e1, new_e2 are the new employeers, the change is
            change = - z(old_e1) - z(old_e2) + z(new_e1) + z(new_e2)
        Hence, the new evaluation is
            newEval = oldEval + change
        """
        self.employees[i].bus_legs.remove(leg)
        self.employees[j].bus_legs.add(leg)
        self.change = -(self.employees[i].objective + self.employees[j].objective)
        # self.change += sum(self.employees[i].evaluate().values())
        # self.change += sum(self.employees[j].evaluate().values())
        self.change += self.employees[i].evaluate()
        self.change += self.employees[j].evaluate()
        self.value += self.change
        return self.value

    def revert(self, i: int, j: int, leg: BusLeg) -> None:
        """ Revert the move [e_i, e_j, leg] previously done.

        :param i:   Index of first employee e1
        :param j:   Index of second employee e2
        :param leg: Leg that is added to i, and removed to j        
        :return: the old evaluation, after reverting the move
        """

        self.employees[i].bus_legs.add(leg)
        self.employees[i].revert()
        self.employees[j].bus_legs.remove(leg)
        self.employees[j].revert()
        self.value-= self.change
        return self.value

    def removeEmptyEmployees(self):
        """ Remove all the employees tha has empty bus legs """
        employees = []
        for key, employee in self.employees.items():
            if employee.objective > 0:
                employees.append(employee)
        outputSolution = Solution(employees)
        return outputSolution
        