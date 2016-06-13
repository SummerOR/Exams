###Balanced Transportaion Problem LP Gurobi Formulation
from gurobipy import *
"""
@param warehouses: list of warehouses, warehouse[i] = supply of warehouse i
@param stores: list of stores, stores[j] = demand of store j
*note sum of supply = sum of demand
@param costs: 2d matrix, costs[i][j] = cost of sending 1 unit from house i to store j


"""
def solve(warehouses, stores, costs):
    m = Model("Transportation")
    # create and add decision variables
    shipMatrix = []
    for w in range(0, len(warehouses)):
        shipMatrix.append([])
        for s in range(0, len(stores)):
            shipMatrix[w].append(m.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.INTEGER))
    m.update()
    #Create objective value
    m.setObjective(quicksum(costs[w][s]*shipMatrix[w][s] for w in range(0, len(warehouses)) for s in range(0, len(stores))), GRB.MINIMIZE)

    #Set Constraints
    ###total sent from a warehouse <= supply
    i = 0
    for w in range(0, len(warehouses)):
        m.addConstr(quicksum(shipMatrix[w][s] for s in range(0, len(stores))) <= warehouses[w],"c"   )
        i = i + 1
    ###total coming to a store = demand
    j = 0
    for s in range(0, len(stores)):
        m.addConstr(quicksum(shipMatrix[w][s] for w in range(0, len(warehouses))) >= stores[s],"c"  ) 
        j = j + 1


    m.update()
    m.optimize()

    """ for w in range(0, len(warehouses)):
        for s in range(0, len(stores)):
            print (shipMatrix[w][s] )
            obj = m.getObjective()
            print obj.getValue()"""





def main():

    ware = [7, 8, 3]
    stor = [3, 5, 2, 8]
    cost = [[8, 0, 3, 2], [1, 9, 4, 5], [8, 6, 9, 7]]
    solve (ware, stor, cost)

if __name__ == "__main__": main()
