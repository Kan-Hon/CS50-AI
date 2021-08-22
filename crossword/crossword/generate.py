import sys
import copy
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        for key, value in self.domains.items():
            values_copy = copy.copy(value)
            for each_word in values_copy:
                if key.length != len(each_word):
                    self.domains[key].remove(each_word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        toRemove = set()
        for each_word_x in self.domains[x]:
            flag = False
            for each_word_y in self.domains[y]:
                if (each_word_x != each_word_y):
                    if self.crossword.overlaps[x,y] is not None:
                        i, j = self.crossword.overlaps[x,y]
                        if each_word_x[i] == each_word_y[j]:
                            if each_word_x in toRemove:
                                toRemove.remove(each_word_x)
                            flag = True
                            break
                        else:
                            toRemove.add(each_word_x)
                            revised = True
                        

        for i in toRemove:
            self.domains[x].remove(i)
            
        return revised

        
        

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            queue = self.initialise_arcs()
        else:
            queue = arcs
        while len(queue) > 0:
            (x, y) = queue.pop()
            if self.revise(x,y):
                if len(self.domains[x]) == 0:
                    return False
                for neighbour_var in self.crossword.neighbors(x):
                    if neighbour_var != y:
                        queue.add((neighbour_var, x))

        return True
            
            
    def initialise_arcs(self):
        # returns the set of tuples of variables
        set_of_arcs = set()
        for each_domain_x in self.domains:
            for each_domain_y in self.domains:
                if each_domain_x != each_domain_y:
                    set_of_arcs.add((each_domain_x, each_domain_y))
        return set_of_arcs
    
    
    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        for k1,v1 in self.domains:
            if k1 not in assignment:
                return False
        return True


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        for k1, v1 in assignment.items():
            for k2, v2 in assignment.items():
                if k1 == k2 or v1 is None or v2 is None or (self.crossword.overlaps[k1,k2]) is None:
                    continue
                else:
                    (i, j) = self.crossword.overlaps[k1,k2]
                    for word1 in v1:
                        for word2 in v2:
                            if word1[i] != word2[j]:
                                return False
                    
        return True
                

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        
        var_neighbours = self.crossword.neighbors(var)
        ruled_out = dict()
                    
        for possible_values in self.domains[var]:
            for neighbour in var_neighbours:
                # find overlaps in var and neighbour
                (i,j) = self.crossword.overlaps[var, neighbour]
                neighbour_ruled_out = 0
                for neighbour_values in self.domains[neighbour]:
                    if possible_values[i] != neighbour_values[j]:
                        neighbour_ruled_out += 1
                ruled_out[possible_values] = neighbour_ruled_out
                
        sort = sorted([x for x in ruled_out], key = lambda x: ruled_out[x])
        return sort

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Get set of unassigned variables
        unassigned = set(self.domains.keys()) - set(assignment.keys())
        sorted_by_domain = sorted([x for x in unassigned], key = lambda x:len(self.domains[x]))
        smallest_domain_length = len(self.domains[sorted_by_domain[0]])
        smallest_domain = []
        for each_var in unassigned:
            if len(self.domains[each_var]) == smallest_domain_length:
                smallest_domain.append(each_var)
                
        # if theres no tie, return smallest domain
        if len(smallest_domain) == 1:
            return smallest_domain[0]
        
        else:
            # else, return smallest domain with largest number of neighbours
            return sorted([x for x in sorted_by_domain], key = lambda x:-len(self.crossword.neighbors(x)))[0]

                

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        assignment_complete = True
        for k,v in self.domains.items():
            if k not in assignment:
                assignment_complete = False
                break
        if assignment_complete:
            return assignment
        
        selected_var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(selected_var, assignment):

            if self.consistent(assignment):
                # if new assignment is consistent, add to assignment
                if selected_var not in assignment:
                    assignment[selected_var] ={value}
                else:
                    assignment[selected_var].add(value)
                result = self.backtrack(assignment)
                
                if result is not None:
                    return result

                assignment[selected_var].remove(value)
            # if somewhere down the road where it is not consistent, remove this assignment

        return None
def remove_curly_brackets(assignment):
    new_assignment = {}
    for k,v in assignment.items():
        new_assignment[k] = v.pop()
    return new_assignment

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()
    assignment = remove_curly_brackets(assignment)

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
