###Balanced Transportaion Problem LP Gurobi Formulation
from gurobipy import *
import csv
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

    for w in range(0, len(warehouses)):
        m.addConstr(quicksum(shipMatrix[w][s] for s in range(0, len(stores))) <= warehouses[w], name = 'f')

    ###total coming to a store = demand

    for s in range(0, len(stores)):
        m.addConstr(quicksum(shipMatrix[w][s] for w in range(0, len(warehouses))) >= stores[s], name = 'q')

    m.update()
    m.optimize();
    foc = csv.writer(open('TransportationSolution.csv','w'), delimiter =',')
    for w in range(0,len(warehouses)):
        value=[]
        for s in range(0,len(stores)):
            value.append(shipMatrix[w][s].x)
        foc.writerow(value)
    obj = m.getObjective()
    val= []
    val.append("The objective value is " + str(obj.getValue()))
    foc.writerow(val)



def main():

    costs = []
    fc = csv.reader(open('TransportationCosts.csv', 'rU'))
    for row in fc:
        row = map(int,row)
        costs.append(row)
    
    
    fw = csv.reader(open('TransportationWarehouses.csv', 'rU'))
    warehouses = fw.next()
    warehouses = map(int,warehouses)

    fs = csv.reader(open('TransportationStores.csv', 'rU'))
    stores = fs.next()
    stores = map(int,stores)


    solve (warehouses, stores, costs)

if __name__ == "__main__": main()
