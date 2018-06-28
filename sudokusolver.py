!#/usr/bin/python3

import copy

FOUND_COLOR = "1;34;40"
UNKNOWN_COLOR = "1;31;40"
NULL_COLOR = "0"

def main():
    puzzle_definition = (
                        # "xxxxxx36x\n"
                        # "xx46x7x52\n"
                        # "x5xxxxxx8\n"
                        # "x4xx3xx9x\n"
                        # "xxx819xxx\n"
                        # "x6xx5xx8x\n"
                        # "3xxxxxx4x\n"
                        # "79x4x12xx\n"
                        # "x86xxxxxx\n"
                        #
                        # "x69xxx5xx\n"
                        # "1xx8xxxxx\n"
                        # "3xxx72xx8\n"
                        # "x9xxx58xx\n"
                        # "xx7xxx3xx\n"
                        # "xx86xxx1x\n"
                        # "5xx23xxx9\n"
                        # "xxxxx9xx1\n"
                        # "xx6xxx75x\n"
                        #
                        "x7x2x8xx9\n"
                        "6xxxx1x2x\n"
                        "xxx3xx5xx\n"
                        "1x8xx5x97\n"
                        "xxxxxxxxx\n"
                        "59x6xx1x2\n"
                        "xx4xx6xxx\n"
                        "x6x8xxxx4\n"
                        "2xx1x4x8x\n"
                        )
    
    puzzle_matrix = parse_table_to_matrix(puzzle_definition)
    #puzzle_history_stack = list()
    history_stack = list()
    current_puzzle = Puzzle(puzzle_matrix)
    iteration_count = 0
    
    while (True):
        iteration_count = iteration_count + 1
        print("Iteration #" + str(iteration_count))
        current_puzzle.find_possibilities()
        possibilities = current_puzzle.get_possibilities()
        non_empty_possibilities = [item for item in possibilities if item.possibilities_count > 0]
        non_empty_possibilities.sort(key=lambda item: item.possibilities_count) # sort by length of possibilities set
        possibilities_count = len(non_empty_possibilities)
        #print("Remaining possibilities: " + str(possibilities_count))
        if possibilities_count > 0:
            # logic here
            most_likely_possibility = non_empty_possibilities.pop(0)
            cell_possibility_list = most_likely_possibility.possibilities
            if most_likely_possibility.possibilities_count == 1:
                # only one possibility
                chosen_possibility = cell_possibility_list.pop()
            else:
                # multiple possibilities (no possibilities shouldn't be possible)
                print("More than one choice found; Branching...")
                chosen_possibility = cell_possibility_list.pop()
                history_stack.append(HistoryItem(current_puzzle, most_likely_possibility.row_index, most_likely_possibility.column_index, cell_possibility_list))
                
            current_puzzle.set_cell_value(most_likely_possibility.row_index, most_likely_possibility.column_index, chosen_possibility) #set on a possibility and loop
            
        elif current_puzzle.is_complete():
            print("Puzzle complete:")
            current_puzzle.print_puzzle(puzzle_matrix)
            break;
        else:
            print("Dead end path. Backing out and trying again")
            latest_history = peek(history_stack)
            if len(history_stack) == 0:
                print("Error: Could not find solution!")
                current_puzzle.print_puzzle(puzzle_matrix)
                return;
                
            current_puzzle = latest_history.get_puzzle()
            chosen_possibility = latest_history.get_next_possibility()
            row_index, column_index = latest_history.get_indexes()
            current_puzzle.set_cell_value(row_index, column_index, chosen_possibility) #set on a possibility and try again
            if latest_history.is_empty():
                history_stack.pop() # pop empty history off the history stack
            
            
class HistoryItem:
    def __init__(self, puzzle, row_index, column_index, possibilities):
        self.puzzle = puzzle.clone()
        self.row_index = row_index
        self.column_index = column_index
        self.possibilities = list(possibilities)
        
    def get_next_possibility(self):
        return self.possibilities.pop()
        
    def is_empty(self):
        return len(self.possibilities) == 0
        
    def get_puzzle(self):
        return self.puzzle.clone()
        
    def get_indexes(self):
        return self.row_index, self.column_index
            
class Puzzle:
    
    def __init__(self, cell_matrix, row_known_values = None, column_known_values = None, square_known_values = None):
        self.cell_matrix = list() # list of lists containing cells
        self.possibilities = None
        
        for row_index, row in enumerate(cell_matrix):
            cell_row = list()
            self.cell_matrix.append(cell_row)
            for column_index, cell_value in enumerate(row):
                cell_row.append(cell_value)
                
        if row_known_values != None and column_known_values != None and square_known_values != None:

            self.row_known_values = dict(row_known_values)
            for key, val in self.row_known_values.items():
                self.row_known_values[key] = set(val)
                
            self.column_known_values = dict(column_known_values)
            for key, val in self.column_known_values.items():
                self.column_known_values[key] = set(val)

            self.square_known_values = dict(square_known_values)
            for key, val in self.square_known_values.items():
                self.square_known_values[key] = set(val)
                
        else:
            self.row_known_values = None
            self.column_known_values = None
            self.square_known_values = None
            self.reset_known_values()
            self.find_known_values()
                
    def get_possibilities(self):
        #possibility_tuples = list()
        return_possibilities = list()
        for row_index in range(0, 9):
            for column_index in range(0, 9):
                possibility_set = self.possibilities[row_index][column_index]
        #        possibility_tuples.append((row_index, column_index, len(possibility_set), list(possibility_set)))
                return_possibilities.append(Puzzle.PuzzlePossibility(row_index, column_index, list(possibility_set)))
        #return possibility_tuples
        return return_possibilities
                
    def find_possibilities(self):
        cell_base_set = {1, 2, 3, 4, 5, 6, 7, 8, 9}
        self.possibilities = list()
        for row_index in range(0, 9):
            row_list = list()
            self.possibilities.append(row_list)
            for column_index in range(0, 9):
                square_column_index = column_index // 3
                square_row_index = row_index // 3
                square_index = square_row_index * 3 + square_column_index
                row_list.append(set() if self.cell_matrix[row_index][column_index] != None else cell_base_set - (self.row_known_values[row_index] | self.column_known_values[column_index] | self.square_known_values[square_index]))
        
                
    def reset_known_values(self):
        self.row_known_values = {}
        self.column_known_values = {}
        self.square_known_values = {}
                
    def find_known_values(self):
        for row_index in range(0, 9):
            row_known_values = self.row_known_values.get(row_index, None)
            if row_known_values == None:
                self.row_known_values[row_index] = row_known_values = set()
                for column_index in range(0, 9):
                    cell = self.cell_matrix[row_index][column_index]
                    if cell != None:
                        row_known_values.add(cell)
                            
        for column_index in range (0, 9):
            column_known_values = self.column_known_values.get(column_index, None)
            if column_known_values == None:
                self.column_known_values[column_index] = column_known_values = set()
                for row_index in range(0, 9):
                    cell = self.cell_matrix[row_index][column_index]
                    if cell != None:
                        column_known_values.add(cell)
        
        for row_index in range(0, 9):
            for column_index in range(0, 9):
                square_column_index = column_index // 3
                square_row_index = row_index // 3
                square_index = square_row_index * 3 + square_column_index
                square_known_values = self.square_known_values.get(square_index, None)
                if square_known_values == None:
                    square_known_values = self.square_known_values[square_index] = set()
        
                    for row_index in range(square_row_index * 3, square_row_index * 3 + 3):
                        for column_index in range(square_column_index * 3, square_column_index * 3 + 3):
                            cell = self.cell_matrix[row_index][column_index]
                            if cell != None:
                                square_known_values.add(cell)
        
    def set_cell_value(self, row_index, column_index, value):
        self.cell_matrix[row_index][column_index] = value;
        new_value_set = {value}
        self.row_known_values[row_index] = self.row_known_values[row_index] | new_value_set
        self.column_known_values[column_index] = self.column_known_values[column_index] | new_value_set
        square_column_index = column_index // 3
        square_row_index = row_index // 3
        square_index = square_row_index * 3 + square_column_index
        self.square_known_values[square_index] = self.square_known_values[square_index] | new_value_set
        
    def print_puzzle(self, start_matrix = None):
        global FOUND_COLOR
        global UNKNOWN_COLOR
        global NULL_COLOR
        for row_index in range(0, 9):
            for column_index in range(0, 9):
                cell_value = self.cell_matrix[row_index][column_index]
                spacer = "\n\n" if column_index == 8 and row_index % 3 == 2 else "\n" if column_index == 8 else "  " if column_index % 3 == 2 else " "
                color = UNKNOWN_COLOR if cell_value == None else FOUND_COLOR if start_matrix != None and start_matrix[row_index][column_index] != cell_value else NULL_COLOR
                #color_print(cell_value if cell_value != None else " ", color, end=spacer)
                print(cell_value if cell_value != None else "X", end=spacer)
                
    def clone(self):
        return Puzzle(self.cell_matrix, self.row_known_values, self.column_known_values, self.square_known_values)
        
    def is_complete(self):
        return len([item for sublist in self.cell_matrix for item in sublist if item != None]) == 81
        
    class PuzzlePossibility:
        def __init__(self, row_index, column_index, possibility_list):
            self.row_index = row_index
            self.column_index = column_index
            self.possibilities_count = len(possibility_list)
            self.possibilities = possibility_list
        
def color_print(text, color = "0", end="\n"):
    print("\x1b[%sm %s \x1b[0m" % (color, text), end=end)
    
def parse_table_to_matrix(table_string):
    matrix_list = list()
    current_sub_list = list()
    matrix_list.append(current_sub_list)
    for char in table_string:
        if char == "\n":
            current_sub_list = list()
            matrix_list.append(current_sub_list)
        elif char == " " or char == "x":
            current_sub_list.append(None)
        else:
            current_sub_list.append(int(char))
            
    return matrix_list
    
def peek(list, index = None):
    length = len(list)
    if length == 0:
        return None
    else:
        return list[(length - 1) if index == None else index]

if __name__ == "__main__":
    main()