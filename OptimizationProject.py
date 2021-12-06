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
R = 8 #number of retail centers
W = 4 #number of warehouses
P = 5 #number of plants
Y = 10 #number of years

#Retailers Data
RetailDemand1 = [1000,1200,1800,1200,1000,1400,1600,1000] #Demand Year 1
DemandGrowthRate = [0.2,0.2,0.25,0.2,0.2,0.25,0.25,0.2] #yearly demand growth rates 

#Plant Data
Capacity = [16000,12000,14000,10000,13000] #in units
ConstructionCost = [2000,1600,1800,900,1500] #in 1000s of $
OperatingCost = [420,380,460,280,340] #in 1000s of $
ReopeningCost = [190,150,160,100,130] #in 1000s of $
ShutdownCost = [170,120,130,80,110] #in 1000s of $

#Warehouse Data
MaxAvgInventory = 4000 #in number of items
MaxMonthlyAvg = 1000 #number of flugels per month any warehouse on average can handle

#Flugel Production Data
AlloyPerFlugel = 4.7 #in lbs
MaxAlloyPerPlant = 60000 #in lbs any plant can acquire per year
AlloyCost1 = 0.02 #in 1000s of $ for a pound of alloy in year 1
WidgetPerFlugel = 3
OriginalWidgetCost1 = 0.15 #in 1000s of $ for a widget in year 1
DiscountWidgetCost1 = 0.12 #cost for widget after 9000 purchased
NoDiscount = 9000 #how many widgets must be ordered before discount applied

#Shipping from plant to warehouse  in 1000s 0f $
PlantWarehouseShippingCost = [[0.12,0.13,0.08,0.05],#Plant 1
                              [0.1,0.03,0.1,0.09],  #Plant 2
                              [0.05,0.07,0.06,0.03],#Plant 3
                              [0.06,0.03,0.07,0.07],#Plant 4
                              [0.06,0.02,0.04,0.08]]#Plant 5

#Shipping from warehouse to retail center  in 1000s 0f $
WarehouseRetailShippingCost = [[0.09,0.1,0.06,0.05,0.08,0.09,0.02,0.12],
                               [0.05,0.07,0.12,0.04,0.03,0.09,0.03,0.08],
                               [0.06,0.09,0.07,0.09,0.09,0.04,0.11,0.07],
                               [0.07,0.08,0.09,0.06,0.1,0.07,0.06,0.09]]

CostGrowthRate = 0.03

#Objective
    #minimizes total cost of meeting expected demand over the next 10 years
    #NOTE: I recommend using if statements, loops, and summations



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


