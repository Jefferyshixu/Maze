# COMP9021 24T1
# Assignment 2 *** Due Monday Week 11 @ 10.00am

# DO *NOT* WRITE YOUR NAME TO MAINTAIN ANONYMITY FOR PLAGIARISM DETECTION


# IMPORT ANY REQUIRED MODULE
from pprint import pprint

class MazeError(Exception):
    def __init__(self, message):
        self.message = message


class Maze:
    def __init__(self, filename):
        self.filename = filename
        self.grid = []
        self.read_and_check_file()
        self.row_num = len(self.grid)
        self.col_num = len(self.grid[0])
    
    
    def read_and_check_file(self):
        with open(self.filename) as file:
            for line in file:
                line_list = list(line.strip().replace(" ", ""))
                if len(line_list) != 0:
                    self.grid.append(line_list)
        
        if len(self.grid) not in range(2, 42):
            raise MazeError("Incorrect input.")
        
        row_lengths = [len(row) for row in self.grid]
        if len(set(row_lengths)) != 1 or len(self.grid[0]) not in range(2, 32):
            raise MazeError("Incorrect input.")
        
        for row in self.grid:
            if not set(row) <= {"0", "1", "2", "3"}:
                raise MazeError("Incorrect input.")
        
        last_row = self.grid[-1]
        last_col = [row[-1] for row in self.grid]

        error = False
        for char in last_row:
            if char != "0" and char != "1":
                error = True
                break
        for character in last_col:
            if character != "0" and character != "2":
                error = True
                break

        if error:
            raise MazeError("Input does not represent a maze.")

        # if (not set(last_row) <= {"0", "1"}) or (not set(last_col) <= {"0", "2"}):
        #     raise MazeError("Input does not represent a maze.")

            
    def analyse(self):
        self.analyze_gate()
        self.analyze_wall()
        self.find_ways()
        self.print_info()
    
    
    def print_info(self):
        if len(self.gates) == 0:
            print("The maze has no gate.")
        elif len(self.gates) == 1:
            print("The maze has a single gate.")
        else:
            print(f"The maze has {len(self.gates)} gates.")
            
        if self.walls_num == 0:
            print("The maze has no wall.")
        elif self.walls_num == 1:
            print("The maze has walls that are all connected.")
        else:
            print(f"The maze has {self.walls_num} sets of walls that are all connected.")
        
        if self.inaccessible_count == 0:
            print("The maze has no inaccessible inner point.")
        elif self.inaccessible_count == 1:
            print("The maze has a unique inaccessible inner")
        else:
            print(f"The maze has {self.inaccessible_count} inaccessible inner points.")
            
        if self.accessible_area == 0:
            print("The maze has no accessible area.")
        elif self.accessible_area == 1:
            print("The maze has a unique accessible area.")
        else:
            print(f"The maze has {self.accessible_area} accessible areas.")
        
        if self.cul_de_sacs_count == 0:
            print("The maze has no accessible cul-de-sac.")
        elif self.cul_de_sacs_count == 1:
            print("The maze has accessible cul-de-sacs that are all connected.")
        else:
            print(f"The maze has {self.cul_de_sacs_count} sets of accessible cul-de-sacs that are all connected.")
        
        if len(self.entry_exit_paths) == 0:
            print("The maze has no entry-exit path with no intersection not to cul-de-sacs.")
        elif len(self.entry_exit_paths) == 1:
            print("The maze has a unique entry-exit path with no intersection not to cul-de-sacs.")
        else:
            print(f"The maze has {len(self.entry_exit_paths)} entry-exit paths with no intersections not to cul-de-sacs.")
        
    
    def find_ways(self):        
        self.row_col_diff = {0: (0, 1), 1: (1, 0), 2: (0, -1), 3: (-1, 0)}
        self.reverse_direction = {0: 2, 1: 3, 2: 0, 3: 1}
        self.generate_direction_grid()
        self.accessible_area = 0
        self.searched_point = set()
        self.entry_exit_paths = []
        
        tested_gates = []
        for gate in self.gates:
            if gate in tested_gates:
                continue
            self.accessible_area += 1
            first_point = self.gate_to_point(gate)
            
            current_path = [gate]
            paths = []
            exit_gates = self.get_exit_gates(paths, first_point, current_path.copy())
            if len(exit_gates) == 1:
                shorted_path = sorted(paths, key=lambda x: len(x))[0]
                self.entry_exit_paths.append(shorted_path)
            for exit_gate in exit_gates:
                tested_gates.append(exit_gate)
        print("ACC", self.accessible_area)
        print("Searched Point", len(self.searched_point))
        print("Total Point", (self.row_num - 1) * (self.col_num - 1))

        total_points = (self.row_num - 1) * (self.col_num - 1)
        self.inaccessible_count = total_points - len(self.searched_point)
        
        self.cul_de_sacs_count = 0
        self.cul_de_sacs_points = []
        for point in self.searched_point:
            if self.direction_grid[point[0]][point[1]].count(True) == 1:
                self.cul_de_sacs_points.append(point)
                self.cul_de_sacs_count += 1
        
        temp_direction_grid = []
        for row in range(self.row_num - 1):
            one_line = []
            for col in range(self.col_num - 1):
                one_line.append(self.direction_grid[row][col].copy())
            temp_direction_grid.append(one_line)
        
        while True:
            start_point_number = len(self.cul_de_sacs_points)
            for point in self.cul_de_sacs_points:
                available_directions = temp_direction_grid[point[0]][point[1]]
                if True not in available_directions:
                    continue
                direction_index = available_directions.index(True)
                temp_direction_grid[point[0]][point[1]][direction_index] = False
                row_diff, col_diff = self.row_col_diff[direction_index]
                next_row = point[0] + row_diff
                next_col = point[1] + col_diff
                if (next_row, next_col) in self.gates:
                    continue
                reverse_direction_index = self.reverse_direction[direction_index]
                temp_direction_grid[next_row][next_col][reverse_direction_index] = False
            
            for point in self.searched_point:
                if point in self.cul_de_sacs_points:
                    continue
                if temp_direction_grid[point[0]][point[1]].count(True) == 1:
                    self.cul_de_sacs_points.append(point)
                    previous_directions = self.direction_grid[point[0]][point[1]]
                    diff = previous_directions.count(True) - 2
                    self.cul_de_sacs_count -= diff
            
            if len(self.cul_de_sacs_points) == start_point_number:
                break
        
        final_paths = []
        for path in self.entry_exit_paths:
            valid = True
            for point in path[1: -1]:
                if temp_direction_grid[point[0]][point[1]].count(True) != 2:
                    valid = False
                    break
            if valid:
                final_paths.append(path)
        
        self.entry_exit_paths = final_paths
    
    def get_exit_gates(self, paths, current_point, current_path):
        if current_point in self.gates:
            current_path.append(current_point)
            paths.append(current_path)
            return [current_point]
        
        current_path.append(current_point)
        self.searched_point.add(current_point)
        
        neighbors = self.get_neighbor(current_point)
        
        exit_gates = []
        for next_point in neighbors:
            if next_point in self.searched_point or next_point in current_path:
                continue
            for gate in self.get_exit_gates(paths, next_point, current_path.copy()):
                if gate not in exit_gates:
                    exit_gates.append(gate)
        return exit_gates
    
    def get_neighbor(self, current_point):
        current_row, current_col = current_point
        available_directions = self.direction_grid[current_row][current_col]
        neighbors = []
        for index in range(4):
            if available_directions[index]:
                row_diff, col_diff = self.row_col_diff[index]
                neighbor = (current_row + row_diff, current_col + col_diff)
                neighbors.append(neighbor)
        return neighbors
        
    
    def gate_to_point(self, gate):
        row_index, col_index = gate
        if row_index == -1:
            row_index = 0
        elif col_index == -1:
            col_index = 0
        elif row_index == self.row_num - 1:
            row_index -= 1
        else:
            col_index -= 1
        return row_index, col_index
    
    def generate_direction_grid(self):
        direction_grid = []
        
        for row_index in range(self.row_num - 1):
            line = []
            for col_index in range(self.col_num - 1):
                # 右，下，左，上
                direction = [False, False, False, False]
                if self.grid[row_index][col_index + 1] not in ["2", "3"]:
                    direction[0] = True
                if self.grid[row_index + 1][col_index] not in ["1", "3"]:
                    direction[1] = True
                if self.grid[row_index][col_index] not in ["2", "3"]:
                    direction[2] = True
                if self.grid[row_index][col_index] not in ["1", "3"]:
                    direction[3] = True
                line.append(direction)
            direction_grid.append(line)
            
        self.direction_grid = direction_grid
    
    
    def analyze_wall(self):
        searched = []
        sets_count = 0
        for row_index in range(self.row_num):
            for col_index in range(self.col_num):
                if (row_index, col_index) not in searched and self.grid[row_index][col_index] != "0":
                    sets_count += 1
                    self.search_one_wall(row_index, col_index, searched)
        self.walls_num = sets_count
    
    
    def search_one_wall(self, row_index, col_index, searched, expected=["1", "2", "3"]):
        if not self.check_indexs(row_index, col_index):
            return None
        if (row_index, col_index) in searched or self.grid[row_index][col_index] not in expected:
            return None
        
        searched.append((row_index, col_index))
        if self.grid[row_index][col_index] != "2":
            self.search_one_wall(row_index, col_index + 1, searched, ["1", "2", "3"])
            self.search_one_wall(row_index, col_index - 1, searched, ["1", "3"])
            self.search_one_wall(row_index - 1, col_index + 1, searched, ["2", "3"])
            self.search_one_wall(row_index - 1, col_index, searched, ["2", "3"])
            
        if self.grid[row_index][col_index] != "1":
            self.search_one_wall(row_index + 1, col_index, searched, ["1", "2", "3"])
            self.search_one_wall(row_index + 1, col_index - 1, searched, ["1", "3"])
            self.search_one_wall(row_index, col_index - 1, searched, ["1", "3"])
            self.search_one_wall(row_index - 1, col_index, searched, ["2", "3"])
    
    
    def check_indexs(self, row_index, col_index):
        return row_index in range(self.row_num) and col_index in range(self.col_num)
    
    
    def analyze_gate(self):
        self.gates = []
        for col in range(len(self.grid[0]) - 1):
            if self.grid[0][col] in ["0", "2"]:
                self.gates.append((-1, col))
            if self.grid[-1][col] in ["0", "2"]:
                self.gates.append((self.row_num - 1, col))

        for row in range(len(self.grid) - 1):
            if self.grid[row][0] in ["1", "0"]:
                self.gates.append((row, -1))
            if self.grid[row][-1] in ["1", "0"]:
                self.gates.append((row, self.col_num - 1))
    
    
    def display(self):
        self.analyze_gate()
        self.analyze_wall()
        self.find_ways()
#         tex_filename = "ExpectedFiles/" + self.filename[:-3] + "tex"
        tex_filename = self.filename[:-3] + "tex"
        with open(tex_filename, "w") as file:
            file.write("\\documentclass[10pt]{article}\n")
            file.write("\\usepackage{tikz}\n")
            file.write("\\usetikzlibrary{shapes.misc}\n")
            file.write("\\usepackage[margin=0cm]{geometry}\n")
            file.write("\\pagestyle{empty}\n")
            file.write("\\tikzstyle{every node}=[cross out, draw, red]\n")
            file.write("\n")
            file.write("\\begin{document}\n")
            file.write("\n")
            file.write("\\vspace*{\\fill}\n")
            file.write("\\begin{center}\n")
            file.write("\\begin{tikzpicture}[x=0.5cm, y=-0.5cm, ultra thick, blue]\n")
            file.writelines(self.draw_walls())
            file.writelines(self.draw_pillars())
            file.writelines(self.draw_cul_de_sacs())
            file.writelines(self.draw_paths())
            file.write("""\\end{tikzpicture}
\\end{center}
\\vspace*{\\fill}

\\end{document}\n""")
    
    
    def draw_paths(self):
        result = ["% Entry-exit paths without intersections\n"]
        lines = []
        for path in self.entry_exit_paths:
            reduced_path = [path[0]]
            for point_index in range(1, len(path) - 1):
                current_point = path[point_index]
                previous_point = path[point_index - 1]
                next_point = path[point_index + 1]
                
                diff_cur_pre = (current_point[0] - previous_point[0], current_point[1] - previous_point[1])
                diff_next_cur = (next_point[0] - current_point[0], next_point[1] - current_point[1])
                
                if diff_cur_pre != diff_next_cur:
                    reduced_path.append(path[point_index])
            reduced_path.append(path[-1])
            
            for point_index in range(len(reduced_path) - 1):
                point1 = (reduced_path[point_index][1] + 0.5, reduced_path[point_index][0] + 0.5)
                point2 = (reduced_path[point_index + 1][1] + 0.5, reduced_path[point_index + 1][0] + 0.5)
                lines.append(sorted([point1, point2]))
        
        lines = sorted(lines, key=lambda x: (x[0][1], x[0][0]))
        for line in lines:
            if line[0][1] == line[1][1]:
                result.append(f"    \draw[dashed, yellow] ({line[0][0]},{line[0][1]}) -- ({line[1][0]},{line[1][1]});\n")
        
        for line in sorted(lines):
            if line[0][0] == line[1][0]:
                result.append(f"    \draw[dashed, yellow] ({line[0][0]},{line[0][1]}) -- ({line[1][0]},{line[1][1]});\n")
        return result
    
    def draw_cul_de_sacs(self):
        result = ["% Inner points in accessible cul-de-sacs\n"]
        for point in sorted(self.cul_de_sacs_points):
            result.append(f"    \\node at ({point[1] + 0.5},{point[0] + 0.5}) " + "{};\n")
        return result
            
    def draw_pillars(self):
        result = ["% Pillars\n"]
        for row in range(self.row_num):
            for col in range(self.col_num):
                if ((self.grid[row][col] == "0") and 
                    (self.check_indexs(row - 1, col) is None or self.grid[row - 1][col] in ["0", "1"]) and
                    (self.check_indexs(row, col - 1) is None or self.grid[row][col - 1] in ["0", "2"])):
                    result.append(f"    \\fill[green] ({col},{row}) circle(0.2);\n")
        return result
    
    
    def draw_walls(self):
        result = ["% Walls\n"]
        for row in range(self.row_num):
            col = 0
            while col < self.col_num:
                if self.grid[row][col] in ["1", "3"]:
                    start = (col, row)
                    length = 0
                    temp_col = col
                    while temp_col < self.col_num:
                        if self.grid[row][temp_col] in ["1", "3"]:
                            length += 1
                            temp_col += 1
                        else:
                            break
                    end = (temp_col, row)
                    draw_line = f"    \\draw ({start[0]},{start[1]}) -- ({end[0]},{end[1]});\n"
                    result.append(draw_line)
                    col = temp_col
                else:
                    col += 1
        
        for col in range(self.col_num):
            row = 0
            while row < self.row_num:
                if self.grid[row][col] in ["2", "3"]:
                    start = (col, row)
                    length = 0
                    temp_row = row
                    while temp_row < self.row_num:
                        if self.grid[temp_row][col] in ["2", "3"]:
                            length += 1
                            temp_row += 1
                        else:
                            break
                    end = (col, temp_row)
                    draw_line = f"    \draw ({start[0]},{start[1]}) -- ({end[0]},{end[1]});\n"
                    result.append(draw_line)
                    row = temp_row
                else:
                    row += 1
        return result

# Maze("incorrect_input_1.txt")
# Maze("incorrect_input_2.txt")
# Maze("not_a_maze_1.txt")
maze = Maze("example1.txt")
maze.display()
# print(maze.direction_grid)