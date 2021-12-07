# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 20:08:28 2021

@author: dylan
"""
#Optimization Project
#Team 2: Anoushka Mahar, Riti Dabas, Dylan Koury

from gurobipy import *
from pulp import LpVariable, LpProblem, LpMaximize, LpStatus, value, LpMinimize, lpSum
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as pat
from matplotlib.patches import Polygon, ConnectionPatch
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
        temp.append(RetailDemand1[j]+(RetailDemand1[j]*DemandGrowthRate[j]*i)) #creating matrix of yearly costs
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
            temp2.append(LpVariable(f'FY{i}P{j}W{k}',0,PC[j])) #non-negative and cannot exceed total plant capacity but constraint will have to be dealt with on sum as well
        temp.append(temp2)
    PWF.append(temp)
    
    #Flugel Numbers sent yearly from warehouse to retailer
WRF = []
for i in Y:
    temp = []
    for j in W:
        temp2 = []
        for k in R:
            temp2.append(LpVariable(f'FY{i}W{j}R{k}',0,FMax)) #non-negative and cannot exceed total warehouse but constraint will have to be dealt with on sum as well
        temp.append(temp2)
    WRF.append(temp)
    
      #Remaining flugel inventory numbers for warehouse W in year Y
EI = []
for i in Y:
    temp = []
    for j in W:
        temp.append(LpVariable(f'EIY{i}W{j}',0,FMax)) #non-negative and cannot exceed total warehouse capacity but also dealt with in constraints
    EI.append(temp)
    
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
SD = []
for i in Y:
    temp = []
    for j in P:
        temp.append(LpVariable(f'SDY{i}P{j}', cat="Binary"))
    SD.append(temp)
        
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
        
        
    #Shipping Constraints - Warehouses
for i in Y: #for each year
    for k in W: #and each warehouse
        globals()[f'TotalStorageY{i}W{k}'] = 0 #Warehouse storage by plant
        globals()[f'TotalOutputY{i}W{k}'] = 0  #warehouse output by retailer
        for j in P: #sum by plant shipments
            globals()[f'TotalStorageY{i}W{k}'] += PWF[i][j][k]
        #total flugels received by warehouse does not exceed avg. yearly flugel storage capacity
        prob += globals()[f'TotalStorageY{i}W{k}'] <= FMax
        if i > 0: #year 0 cannot have prior inventory and deal with list out of range, but other years do
            globals()[f'TotalStorageY{i}W{k}'] += EI[i-1][k] #inflow plus remaining inventory
        #Average inventory cannot exceed inventory maximum capacity
        if i == 0: #year 1 has no prior inventory, must be dealt with separately
            prob += 0.5*EI[i][k] <= IMax #average will be (0 + end inventory)/2
        else: #all other years do have remaining inventory
            prob += 0.5*EI[i-1][k] + 0.5*EI[i][k] <= IMax #average of starting and ending inventory cannot exceed 4000
        for j in R: #sum by retailer
            globals()[f'TotalOutputY{i}W{k}'] += WRF[i][k][j]
        #Total flugels sent out of warehouse must not exceed avg yearly flugel storage capacity
        prob += globals()[f'TotalOutputY{i}W{k}'] <= FMax
        globals()[f'TotalOutputY{i}W{k}'] += + EI[i][k] #total outflow includes sent to retailers plus remaining inventory
        #flow into warehouse must be equivalent to flow out of warehouse (and inventory level differences)
        prob += globals()[f'TotalStorageY{i}W{k}'] == globals()[f'TotalOutputY{i}W{k}']
        
    #Shipping Constraints - Retail Centers
for i in Y: #for each year
    for k in R: #and each retail center
        globals()[f'TotalInventoryY{i}R{k}'] = 0 
        for j in W: #across all warehouses
            globals()[f'TotalInventoryY{i}R{k}'] += WRF[i][j][k]
        #total flugels received by retailer must meet demand each year
        prob += globals()[f'TotalInventoryY{i}R{k}'] == D[i][k]

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
            TotalWRSC += WRSC[i][j][k]*WRF[i][j][k]
            
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
        TotalWidget += 0*L1[i][j] + ((WTD/WPF)*OWC[i])*L2[i][j] + ((WTD/WPF)*OWC[i] + (PC[j] - (WTD/WPF))*DWC[i])*L3[i][j]
        
#Sum the costs

prob += TotalAlloyCosts + TotalPWSC + TotalWRSC + TotalOperating + TotalConstruction + TotalReopening + TotalShutdown + TotalWidget
        
status = prob.solve()

print(f"status={LpStatus[status]}")   


#create graph of supply chain nodes
    
Pcolors = ['lightblue','lightgreen','lightpink','yellow','thistle']     
Wcolors= ['blue','green','red','purple']

for i in Y:
    fig,ax = plt.subplots()
    plt.ylim(0,520)
    plt.xlim(0,720)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    
    for j in P:
        Production = 0
        for k in W:
            Production += (abs(PWF[i][j][k].varValue)/PC[j])
            if PWF[i][j][k].varValue > 0:
                globals()[f"conY{i}P{j}W{k}"] = ConnectionPatch(xyA=(170 + 40,470-(100*j)), xyB=(360-35,460-(130*k)), coordsA='data',coordsB='data',arrowstyle="->", shrinkB=0,axesA=ax,axesB=ax)
                ax.add_artist(globals()[f"conY{i}P{j}W{k}"])
        plt.pie([Production,1-Production], colors=[Pcolors[j], 'white'], radius=40,normalize=True,center=(170,470-(100*j)), wedgeprops={'clip_on':True, 'linewidth': .7, 'edgecolor':'black'},frame=True)
        circle6 = plt.Circle([170,470-(100*j)],radius= 40, color='black', fill=False)
        ax.add_artist(circle6)
        ax.text(40,500-(100*j), f"Plant {j+1}", size=5, ha="center", va = "center", weight='bold')
        ax.text(40,480-(100*j), f"Units Produced:\n{round(Production*PC[j])}", size=4.5, ha="center", va = "center")
        ax.text(40,450-(100*j), f"Percent Capacity:\n{round(Production*100)}%", size=4.5, ha="center", va="center")
    
    for j in W:
        Inventory = []
        for k in P:
            Inventory.append(abs(PWF[i][k][j].varValue)/(FMax+IMax))
        if i > 0:
            Inventory.append(EI[i-1][j].varValue/(FMax+IMax))
        else:
            Inventory.append(0)
        plt.pie(Inventory, colors=['lightblue','lightgreen','lightpink','yellow','thistle','gray','white'], radius=35,normalize=False,center=(360,460-(130*j)), wedgeprops={'clip_on':True, 'linewidth': .7, 'edgecolor': Wcolors[j]},frame=True)
        circle6 = plt.Circle([360,460-(130*j)],radius= 35, color=Wcolors[j], fill=False)
        ax.add_artist(circle6)
        ax.text(360,510-(130*j), f"Warehouse {j+1}", size=5, ha="center", va = "center", weight='bold')
        ax.text(360,415-(130*j), f"Units Stored: {round(sum(Inventory)*(FMax+IMax))}", size=4.5, ha="center", va = "center")
        ax.text(360,400-(130*j), f"Percent Capacity: {round(sum(Inventory)*100)}%", size=4.5, ha="center", va="center")
    


    for j in R:
        DemandFulfill = []
        for k in W:
            DemandFulfill.append(WRF[i][k][j].varValue/D[i][j])
            if WRF[i][k][j].varValue > 0:
                globals()[f"conY{i}R{j}W{k}"] = ConnectionPatch(xyA=(360+35,460-(130*k)), xyB=(575-28,480-(64*j)), coordsA='data',coordsB='data',arrowstyle="->", shrinkB=0,axesA=ax,axesB=ax)
                ax.add_artist(globals()[f"conY{i}R{j}W{k}"])
        plt.pie(DemandFulfill, colors=Wcolors, radius=28,normalize=False,center=(575,480-(64*j)), wedgeprops={'clip_on':True, 'linewidth': .7, 'edgecolor':'black'},frame=True)
        circle6 = plt.Circle([575,480-(64*j)],radius= 28, color='black', fill=False)
        ax.add_artist(circle6)
        ax.text(670,510-(64*j), f"Retail Center {j+1}", size=5, ha="center", va = "center", weight='bold')
        ax.text(670,490-(64*j), f"Units Demanded:\n{round(D[i][j])}", size=4.5, ha="center", va = "center")
        ax.text(670,465-(64*j), f"Percent Fulfuilled:\n{round(sum(DemandFulfill)*100)}%", size=4.5, ha="center", va="center")
    
    
    
    plt.title(f"Flugel Supply Chain Year {i + 1}", size=10)
    
    plt.show





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


