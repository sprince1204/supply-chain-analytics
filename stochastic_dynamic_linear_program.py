# -*- coding: utf-8 -*-



import math
import csv

from gurobipy import *
model = Model("Barkawi")




I = [0,1,2,3,4,5,6,7,8,9,10]    #Nodes = Warehouses + Outlets

T = [0,1]   #optimisation over time horizon of 2 weeks

PROB = [0.05, 0.3, 0.25, 0.23, 0.17]    #Probabilities assigned to each demand scenario


#INPUT STEP 1: Replace the file location in open statement with Demand forecast over next two weeks 

#Demand at all 10 outlets over the two following weeks

with open('demand_forecast_2_week0_uncertain.csv', newline='') as csvfile:
    Dinp = list(csv.reader(csvfile))

for i in range(10):
    for j in range(len(T)*(len(PROB)+1)):
        Dinp[i][j]=math.ceil(float(Dinp[i][j]))

#Arranging demand array into a MATRIX with usable indices
DEM = {}
for a in range(len(PROB)):
    for t in T:
        for i in I:
            if i!=0:                        #Demand is not defined for the warehouse
                DEM[a, t, i] = Dinp[i-1][6*t+a+1]       


#Demand D for outlets at different times D[t][j]. Vertices V are thus defined as (t,i) for all t        
V, D = gurobipy.multidict(DEM)    


#INPUT STEP 2: Enter the location of the outlet stocks file in the open statement below

#Stock left over from week '-1', week before the order week t=0: This would be an input Array

with open('outlet_stock.csv', newline='') as csvfile:
    Oinp = list(csv.reader(csvfile))

O=[]
for a in range(len(PROB)):
    O.append([])
    for i in range(10):
        O[a].append(math.ceil(float(Oinp[a][i])))
        

#INPUT STEP 3: Enter the location of the replenishment file in the open statement below

#replenishment from Warehouse arriving at starting of week t=0: This would be an input Array

with open('replenishment.csv', newline='') as csvfile:
    Rinp = list(csv.reader(csvfile))
R=[]
for i in range(10):
    R.append(math.ceil(float(Rinp[0][i])))
       

#Transport cost per dist per quantity transferred
GO = 0.08
GW = 0.06      

#Inventory holding cost per unit inventory: 5% of cost of the product 
H = 0.79  

#Cost incurred due to loss of sales: margin on the product = 30% of cost of product   
LS = 591       

#MOQ of the item- Input from User
Q=25       

# MAX CAPACITY value for each arc for relating decision variable to quantity variable for each arc = max(demand) + MOQ
M = 1*(Q + max(max(Dinp)))   

#Distance matrix: it is symmetric
with open('J:\MMM_Data\distance_matrix.csv', newline='') as csvfile:
    distinp = list(csv.reader(csvfile))

x=[]
location=[]
for i in range(11):
    location.append(distinp[i+1][0])
    x.append([])
    for j in range(11):
        x[i].append(float(distinp[i+1][j+1]))


#decision matrix to define the cost of each arc
COST = {}
for t in T:                                 
    for i in I:
        for j in I:                               
            if i!=0 and j!=0:
                if i!=j:
                    COST[t,i,j] = x[i][j]*GO
            if i==0 and j!=0:
                COST[t,i,j] = x[i][j]*GW + H


#Definition of each arc in A and Cost C of each arc which includes inventory holding cost + transportation cost
A, C = gurobipy.multidict(COST)  

#decision matrix to define the inventory holding cost for left over stock after each week at each vertex
INV = {}
LOSS = {}
for a in range(len(PROB)):
    for t in T:
        for i in I:
            if i!=0: 
                if t==T[-1]:                       #Inventory holding cost is only incurred by the inventory left over in the end of last week
                    INV[a,t,i] = H*PROB[a]
                    LOSS[a,t,i] = LS*PROB[a]
                else:
                    INV[a, t, i] = 2*H*PROB[a]
                    LOSS[a,t,i] = LS*PROB[a]
                
#inventory holding cost over left over stock = K[t][j]. Vertices V are thus defined as (t,i) for all t        
V, K = gurobipy.multidict(INV)
V, U = gurobipy.multidict(LOSS)  


'''
VARIABLES:
    w[a] = amount of goods carried on each arc, for all a in A
    l[V] = loss of sales at each outlet, for all v in V
    y[A] = if arc is chosed or not, for all a in A
    s[V]= stock at the end of each week not sold at the outlet, for all v in V
'''

w = model.addVars(A, lb =0, obj=C, vtype= GRB.INTEGER, name="arc_quantity")
l = model.addVars(V, lb=0, obj=U, vtype= GRB.INTEGER, name="lost_sales")
y = model.addVars(A, obj=0, vtype= GRB.BINARY, name="arc_select")
s = model.addVars(V, lb=0, obj=K, vtype= GRB.INTEGER, name="stock")


'''
CONSTRAINTS:
    Constraints assigning initial conditions to variables in week 0
    Demand constraint for all outlets
    MOQ constraints for shipment from Warehouse
    arc selection constraint linking w and y
'''


#Replenishment from the warehouse in Week t needs to be assigned as per input array R
for j in I[1:]:
    if (0,0,j) in A:
        model.addConstr((w[0,0,j]>=R[j-1]), "from_warehouse_t0_greater")
        model.addConstr((w[0,0,j]<=R[j-1]), "from_warehouse_t0_smaller")
                

#Demand constraints for week t (T equations)
model.addConstrs((O[a][j-1] + w.sum(0, '*',j) - w.sum(0, j, '*') >= D[a,0,j] - l[a,0,j] for j in I[1:] for a in range(len(PROB))), "demand_t=0")
model.addConstrs((s[a,t-1,j] + w.sum(t, '*',j) - w.sum(t, j, '*') >= D[a,t,j] - l[a,t,j] for j in I[1:] for t in T[1:] for a in range(len(PROB))), "demand_t")                           


#Stock at the end of week t (T equations)
model.addConstrs((s[a, 0, j] >= O[a][j-1] + w.sum(0, '*',j) - w.sum(0, j, '*') - D[a,0,j] +l[a,0,j] for j in I[1:] for a in range(len(PROB))), "demand_t=0greater")                          
model.addConstrs((s[a, 0, j] <= O[a][j-1] + w.sum(0, '*',j) - w.sum(0, j, '*') - D[a,0,j] +l[a,0,j] for j in I[1:] for a in range(len(PROB))), "demand_t=0lesser")                          
model.addConstrs((s[a, t, j] >= s[a,t-1,j] + w.sum(t, '*',j) - w.sum(t, j, '*') - D[a,t,j] +l[a,t,j] for j in I[1:] for t in T[1:] for a in range(len(PROB))), "demand_tgreater")                          
model.addConstrs((s[a, t, j] <= s[a,t-1,j] + w.sum(t, '*',j) - w.sum(t, j, '*') - D[a,t,j] +l[a,t,j] for j in I[1:] for t in T[1:] for a in range(len(PROB))), "demand_tlesser")                          


#MOQ constraints
model.addConstrs((w[t,0,j]>=Q*y[t,0,j] for j in I[1:] for t in T), "MOQ")

#y constraints
model.addConstrs((w[t,i,j]<=M*y[t,i,j] for (t,i,j) in A), "x_y_relationship")


'''
SOLVE THE MODEL:
'''

model.optimize()

'''
PRINTING THE SOLUTION:
'''
TotalCost=0
TotalCostWeek1=0
avgloss0=0
avgloss1=0
prodloss0=0
prodloss1=0

if model.status == GRB.OPTIMAL:
    print("\nRESULT:\n")
    print("Rebalancing to be done in WEEK 0:\n")
    rebcnt=0
    for t in T:        
        for i in I:
            for j in I:
                if (t,i,j) in A:
                    if w[(t,i,j)].x:
                        #print(f"{(w[t,i,j].x)} quantity of the product is transferred from {location[i]} to {location[j]} in week {t}")
                        TotalCost = TotalCost + (w[t,i,j].x)*C[t,i,j]
                        if t==0:
                            TotalCostWeek1 = TotalCostWeek1 + (w[t,i,j].x)*C[t,i,j]
                            if i != 0:
                                rebcnt=rebcnt+1
                                print(f"{(w[t,i,j].x)} quantity of the product is to be rebalanced from {location[i]} to {location[j]} in week {t}")
                        #print(TotalCost)
                        #print(TotalCostWeek1)
    if rebcnt==0:
        print("No rebelancing Needed.")
    
    print("\nReplenishment to be ordered from Warehouse in WEEK 1:")
    repcnt = 0
    for t in T:        
        for i in I:
            for j in I:
                if (t,i,j) in A:
                    if w[(t,i,j)].x:
                        if t==1:
                            if i==0:
                                repcnt=repcnt+1
                                print(f"{(w[t,i,j].x)} quantity of the product is to be ordered from {location[i]} to {location[j]} in week {t}")
    if repcnt==0:
        print("\nNo replenishment from Warehouse needed.")                   
                        
    cnt=0
    for a in range(len(PROB)):
        for t in T:        
            for i in I:
                if (a,t,i) in V:
                    if l[(a,t,i)].x:
                        print(f"{(l[a,t,i].x)} is the loss of sales at {location[i]} in week {t} scenario {a}")
                        cnt=cnt+1
                        TotalCost = TotalCost + (l[a,t,i].x)*U[a,t,i]
                        if t==0:
                            TotalCostWeek1 = TotalCostWeek1 + (l[a,t,i].x)*U[a,t,i]
                            avgloss0 = avgloss0 + (l[a,t,i].x)*U[a,t,i]
                            prodloss0 = prodloss0 + (l[a,t,i].x)*PROB[a] 
                        if t==1:
                            avgloss1 = avgloss1 + (l[a,t,i].x)*U[a,t,i]
                            prodloss1 = prodloss1 + (l[a,t,i].x)*PROB[a]
                    if s[(a,t,i)].x:
                        #print(f"{s[a,t,i].x} is inventory left at outlet {i} after week {t} in scenario {a}")
                        TotalCost = TotalCost + (s[a,t,i].x)*K[a,t,i]
                        if t==0:
                            TotalCostWeek1 = TotalCostWeek1 + (s[a,t,i].x)*K[a,t,i]
                    #print(TotalCost)
                    #print(TotalCostWeek1)
    if cnt==0:
        print("\nThere is no loss of sales.")
    else:
        print(f"\nAverage cost of loss of sales over week 0 = {avgloss0} over average unmet demand of {prodloss0} quanities")
        print(f"\nAverage loss of sales over week 1 = {avgloss1} over average unmet demand of {prodloss1} quanities")
        
    #for i in range(10):
        #TotalCost = TotalCost + O[i]*H
        
    print(f"\nThe total estimated cost of replenishment and rebalancing for the 2 week time horizon is {round(model.objval,2)}")
    print(f"\nThe total estimated cost of replenishment and rebalancing over WEEK 0 is {round(TotalCostWeek1,2)}")
    print(f"\nThe runtime of the model is {round(model.Runtime,2)}seconds")

else:
    print("\n\nRESULT:\nNo solution could be obtained for given preferences")


'''
GENERATING INPUT FILES FOR NEXT WEEK:
'''

if model.status == GRB.OPTIMAL:
    print("\nInput files for next week's program are generated as outlet_stock_next.csv and replenishment_next.csv.")
    REPL=[]
    STOCK=[]
    
    for j in I:
        if j!=0:
            if (1,0,j) in A:
                REPL.append(w[1,0,j].x)
                
    for a in range(len(PROB)):
        STOCK.append([])
        for j in I:
            if j!=0:
                if (a,0,j) in V:
                    STOCK[-1].append(s[a,0,j].x)
                
                               
    import csv
    with open("replenishment_next.csv", "w", newline="") as f:			#input file for next program
        writer = csv.writer(f)
        writer.writerows([REPL]) 
    with open("outlet_stock_next.csv", "w", newline="") as g:			#input file for next program
        writer = csv.writer(g)
        writer.writerows(STOCK)