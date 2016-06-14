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
    shipMatrix=[]
    
    #arbitraily have decided that we can't ship from warehouse 0 to first and last store.
    
    for w in range(0, len(warehouses)):
        storestovisit= {}
        storestovisit[w] = storelist(w, stores)
        shipMatrix.append([])
        for s in range(0, len(stores)):
            if(s in storestovisit[w]):
                #make a decision variable that model can work with
                shipMatrix[w].append(m.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.INTEGER))
            else:
                #Just add integer 0
                shipMatrix[w].append(int(0))
    m.update()
    #Create objective value
    m.setObjective(quicksum(costs[w][s]*shipMatrix[w][s] for w in range(0, len(warehouses)) for s in range(0, len(stores))), GRB.MINIMIZE)

    #Set Constraints
    ###total sent from a warehouse = supply

    for w in range(0, len(warehouses)):
        m.addConstr(quicksum(shipMatrix[w][s] for s in range(0, len(stores))) <= warehouses[w], name = 'f')

    ###total coming to a store = demand

    for s in range(0, len(stores)):
        m.addConstr(quicksum(shipMatrix[w][s] for w in range(0, len(warehouses))) >= stores[s], name = 'q')

    m.update()
    m.optimize();
    
    foc = csv.writer(open('TransportationSolution2.csv','w'), delimiter =',')
    for w in range(0,len(warehouses)):
        value=[]
        for s in range(0,len(stores)):
            #if it is a decision variable, add the value of the variable
            if(isinstance(shipMatrix[w][s],Var)):
                value.append(shipMatrix[w][s].x)
            #otherwise just add the integer 0 that is present in that cell
            else:
                value.append(shipMatrix[w][s])
        foc.writerow(value)
    obj = m.getObjective()
    val= []
    val.append("The objective value is " + str(obj.getValue()))
    foc.writerow(val)


#returns the list of stores that this warehouse can send to
def storelist(w, stores):
    list = []
    if w == 0:
        for x in range(1,len(stores)-1):
            list.append(x)
    else:
        for x in range(0,len(stores)):
            list.append(x)

    return list
            
    
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
