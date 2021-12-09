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
import numpy as np

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
        #Also set equal to widget cost structure
        prob += 0*(L1[i][j])+(WTD/WPF)*(L2[i][j])+PC[j]*(L3[i][j]) == globals()[f'TotalSupplyY{i}P{j}']
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
    for i in Y: #loop through years
        if i==0:
            YearsofOperation = 0 #Plant not operational yet
        else:
            YearsofOperation += O[i-1][j] #if not operation, 0 is added, otherwise 1 year is added
        #Plant only in construction if operational this year, but never any in the past. i.e. "Years of Operation" is 0
        prob += CD[i][j] >= O[i][j] - YearsofOperation
        
#Objective
    #minimizes total cost of meeting expected demand over the next 10 years
#Cost summations
    #Alloy Costs
TAC = []
TotalAlloyCosts = 0
for i in Y:
    temp = []
    for j in P:
        temp2 = []
        for k in W:
            TotalAlloyCosts += PWF[i][j][k]*APF*AC[i]
            temp2.append(PWF[i][j][k]*APF*AC[i])
        temp.append(temp2)   
    TAC.append(temp)

    #Shipping Costs - Plant to Warehouse
TotalPWSC = 0
TPWSC = []
for i in Y:
    temp = []
    for j in P:
        temp2 = []
        for k in W:
            TotalPWSC += PWSC[i][j][k]*PWF[i][j][k]
            temp2.append(PWSC[i][j][k]*PWF[i][j][k])
        temp.append(temp2)   
    TPWSC.append(temp)
            
    #Shipping Costs - Warehouse to Retailer
TotalWRSC = 0
TWRSC = []
for i in Y:
    temp = []
    for j in W:
        temp2 = []
        for k in R:
            TotalWRSC += WRSC[i][j][k]*WRF[i][j][k]
            temp2.append(WRSC[i][j][k]*WRF[i][j][k])
        temp.append(temp2)   
    TWRSC.append(temp)
        
    #Plant Costs - Operating
TotalOperating = 0
TO = []
for i in Y:
    temp = []
    for j in P:
        TotalOperating += O[i][j]*OC[i][j]
        temp.append(O[i][j]*OC[i][j])
    TO.append(temp)
        
    #Plant Costs - Construction
TotalConstruction = 0
TC = []
for i in Y:
    temp = []
    for j in P:
        TotalConstruction += CD[i][j]*CC[i][j]
        temp.append(CD[i][j]*CC[i][j])
    TC.append(temp)
        
    #Plant Costs - Reopening
TotalReopening = 0
TR = []
for i in Y:
    temp = []
    for j in P:
        TotalReopening += RD[i][j]*RC[i][j]
        temp.append(RD[i][j]*RC[i][j])
    TR.append(temp)
        
    #Plant Costs - Shutdown
TotalShutdown = 0
TS = []
for i in Y:
    temp = []
    for j in P:
        TotalShutdown += SD[i][j]*SC[i][j]
        temp.append(SD[i][j]*SC[i][j])
    TS.append(temp)
        
    #Widget Costs (formula derived on formulation sheet)
TotalWidget = 0
TW = []
for i in Y:
    temp = []
    for j in P:
        TotalWidget += 0*L1[i][j] + ((WTD)*OWC[i])*L2[i][j] + ((PC[j] - (WTD/WPF))*WPF*DWC[i])*L3[i][j]
        temp.append(0*L1[i][j] + ((WTD)*OWC[i])*L2[i][j] + ((PC[j] - (WTD/WPF))*WPF*DWC[i])*L3[i][j])
    TW.append(temp)
        
#Sum the costs
objective = TotalAlloyCosts + TotalPWSC + TotalWRSC + TotalOperating + TotalConstruction + TotalReopening + TotalShutdown + TotalWidget
prob += objective
        
status = prob.solve()

print(f"status={LpStatus[status]}")   
print(f"Cost=${round(value(objective)*1000,2)}") 


#Supply Chain Nodes
    
Pcolors = ['lightblue','lightgreen','lightpink','yellow','thistle']     
Wcolors= ['blue','green','red','purple']
YCost = []
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
            Production += (abs(round(PWF[i][j][k].varValue))/PC[j])
            if PWF[i][j][k].varValue > 0:
                globals()[f"conY{i}P{j}W{k}"] = ConnectionPatch(xyA=(170 + 40,470-(100*j)), xyB=(360-35,460-(130*k)), coordsA='data',coordsB='data',arrowstyle="->", shrinkB=0,axesA=ax,axesB=ax)
                ax.add_artist(globals()[f"conY{i}P{j}W{k}"])
        plt.pie([Production,1-Production], colors=[Pcolors[j], 'white'], radius=40,normalize=False,center=(170,470-(100*j)), wedgeprops={'clip_on':True, 'linewidth': .7, 'edgecolor':'black'},frame=True)
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
    
    ax.text(0,0,"Total Cost:",size=8, weight = 'bold')
    YearlyCost = str(round(value(lpSum(TAC[i] + TPWSC[i] + TWRSC[i] + TO[i] + TC[i] + TR[i] + TS[i] + TW[i])))*1000)
    YCost.append(int(YearlyCost))  
    ax.text(120,0,f"${YearlyCost[:-6]},{YearlyCost[-6:-3]},{YearlyCost[-3:]}",size=8)
    
    plt.title(f"Flugel Supply Chain Year {i + 1}", size=10)
    
    plt.show

#Demand Chart
RColors = ['red','orange','black','green','blue','purple','pink','brown']
fig,ax = plt.subplots()
plt.ylim(0,7000)
plt.xlim(1,11)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
DLegend = []
for i in R:
    DLegend.append(pat.Patch(color=RColors[i], label=f"{i+1}"))
    for j in Y: 
        if j == 0:
            continue
        elif j == max(Y):
            con = ConnectionPatch(xyA=(j,D[j-1][i]), xyB=(j+1,D[j][i]), coordsA='data',coordsB='data',arrowstyle="->", shrinkB=0,axesA=ax,axesB=ax, color = RColors[i])
            ax.add_artist(con)
            ax.text(j+1.2,D[j][i],str(round(D[j][i])),size=8)
        else:
            con = ConnectionPatch(xyA=(j,D[j-1][i]), xyB=(j+1,D[j][i]), coordsA='data',coordsB='data',arrowstyle='-', shrinkB=0,axesA=ax,axesB=ax, color = RColors[i])
            ax.add_artist(con)
ax.legend(loc="upper left", handles=DLegend,title="Retail Centers",prop={'size': 7})
ax.set_xlabel("Year")
ax.set_ylabel("Demand (units)")
plt.title("Projected Flugel Demand")
plt.show


#Plant Cost Charts 
PColors = ['red','orange','green','blue','purple']
RValues = [TO,TS,TR,TC]
PValues = [OC,SC,RC,CC]
CTitles = ["Operating","Shutdown","Reopening","Construction"]
for i in range(len(PValues)):
    fig,ax = plt.subplots()
    ax.set_xticks(range(1,11))
    plt.xlim(1,11)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    Legend = []
    Legend.append(pat.Patch(color='black', label=f"Realized"))
    for j in P:
        Legend.append(pat.Patch(color=PColors[j], label=f"Plant {j+1}"))
        line = []
        for k in Y: 
            line.append(PValues[i][k][j])
        plt.plot(range(1,11),line,c=PColors[j],ls='-')
    line = []
    for k in Y:
        line.append(value(lpSum(RValues[i][k])))
    plt.plot(range(1,11),line,c='black',ls='-')
    ax.legend(loc=[.05,.75], handles=Legend,prop={'size': 7})
    ax.set_xlabel("Year")
    ax.set_ylabel("Cost (1000s of $)")
    Total = str(round(value(lpSum(RValues[i]))*1000))
    if len(Total) > 6:
        plt.title(f"Projected/Realized {CTitles[i]} Costs\n${Total[:-6]},{Total[-6:-3]},{Total[-3:]}")
    else:
        plt.title(f"Projected/Realized {CTitles[i]} Costs\n${Total[-6:-3]},{Total[-3:]}")
    plt.show
    
#Total Cost bar chart
Costs =  [TAC,TPWSC ,TWRSC, TO, TC ,TR , TS , TW]
label = ['Alloy Cost','P2W Shipping', 'W2R Shipping','Operations','Construction','Reopening Cost','Shutdown Cost','Widget Cost']
fig,ax = plt.subplots()
plt.ylim(0,22000)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
colors = ['red','blue','orange','green','yellow','purple','brown','pink']
heightsold = [0,0,0,0,0,0,0,0,0,0]
width = .8
ticks = []
CLegend = []

for j in range(len(Costs)):
    CLegend.append(pat.Patch(color=colors[j], label=label[j]))
    heightsnew = []
    ticks = []
    for i in Y:
        ticks.append(f"{i+1}")
        heightsnew.append(value(lpSum(Costs[j][i])))
    ax.bar(ticks, heightsnew, width=width, bottom = heightsold, label=label[j])
    for i in Y:
        heightsold[i] += heightsnew[i]
Total = str(round(value(objective)*1000))
if len(Total) > 6:
    plt.title(f"Yearly Flugel Production Cost Strategy\n${Total[:-6]},{Total[-6:-3]},{Total[-3:]}")
else:
    plt.title(f"Yearly Flugel Production Cost Strategy\n${Total[-6:-3]},{Total[-3:]}")
ax.set_xlabel("Year")
ax.set_ylabel("Cost (1000s of $)")
ax.legend(loc=[.05,.72],title="Cost Type",prop={'size': 5})
plt.axhline(sum(YCost)/1000/len(YCost), color='k')
plt.show
    
#Plant to warehouse shipping numbers
for i in Y:
    fig,ax = plt.subplots()
    plt.ylim(17,72)
    plt.xlim(0,270)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    plt.title("Plants: Flugel Production and Shipping Strategy", size=14,ha="center",weight='bold')
    ax.text(10,65, s=f"Year {i+1}", size=9, ha="center", va="center", wrap=True, weight = 'bold')
    plt.arrow(0,62,270,0, width=.1,color="black",head_width=None)
    ax.text(40,65, s=f"Status", size=9, ha="center", va="center", wrap=True)
    plt.arrow(26,68,0,-45, width=.1,color="black",head_width=None)
    ax.text(140,70, s=f"Warehouse", size=11, ha="center", va="center", wrap=True, weight = 'bold')
    ax.text(240,65, s=f"Total", size=9, ha="center", va="center", wrap=True)
    plt.arrow(220,68,0,-45, width=.1,color="black",head_width=None)
    
    for j in W:
        ax.text(80+(j*40),65, s=f"{j+1}", size=9, ha="center", va="center", wrap=True)
        plt.arrow(58+(j*40),68,0,-45, width=.1,color="black",head_width=None)
        Total = 0
        for k in P:
            Total += PWF[i][k][j].varValue
        ax.text(80+(j*40),25, s=round(Total), size=9, ha="center", va="center", wrap=True)
    for j in P:
        ax.text(10,58-(j*7), s=f"Plant {j+1}", size=9, ha="center", va="center", wrap=True)
        if CD[i][j].varValue == 1:
            ax.text(40,58-(j*7), s=f"BUILD", size=9, ha="center", va="center", wrap=True)
        elif O[i][j].varValue == 1:
            ax.text(40,58-(j*7), s=f"OPEN", size=9, ha="center", va="center", wrap=True)
        else:
            ax.text(41,58-(j*7), s=f"CLOSED", size=9, ha="center", va="center", wrap=True)
        plt.arrow(0,55-(j*7),270,0, width=.1,color="black",head_width=None)
        ax.text(240,58-(j*7), s=round(value(lpSum(PWF[i][j]))), size=9, ha="center", va="center", wrap=True)
        for k in W:
            ax.text(80+(k*40),58-(j*7), s=round(PWF[i][j][k].varValue), size=9, ha="center", va="center", wrap=True)
    ax.text(10,25, s=f"Total", size=9, ha="center", va="center", wrap=True)
    ax.text(240,25, s=round(value(lpSum(PWF[i]))), size=9, ha="center", va="center", wrap=True)
    ax.text(50,20, s=f"Total Shipping Cost:", size=12, ha="center", va="center", wrap=True, weight = 'bold')
    Cost = str(round(value(lpSum(TPWSC[i]))*1000))
    if len(Cost) > 6:
        ax.text(110,20, s=f"${Cost[:-6]},{Cost[-6:-3]},{Cost[-3:]}", size=12, va="center", wrap=True)
    else:
        ax.text(110,20, s=f"${Cost[:-3]},{Cost[-3:]}", size=12, va="center", wrap=True)
    plt.show
    
#Warehouse to retailer shipping numbers
for i in Y:    
    fig,ax = plt.subplots()
    plt.ylim(-25,75)
    plt.xlim(-10,270)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    plt.title("Warehouses: Flugel Shipping Strategy", size=14,ha="center",weight='bold')
    ax.text(25,65, s=f"Year {i+1}", size=9, ha="center", va="center", wrap=True,weight='bold')
    plt.arrow(-10,62,280,0, width=.1,color="black",head_width=None)
    
    
    ax.text(150,71, s=f"Warehouse", size=11, ha="center", va="center", wrap=True, weight='bold')
    ax.text(250,65, s=f"Total", size=9, ha="center", va="center", wrap=True)
    plt.arrow(230,68,0,-83, width=.1,color="black",head_width=None)
    ax.text(28,58, s=f"Starting Inventory", size=9, ha="center", va="center", wrap=True)
    plt.arrow(-10,55,280,0, width=.1,color="black",head_width=None)
    ax.text(28,51, s=f"Incoming Inventory", size=9, ha="center", va="center", wrap=True)
    plt.arrow(-10,48,280,0, width=.1,color="black",head_width=None)
    for j in W:
        ax.text(90+(j*40),65, s=f"{j+1}", size=9, ha="center", va="center", wrap=True)
        plt.arrow(69+(j*40),68,0,-83, width=.1,color="black",head_width=None)
        if i == 0:
            ax.text(90+(j*40),58, s=f"0", size=9, ha="center", va="center", wrap=True)
        else:
            ax.text(90+(j*40),58, s=round(EI[i-1][j].varValue), size=9, ha="center", va="center", wrap=True)
        ax.text(90+(j*40),-12, s=round(EI[i][j].varValue), size=9, ha="center", va="center", wrap=True)
        Total = 0
        for k in P:
            Total += PWF[i][k][j].varValue
        ax.text(90+(j*40),51, s=round(Total), size=9, ha="center", va="center", wrap=True)
        for k in R:
            ax.text(90+(j*40),44-(k*7), s=round(WRF[i][j][k].varValue), size=9, ha="center", va="center", wrap=True)
    
    for j in R:
        ax.text(30,44-(j*7), s=f"Retail Center {j+1}", size=9, ha="center", va="center", wrap=True)
        Total = 0
        for k in W:
            Total += WRF[i][k][j].varValue
        ax.text(250,44-(j*7), s=round(Total), size=9, ha="center", va="center", wrap=True)
        plt.arrow(-10,41-(j*7),280,0, width=.1,color="black",head_width=None)
    ax.text(28,-12, s="Remaining Inventory", size=9, ha="center", va="center", wrap=True)
    ax.text(50,-20, s=f"Total Shipping Cost:", size=12, ha="center", va="center", wrap=True, weight = 'bold')
    Cost = str(round(value(lpSum(TWRSC[i]))*1000))
    if len(Cost) > 6:
        ax.text(110,-20, s=f"${Cost[:-6]},{Cost[-6:-3]},{Cost[-3:]}", size=12, va="center", wrap=True)
    else:
        ax.text(110,-20, s=f"${Cost[:-3]},{Cost[-3:]}", size=12, va="center", wrap=True)
    plt.show

Used = []        
for j in P:
    Total = 0
    for i in Y:
        Total += CD[i][j].varValue
    Used.append(Total)

#Widget Cost bar chart    
for i in range(len(Used)):
    if Used[i] == 1:
        label = ['Regular Pricee','Discount Price']
        fig,ax = plt.subplots()
        plt.ylim(0,7000)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        colors = ['red','blue']
        width = .8
        ticks = []
        WLegend = []
        for j in range(len(colors)):
            WLegend.append(pat.Patch(color=colors[j], label=label[j]))
        RCosts = []
        DCosts = []
        for j in Y:
            ticks.append(f"{j+1}")
            if value(lpSum(PWF[j][i]))*WPF > WTD:
                RCosts.append(WTD*OWC[j])
                DCosts.append((value(lpSum(PWF[j][i]))*WPF-(WTD))*DWC[j])  
            else:
                RCosts.append(value(lpSum(PWF[j][i]))*WPF*OWC[j])
                DCosts.append(0)
        ax.bar(ticks, RCosts, width=width, bottom = [0,0,0,0,0,0,0,0,0,0], label=label[0],fc=colors[0])
        ax.bar(ticks, DCosts, width=width, bottom = RCosts, label=label[1],fc=colors[1])

        Total = str(round(sum(RCosts)+sum(DCosts)*1000))
        if len(Total) > 6:
            plt.title(f"Plant {i+1} Widget Order Costs\n${Total[:-6]},{Total[-6:-3]},{Total[-3:]}")
        else:
            plt.title(f"Plant {i+1} Widget Order Costs\n${Total[-6:-3]},{Total[-3:]}")
        ax.set_xlabel("Year")
        ax.set_ylabel("Cost (1000s of $)")
        ax.legend(loc=[.05,.78],handles =WLegend, title="Cost Type",prop={'size': 8})
        plt.show

#Allot cost bar chart
for i in range(len(Used)):
    if Used[i] == 1:        
        fig,ax = plt.subplots()
        plt.ylim(0,2500)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        width = .8
        ticks = []

        ACosts = []

        for j in Y:
            ticks.append(f"{j+1}")
            ACosts.append(value(lpSum(PWF[j][i]))*APF*AC[j]) 
        ax.bar(ticks, ACosts, width=width)

        Total = str(round(sum(RCosts)*1000))
        if len(Total) > 6:
            plt.title(f"Plant {i+1} Alloy Order Costs\n${Total[:-6]},{Total[-6:-3]},{Total[-3:]}")
        else:
            plt.title(f"Plant {i+1} Alloy Order Costs\n${Total[-6:-3]},{Total[-3:]}")
        ax.set_xlabel("Year")
        ax.set_ylabel("Cost (1000s of $)")
        plt.show

#Flugel Production and resource order numbers
for i in range(len(Used)):
    if Used[i] == 1:        
        fig,ax = plt.subplots()
        plt.ylim(-7.5,75)
        plt.xlim(15,230)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.axes.xaxis.set_visible(False)
        ax.axes.yaxis.set_visible(False)
        plt.title(f"Plant {i + 1}: Production Strategy", size=14,ha="center",weight='bold')
        ax.text(30,65, s=f"Year", size=9, ha="center", va="center", wrap=True,weight='bold')
        plt.arrow(-10,62,280,0, width=.1,color="black",head_width=None)
        
        ax.text(170,71, s=f"Resources", size=11, ha="center", va="center", wrap=True, weight='bold')
        plt.arrow(50,68,0,-83, width=.1,color="black",head_width=None)
        ax.text(80,65, s=f"Flugels", size=9, ha="center", va="center", wrap=True,weight='bold')
        plt.arrow(110,68,0,-83, width=.1,color="black",head_width=None)
        ax.text(140,65, s=f"Alloy (lbs)", size=9, ha="center", va="center", wrap=True,weight='bold')
        plt.arrow(170,68,0,-83, width=.1,color="black",head_width=None)
        ax.text(200,65, s=f"Widgets", size=9, ha="center", va="center", wrap=True,weight='bold')

        for j in Y:
            ax.text(30,58-(j*7), s=f"{j+1}", size=9, ha="center", va="center", wrap=True)
            plt.arrow(-10,55-(j*7),280,0, width=.1,color="black",head_width=None)
            Total = 0
            for k in W:
                Total += PWF[j][i][k].varValue
            ax.text(80,58-(j*7), s=round(Total), size=9, ha="center", va="center", wrap=True,weight='bold')
            ax.text(140,58-(j*7), s=round(Total*APF), size=9, ha="center", va="center", wrap=True,weight='bold')
            ax.text(200,58-(j*7), s=round(Total)*WPF, size=9, ha="center", va="center", wrap=True,weight='bold')
            
