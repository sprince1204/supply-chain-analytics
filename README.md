# Supply Chain Analytics Project

## General Information
This project was undertaken as part of the RWTH Aachen Business School Analytics Project for Barkawi Group, a consultancy firm specializing in Supply Chain Optimization. The project focuses on Supply Chain analytics to evaluate the effect of re-balancing inventory between retail outlets by modeling the uncertainties of demand using a stochastic dynamic program to optimize the supply plan.

### Project Phases
1. **Demand Forecasting**: The first phase involved forecasting demand.
2. **Supply Planning**: The second phase involved building a supply plan based on forecasted demand.
3. **Stochastic Modeling**: The third phase incorporated demand uncertainties into the supply plan using a stochastic dynamic program.

### Model Details
- **Hub-Spoke Model**: Inventories of retail outlets are replenished weekly from the central warehouse, subject to Minimum Order Quantity constraints.
- **Re-balancing Inventory**: Introduced re-balancing of inventory between outlets along with weekly replenishments from the central warehouse.
- **Optimization**: The supply decisions aim to minimize total costs, including transport costs, inventory holding costs, and costs due to loss of sales.
- **Stochastic Dynamic Program**: Demand uncertainties are modeled using scenarios generated around deterministic demand forecasts, with probabilities assigned using a triangular distribution.

## Questions 
We are given 10 outlets j = 1, 2... 10, and warehouse j = 0 in France.
Set of all products sold by the company is also given.
Time horizon is considered as 2 weeks.
We know the demand D for 2 subsequent week (week t = 0 =current week)
at every outlet j for each product. This is a result of forecasting carried out over past 3 years demand data.
We know the stock at each outlet j = S for week t and all products p.
We know the distance x between all centres to compute the cost of transportation.
Every week we run a decision model once to replenish the inventory at each outlet in two ways:
- From the warehouse, where the lead time is one week => products ordered today will arrive next week.
- Rebalancing from other outlets, where lead time is zero => products ordered today arrive immediately.
The warehouse and the outlets have no capacity constraints. The arcs also have no capacity constraints.
For material stored at the outlets we have identical inventory holding costs H.
For Transportation Cost G we assume a dependence on the distance and amount of material transported on each arc
We need to model this and at the beginning of each week determine what quantity of each product is to be
rebalanced between the outlets and how much has to be ordered from the warehourse for each outlet
so that the overall cost is minimized.
We do the optimisation for only a particular product for all the ten outlets. 

IDEA OF SOLUTION:
We define a dynamic model where over two weeks we model the flow through the network. 

## Instructions for Running the Code

### Step-by-Step Guide
1. **Save the demand forecasts and demand scenarios as a CSV file**:
   - Column 1: Forecasted demand value for week 0.
   - Columns 2-6: Demand scenarios for week 0 (various percentages of the expected value).
   - Columns 7-12: Forecasted demand value and scenarios for week 1.

2. **Ensure the demand scenarios have at least one unit difference**.

3. **Output Files**:
   - `outlet_stock_next.csv`: Stock for each outlet for the next week.
   - `replenishment_next.csv`: Replenishment orders for each outlet for the next week.

4. **Initial Files**:
   - Use `outlet_stock.csv` and `replenishment.csv` for the first week.

5. **Input Files**:
   - Demand forecast over the next two weeks.
   - Stock at each outlet at the end of the last week.
   - Replenishments ordered from the warehouse last week.

6. **Program Execution**:
   - Enter the location of the three input files in the appropriate positions in the code.
   - The program will print the re-balance to be carried out over the current week (WEEK 0) and replenishments to be ordered from the warehouse for the next week (WEEK 1).

### Requirements
- Python 3.x
- pandas
- numpy
- Any additional libraries used in the project

### Installation
To install the required libraries, use the following command:
```bash
pip install -r requirements.txt
