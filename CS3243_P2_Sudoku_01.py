# CS3243 Introduction to Artificial Intelligence
# Project 2, Part 1: Sudoku

import sys
import copy

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class Sudoku(object):
    def __init__(self, puzzle):
        self.puzzle = puzzle  # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle)  # self.ans is a list of lists
        self.neighbourCells = {}

    def solve(self):
        self.start()
        self.backtrackAlgo(self.puzzle)
        self.convert()
        return self.ans

    # Create domains for all the cells and establish constraints
    # Ensure initial cells with value != 0 to have the fix value
    #Domain = {1 - 9}
    def start(self):
        temp = [range(9) for i in range(9)]
        for row in range(9):
            for col in range(9):
                temp[row][col] = set()
                for i in range(9):
                    temp[row][col].add(i + 1)
                neighbourCellsTemp = self.connectedCells(puzzle, (row, col))
                self.neighbourCells[(row, col)] = neighbourCellsTemp

        for row in range(9):
            for col in range(9):
                if self.puzzle[row][col] != 0:
                    self.forwardChecking(temp, (row, col), self.puzzle[row][col])
        self.puzzle = temp
 
    # Establish Connections between each cells for same row/ column/ box
    def connectedCells(self, puzzle, pos):
        (row, col) = pos
        connectedCellsList = list()
        #Same row
        for colV in range(9): 
            if colV != col: connectedCellsList.append((row, colV))
        #Same col
        for row_value in range(9):
            if row_value != row: connectedCellsList.append((row_value, col))
        #Same box
        top_rowbox = 3 * (row // 3)  
        top_colbox = 3 * (col // 3)
        for rowV in range(top_rowbox, top_rowbox + 3):
            for colV in range(top_colbox, top_colbox + 3):
                if rowV != row and colV != col:
                    connectedCellsList.append((rowV, colV))
        return connectedCellsList

    #Backtracking algorithm with MRV, LCV and Forward Checking
    def backtrackAlgo(self, puzzle):

        #Check if any existing domain size = 1, if there is, then the value must be assigned to the variable
        if not self.checkDomain(puzzle):
            return False

        (MRV_row, MRV_col) = self.MRV(puzzle) # Using MRV
        MRV_variable = (MRV_row, MRV_col)
        if MRV_row == -1 and MRV_col == -1:
            self.puzzle = puzzle
            return True

        LCV_Order = self.LCV(MRV_variable, puzzle) #Using Least Constraining Value

        #for value, frequency in ordered_domain_values:
        for value in LCV_Order:
            current_puzzle = copy.deepcopy(puzzle)
            current_puzzle[MRV_row][MRV_col] = set()
            current_puzzle[MRV_row][MRV_col].add(value[0])
            if not self.forwardChecking(current_puzzle, (MRV_row, MRV_col), value[0]):
                continue
            if self.backtrackAlgo(current_puzzle):
                return True
        return False
            
    #Minimum Remaining Value Heuristic
    def MRV(self, puzzle):
        mrv = 10
        mrv_pos = (-1, -1)
        for row in range(9):
            for col in range(9):
                numbers = puzzle[row][col]
                if len(numbers) < mrv and len(numbers) != 1:
                    mrv = len(numbers)
                    mrv_pos = (row, col)
        return mrv_pos
 
    # least constraining value heuristic.
    def LCV(self, pos, puzzle):
        (row, col) = pos
        values = puzzle[row][col]
        connectingCellPos = list()
        for neighbour in self.neighbourCells.get(pos):
            (n_Row, n_Col) = neighbour
            if len(puzzle[n_Row][n_Col]) != 1:
                connectingCellPos.append((n_Row, n_Col))
        LCV_tuple = []
        for value in values:
            constrainingValue = 0
            for (connected_Row, connected_Col) in connectingCellPos:
                if value in puzzle[connected_Row][connected_Col]:
                    constrainingValue += 1
            LCV_tuple.append((value, constrainingValue))
        LCV_tuple.sort(key = lambda tup: tup[1])
        return LCV_tuple


    # Assign value to variable and reduce domain of neigbouring cells.
    def forwardChecking(self, puzzle, pos, val):
        (row, col) = pos
        puzzle[row][col] = set()
        puzzle[row][col].add(val)
        listOfConnectingCells = self.neighbourCells.get(pos)
        for rowV, colV in listOfConnectingCells:
            if val in puzzle[rowV][colV]:
                puzzle[rowV][colV].remove(val)
                if len(puzzle[rowV][colV]) == 1:
                    for valRemaining in puzzle[rowV][colV]:
                        tempPos = (rowV, colV)
                        if self.forwardChecking(puzzle, tempPos, valRemaining) == False:
                            return False
            if len(puzzle[rowV][colV]) == 0:
                return False
        return True

    #Check for any domain with size of 1
    def checkDomain(self, puzzle):

        #Check row: If domain only have 1 value (Size of domain = 1), the value must be assigned to the variable
        for row in range(9):
            count = {}
            pos = {}
            for col in range(9):
                if len(puzzle[row][col]) == 1:
                    val = (puzzle[row][col]).pop()
                    puzzle[row][col].add(val)
                    count[val] = -1000
                for value in puzzle[row][col]:
                    if value not in count:
                        count[value] = 1
                    else:
                        count[value] = count[value] + 1
                    pos[value] = col
            for i in range(1, 10):
                if i in count and i in pos:
                    if count[i] == 1:
                        tempPos = (row, pos[i])
                        if not self.forwardChecking(puzzle, tempPos, i):
                            return False

        #Check column: If domain only have 1 value (Size of domain = 1), the value must be assigned to the variable
        for col in range(9):
            count = {}
            pos = {}
            for row in range(9):
                if len(puzzle[row][col]) == 1:
                    val = (puzzle[row][col]).pop()
                    puzzle[row][col].add(val)
                    count[val] = -1000

                for value in puzzle[row][col]:
                    if value not in count:
                        count[value] = 1
                    else:
                        count[value] = count[value] + 1
                    pos[value] = row
            for i in range(1, 10):
                if i in count and i in pos:
                    if count[i] == 1:
                        tempPos = (pos[i], col)
                        if not self.forwardChecking(puzzle, tempPos, i):
                            return False

        #Check 3x3 box: If domain only have 1 value (Size of domain = 1), the value must be assigned to the variable
        small_box = []
        big_box = []
        box_list = []

        for i in range(3):
            for j in range(3):
                small_box.append((i,j))
                big_box.append((i * 3, j * 3))
        for bb in big_box:
            boxes = []
            for sb in small_box:
                boxes.append((sb[0] + bb[0], sb[1] + bb[1]))
            box_list.append(boxes)
        
        for sb in box_list:
            count = {}
            pos = {}
            for box in sb:
                row = box[0]
                col = box[1]
                if len(puzzle[row][col]) == 1:
                    val = (puzzle[row][col]).pop()
                    puzzle[row][col].add(val)
                    count[val] = -1000
                for value in puzzle[row][col]:
                    if value not in count:
                        count[value] = 1
                    else:
                        count[value] = count[value] + 1
                    pos[value] = box
            for i in range(1, 10):
                if i in count and i in pos:
                    if count[i] == 1:
                        if not self.forwardChecking(puzzle, pos[i], i):
                            return False
            return True       

    # Converts from values in a set to values for list.
    def convert(self):
        for row in range(9):
            for col in range(9):
                for val in self.puzzle[row][col]:
                    self.ans[row][col] = val

if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise IOError("Input file not found!")

    puzzle = [[0 for i in range(9)] for j in range(9)]
    lines = f.readlines()

    i, j = 0, 0
    for line in lines:
        for number in line:
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0

    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()

    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
