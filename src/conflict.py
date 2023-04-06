import init


def solvedLogic(order):

    # If not nth order solution
    if order < init.maxorder-1:
        # If this solution round has not gone to n+1 order
        # it means this is max order this round even if previous attempts have gone to n+
        if init.presolved[order + 1] == init.solved[order + 1]:
            init.solved[order] += 1
            # If solves for n order reaches max solves, only move to next potential solution for nth order
            # Nth order is determined by presolved if presolved n+1 has not changed then it has not been reached and in a new 'Chain'
            # Ex: if a 2nd order solution only update 2nd order metadata
            # if init.solved[order] >= init.maxsolves and (init.solution[order+1] == 0 or init.presolved[order+1] == init.solved[order+1]):
            if init.solved[order] >= init.maxsolves:
                init.solution[order] += 1  # Increment the solution number to stop at the next solution, if none go up an order or return -1 no solution
                init.solved[order] = 0  # Reset the number of times it is attempted
                if init.solution[order] == init.maxsolutions[order]:
                    init.solved[order] = -1
        init.presolved[order + 1] = init.solved[order + 1]  # When a level is solved lock in the +1 orders solved to presolved
    else:
        init.solved[order] += 1
        # If solves for n order reaches max solves, only move to next potential solution for nth order
        # Nth order is determined by presolved if presolved n+1 has not changed then it has not been reached and in a new 'Chain'
        # Ex: if a 2nd order solution only update 2nd order metadata
        # if init.solved[order] >= init.maxsolves and (init.solution[order+1] == 0 or init.presolved[order+1] == init.solved[order+1]):
        if init.solved[order] >= init.maxsolves:
            init.solution[order] += 1  # Increment the solution number to stop at the next solution, if none go up an order or return -1 no solution
            init.solved[order] = 0  # Reset the number of times it is attempted
            if init.solution[order] == init.maxsolutions[order]:
                init.solved[order] = -1


def resetSolutionLogic():
    init.solved = [0] * init.maxorder
    init.solution = [0] * (init.maxorder + 1)
