# Auto-MPG  Analysis

## Dataset Description: 
The MPG dataset is technical spec of cars originaly provided from [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/auto+mpg) and can be found on Kaggle [here](https://www.kaggle.com/uciml/autompg-dataset). 
The data concerns city-cycle fuel consumption in miles per gallon to be analyzed in terms of 3 multivalued discrete and 5 continuous attributes.

## Data Visualization
Using `Matplotlib` and `Seaborn`, several meaningful visuals and charts were made to help gain informative insights.

## Findings from Auto MPG Data
These are derived conclusions after the data visualisation phase.

### 1. MPG Distribution
- Most cars have an MPG between **15 and 35**, with a peak around **25 MPG**, suggesting a right-skewed distribution.
- There are few cars with extremely low or high fuel efficiency.

### 2. Weight vs MPG
- There is a **strong negative correlation** between weight and MPG.
- Heavier cars tend to have **lower fuel efficiency**, especially those from **origin 1 (USA)**.

### 3. Cylinders and Fuel Efficiency
- Cars with **fewer cylinders (e.g., 4)** have **higher average MPG**.
- Vehicles with **6 or 8 cylinders** show significantly **lower fuel efficiency**.

### 4. Model Year Trends
- There is a clear **upward trend in average MPG over the years**, especially from 1970 to 1982.
- This reflects **improvements in automotive technology** and possibly **regulatory pressure** during the oil crisis years.

### 5. Correlation Matrix
- **Horsepower, weight, and displacement** are all negatively correlated with MPG.
- The strongest negative correlation is with **weight (-0.83)**, followed by **horsepower (-0.78)**.
- This implies that **lighter and less powerful cars are more fuel-efficient**.

### 6. Horsepower vs MPG (Regression Plot)
- Shows a **clear downward linear trend**: higher horsepower generally means **lower MPG**.
- This reinforces the idea that performance often comes at the cost of efficiency.

### 7. MPG by Origin
- Cars from **origin 3 (Asia)** generally have **higher MPG**, followed by **origin 2 (Europe)**.
- **American cars (origin 1)** are on average **less fuel-efficient**, likely due to larger engines and heavier builds.