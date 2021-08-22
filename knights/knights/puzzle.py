from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

KnightAndKnaveRules = And(
Not(And(AKnight,AKnave)), Not(And(BKnight,BKnave)), Not(And(CKnight,CKnave)) 
#Biconditional(Not(AKnight), AKnave), Biconditional(Not(AKnave), AKnight), Biconditional(Not(BKnight), BKnave),
#Biconditional(Not(BKnave), BKnight), Biconditional(Not(CKnight), CKnave), Biconditional(Not(CKnave), CKnight) 
,Biconditional(Not(AKnight), AKnave), Biconditional(Not(BKnight), BKnave), Biconditional(Not(CKnight), CKnave)                         
)

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
        #Either A is a Knave, or A is a Knight and the statement is true
KnightAndKnaveRules, Or(AKnave, And(AKnight, And(AKnave,AKnight)))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
premise1 = And(BKnave, AKnave)
knowledge1 = And(
KnightAndKnaveRules, Or(And(AKnave, Not(premise1)), And(AKnight, premise1))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
premise2a = And(BKnave, AKnave)
premise2b = Or(And(AKnave, BKnight), And(BKnave, BKnight))
knowledge2 = And(
    # TODO
    KnightAndKnaveRules, 
    Or(And(AKnave, Not(premise2a)), And(AKnight, premise2a)),
    Or(And(BKnave, Not(premise2b)), And(BKnight, premise2b))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
premise3a = Or(AKnight, AKnave)
premise3b = Or(And(AKnave, Not(BKnave)), And(AKnight, BKnight))
premise3c = CKnave
premise3d = AKnight 
knowledge3 = And(
    # TODO
    KnightAndKnaveRules, 
    Or(And(AKnave, Not(premise3a)), And(AKnight, premise3a)),
    Or(And(BKnave, Not(premise3b)), And(BKnight, premise3b)),
    Or(And(BKnave, Not(premise3c)), And(BKnight, premise3c)),
    Or(And(CKnave, Not(premise3d)), And(CKnight, premise3d))    
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
