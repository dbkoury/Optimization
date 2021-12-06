# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 20:08:28 2021

@author: dylan
"""
#Optimization Project
#Team 2: Anoushka Mahar, Riti Dabas, Dylan Koury

from gurobipy import *
from pulp import LpVariable, LpProblem, LpMaximize, LpStatus, value, LpMinimize
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as pat
from matplotlib.patches import Polygon
import matplotlib.path as mpath

#Indexed Sets
R = range(8) #number of retail centers
W = range(4) #number of warehouses
P = range(5) #number of plants
Y = range(10) #number of years

#Retailers Data
RetailDemand1 = [1000,1200,1800,1200,1000,1400,1600,1000] #Demand Year 1
DemandGrowthRate = [0.2,0.2,0.25,0.2,0.2,0.25,0.25,0.2] #yearly demand growth rates 
D = []
for i in Y:
    temp = []
    for j in R:
        temp.append(RetailDemand1[j]*(1+DemandGrowthRate[j])**i) #creating matrix of yearly costs
    D.append(temp)

C = 0.03 #cost growth rate

#Plant Data
PC = [16000,12000,14000,10000,13000] #Production Capacity in units
ConstructionCost = [2000,1600,1800,900,1500] #in 1000s of $
CC = [] #yearly construction cost data
OperatingCost = [420,380,460,280,340] #in 1000s of $
OC = [] #yearly operating cost data
ReopeningCost = [190,150,160,100,130] #in 1000s of $
RC = [] #yearly reopening cost data
ShutdownCost = [170,120,130,80,110] #in 1000s of $
SC = [] #yearly shutdown cost data
#Creating matrices of yearly plant costs
for i in Y:
    temp = []
    for j in P:
        temp.append(ConstructionCost[j]*(1+C)**i)
    CC.append(temp)
    
for i in Y:
    temp = []
    for j in P:
        temp.append(OperatingCost[j]*(1+C)**i)
    OC.append(temp)
    
for i in Y:
    temp = []
    for j in P:
        temp.append(ReopeningCost[j]*(1+C)**i)
    RC.append(temp)

for i in Y:
    temp = []
    for j in P:
        temp.append(ShutdownCost[j]*(1+C)**i)
    SC.append(temp)
    
#Warehouse Data
IMax = 4000 #Maximum Average Inventory in number of items
MaxMonthlyAvg = 1000 #Maximum Monthly Average number of flugels per month any warehouse can handle
FMax = MaxMonthlyAvg*12 #Yearly warehouse capacity average

#Flugel Production Data
APF = 4.7 #Alloy required for one flugel in lbs
APPMax = 60000 #maximum in lbs of alloy any plant can acquire per year
AC1 = 0.02 #in 1000s of $ for a pound of alloy in year 1
WPF = 3 #number of widgets to make a flugel
OriginalWidgetCost1 = 0.15 #in 1000s of $ for a widget in year 1
DiscountWidgetCost1 = 0.12 #cost for widget after 9000 purchased
WTD = 9000 #how many widgets must be ordered before discount applied

#Creating yearly resource costs
AC = [] #yearly alloy cost
OWC = [] #yearly non discounted alloy costs
DWC = [] #yearly discounted alloy costs

for i in Y:
    AC.append(AC1*(1+C)**i)

    
for i in Y:
    OWC.append(OriginalWidgetCost1*(1+C)**i)

    
for i in Y:
    DWC.append(DiscountWidgetCost1*(1+C)**i)


#Shipping from plant to warehouse  in 1000s 0f $
PlantWarehouseShippingCost = [[0.12,0.13,0.08,0.05],#Plant 1
                              [0.1,0.03,0.1,0.09],  #Plant 2
                              [0.05,0.07,0.06,0.03],#Plant 3
                              [0.06,0.03,0.07,0.07],#Plant 4
                              [0.06,0.02,0.04,0.08]]#Plant 5

#Shipping from warehouse to retail center  in 1000s 0f $
WarehouseRetailShippingCost = [[0.09,0.1,0.06,0.05,0.08,0.09,0.02,0.12], #warehouse 1
                               [0.05,0.07,0.12,0.04,0.03,0.09,0.03,0.08], #warehouse 2
                               [0.06,0.09,0.07,0.09,0.09,0.04,0.11,0.07], #warehouse 3
                               [0.07,0.08,0.09,0.06,0.1,0.07,0.06,0.09]] #warehouse 4

#create shipping cost list of lists of lists for yearly costs
PWSC = []
WRSC = []
for i in Y:
    temp = []
    for j in P:
        temp2 = []
        for k in W:
            temp2.append(PlantWarehouseShippingCost[j][k]*(1+C)**i)
        temp.append(temp2)
    PWSC.append(temp)
    
for i in Y:
    temp = []
    for j in W:
        temp2 = []
        for k in R:
            temp2.append(WarehouseRetailShippingCost[j][k]*(1+C)**i)
        temp.append(temp2)
    WRSC.append(temp)
    
#Create Variables
#Shipping Variables:
    #Flugel Numbers sent yearly from plant to warehouse
PWF = []
for i in Y:
    temp = []
    for j in P:
        temp2 = []
        for k in W:
            temp2.append(LpVariable(f'Y{i}P{j}W{k}',0,PC[j])) #non-negative and cannot exceed total plant capacity but constraint will have to be dealt with on sum as well
        temp.append(temp2)
    PWF.append(temp)
    
    #Flugel Numbers sent yearly from warehouse to retailer
WRF = []
for i in Y:
    temp = []
    for j in W:
        temp2 = []
        for k in R:
            temp2.append(LpVariable(f'Y{i}W{j}R{k}',0,FMax)) #non-negative and cannot exceed total warehouse but constraint will have to be dealt with on sum as well
        temp.append(temp2)
    WRF.append(temp)
    
#Plant Variables:
    #Operating Binary
O = []
for i in Y:
    temp = []
    for j in P:
        temp.append(LpVariable(f'OY{i}P{j}', cat="Binary"))
    O.append(temp)

    #Construction Binary
CD = []
for i in Y:
    temp = []
    for j in P:
        temp.append(LpVariable(f'CDY{i}P{j}', cat="Binary"))
    CD.append(temp)
        
    #Reopening Binary
RD = []
for i in Y:
    temp = []
    for j in P:
        temp.append(LpVariable(f'RDY{i}P{j}', cat="Binary"))
    RD.append(temp)
        
    #Shutdown Binary
CD = []
for i in Y:
    temp = []
    for j in P:
        temp.append(LpVariable(f'SDY{i}P{j}', cat="Binary"))
    CD.append(temp)
        
#Widget Cost Structure Variables:
    #Curve Segments for each plant in each year
A1 = []
for i in Y:
    temp = []
    for j in P:
        temp.append(LpVariable(f'Segment1Y{i}P{j}', cat="Binary"))
    A1.append(temp)
    
A2 = []
for i in Y:
    temp = []
    for j in P:
        temp.append(LpVariable(f'Segment2Y{i}P{j}', cat="Binary"))
    A2.append(temp)

    #Break Point Lambdas for each plant in each year
L1 = []
for i in Y:
    temp = []
    for j in P:
        temp.append(LpVariable(f'Lambda1Y{i}P{j}',0,None))
    L1.append(temp)
    
L2 = []
for i in Y:
    temp = []
    for j in P:
        temp.append(LpVariable(f'Lambda2Y{i}P{j}',0,None))
    L2.append(temp)

L3 = []
for i in Y:
    temp = []
    for j in P:
        temp.append(LpVariable(f'Lambda3Y{i}P{j}',0,None))
    L3.append(temp)
    
# defines the problem
prob = LpProblem("problem", LpMinimize)

#Constraints
    #Widget Cost Structure
for i in Y: #for each year
    for j in P: #and every plant
        prob += L1[i][j] + L2[i][j] + L3[i][j] == 1 #ratio Lambdas sum to 1 for each plant each year
        prob += L1[i][j] <= A1[i][j] #only access purchasing closer to zero if discount section not selected 
        prob += L2[i][j] <= A1[i][j] + A2[i][j] #Close to discount number accessible in both segments of cost structure
        prob += L3[i][j] <= A2[i][j] #Max production may only be possible in discount segment
        prob += A1[i][j] + A2[i][j] == 1 #only one segment can be selected

    #Shipping Constraints - Plants
for i in Y: #for each year
    for j in P: #and each plant
        globals()[f'TotalSupplyY{i}P{j}'] = 0
        for k in W: #sum of production sent across warehouses
            globals()[f'TotalSupplyY{i}P{j}'] += PWF[i][j][k]
        #total flugels made by plant does not exceed production capacity of plant
        prob += globals()[f'TotalSupplyY{i}P{j}'] <= PC[j] 
        #They can also not exceed the limitations of alloys available for purchase required to make them
        prob += globals()[f'TotalSupplyY{i}P{j}'] <= (APPMax/APF)
        #Operation costs only exist if plant is producing flugels
        prob += O[i][j]*PC[j] >= PWF[i][j]
        #Reopening costs only exist if plant operating this year but not the year before
        if i == 0: #because using year prior, must account for year 1
            prob += RD[i][j] == O[i][j] #must have reopening cost if operating
        else: #for all other years 
            prob += RD[i][j] >= O[i][j] - O[i-1][j] #must not have been in operation the year prior
        #Shutdowncosts only exist if plant not operating this year but had been operating the year before
        if i > 0: #Shutdown not possible for zero year since no prior value available and cant go out of range and more contextually business did not exist
            prob += SD[i][j] >= O[i-1][j] - O[i][j]
        #Construction 
        
    #Shipping Constraints - Warehouses
for i in Y: #for each year
    for k in W: #and each warehouse
        globals()[f'TotalStorageY{i}W{k}'] = 0 #Warehouse storage by plant
        globals()[f'TotalOutputY{i}W{k}'] = 0  #warehouse output by retailer
        for j in P: #sum by plant
            globals()[f'TotalStorageY{i}W{k}'] += PWF[i][j][k]
        #total flugels received by warehouse does not exceed avg. yearly flugel storage capacity
        prob += globals()[f'TotalStorageY{i}W{k}'] <= FMax
        for j in R: #sum by retailer
            globals()[f'TotalOutputY{i}W{k}'] += WRF[i][k][j]
        #flow into warehouse must be equivalent to flow out of warehouse
        prob += globals()[f'TotalStorageY{i}W{k}'] == globals()[f'TotalOutputY{i}W{k}']
        
    #Shipping Constraints - Retail Centers
for i in Y: #for each year
    for k in R: #and each retail center
        globals()[f'TotalInventoryY{i}R{k}'] = 0 
        for j in W: #across all warehouses
            globals()[f'TotalInventoryY{i}R{k}'] += WRF[i][j][k]
        #total flugels received by retailer must meet demand each year
        prob += globals()[f'TotalInventoryY{i}R{k}'] = D[i][k]

    #Construction Binary Constraints
for j in P: # for each p
    YearsofOperation = 0 #Plant not operational yet
    for i in Y: #loop through years
        YearsofOperation += O[i][j] #if not operation, 0 is added, otherwise 1 year is added
        #Plant only in construction if operational this year, but never any in the past. i.e. "Years of Operation" is 0
        prob += CD[i][j] >= O[i][j] - YearsofOperation
        
#Objective
    #minimizes total cost of meeting expected demand over the next 10 years
#Cost summations
    #Alloy Costs
TotalAlloyCosts = 0
for i in Y:
    for j in P:
        for k in W:
            TotalAlloyCosts += PWF[i][j][k]*APF*AC[i]

    #Shipping Costs - Plant to Warehouse
TotalPWSC = 0
for i in Y:
    for j in P:
        for k in W:
            TotalPWSC += PWSC[i][j][k]*PWF[i][j][k]
            
    #Shipping Costs - Warehouse to Retailer
TotalWRSC = 0
for i in Y:
    for j in W:
        for k in R:
            TotalWRSC += PWSC[i][j][k]*WRF[i][j][k]
            
    #Plant Costs - Operating
TotalOperating = 0
for i in Y:
    for j in P:
        TotalOperating += O[i][j]*OC[i][j]
        
    #Plant Costs - Construction
TotalConstruction = 0
for i in Y:
    for j in P:
        TotalConstruction += CD[i][j]*CC[i][j]
        
    #Plant Costs - Reopening
TotalReopening = 0
for i in Y:
    for j in P:
        TotalReopening += RD[i][j]*RC[i][j]
        
    #Plant Costs - Shutdown
TotalShutdown = 0
for i in Y:
    for j in P:
        TotalShutdown += SD[i][j]*SC[i][j]
        
    #Widget Costs (formula derived on formulation sheet)
TotalWidget = 0
for i in Y:
    for j in P:
        TotalWidget += 0*Lambda1 + ((WTD/WPF)*OWC[i])*Lambda2 + ((WTD/WPF)*OWC[i] + (PC[j] - (WTD/WPF))*DWC[i])*Lambda3
        
#Sum the costs

prob += TotalAlloyCosts + TotalPWSC + TotalWRSC + TotalOperating + TotalConstruction + TotalReopening + TotalShutdown + TotalWidget
        
status = prob.solve()

print(f"status={LpStatus[status]}")        
        
        

#Variables

#Whether or not to use plant that year, which will impact construction, operating and shutdown costs

#NOTE: I think a node illustration would be good

#How many flugels to send from plant p to warehouse w each year

#How many flugels to send from warehouse w to retail center r each year


#Constraints

#Flugels sent from each plant to warehouses must sum to less than or equal to the production capacity of that plant each year

#Flugels sent from plant to each warehouse must sum to less than or equal to the yearly average flugel capacity of that warehouse each year

#Flugels sent from warehouses to each retail center must sum to the demand of that retail center each year

#Flugels sent from warehouses to each retail center must not exceed flugels sent from all plants to that warehouse each year

#Each plant can acquire at most 60000 pounds of alloy i.e number of flugels made by plant cannot exceed necessary allow limit

#Constraints for warehouse shutdowns and whatnot

#Output
    #NOTE: I would recommend a breakdown of the yearly costs, production numbers, warehouse storage numbers, and shipping numbers using these tables:
        #Production Costs/Plant 1/Plant 2/etc for each year or year 1/year 2/ etc. for each plant
            #Number of Flugels
            #Input Costs
                #Widgets
                #Alloy
            #Opening Costs
            #Operating Costs
            #Reopening Costs
            #ShutDown Costs
            #Total Costs
        
        #Shipping Costs and number shipped in a grid with plants and warehouses with a total bar grouped by plant
        
        #Shipping Costs and number shipped in a grid with warehouses and retailers with a total bar grouped by warehouse (tho maybe one on both axis)
        
    #An analysis of the results and perhaps some interesting conclusions and recommendations would be a good idea
    #Given that the results are time series, some time series line graphs would also be interesting tracking costs
    
    #I know this isnt technically what they recommend but perhaps we make each node in a flow chart a pie graph so that way we can conceptualize capacity and what numbers come from where
    #I actually think it could look really cool and would be hella fun to code imo


