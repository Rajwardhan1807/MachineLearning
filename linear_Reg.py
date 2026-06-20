import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


df = pd.read_csv('price.csv')# Load dataset in csv format


X = df[['Area_sqft']]#  (X) and (y)
y = df['Price_Lakh']


reg = LinearRegression()# Create and train model
reg.fit(X, y)


plt.scatter(X, y, color='red', marker='*')# Scatter plot


plt.plot(X, reg.predict(X), color='black')# Regression line

plt.xlabel('Area (sq.ft)')
plt.ylabel('Price (INR)')
plt.title('Linear Regression: Area vs Price')
plt.show()


print("Slope:", reg.coef_[0])
print("Intercept:", reg.intercept_)

# Predict price for a new house
area = 1500
predicted_price = reg.predict([[area]])

print(f"Predicted price for {area} sq.ft = ₹{predicted_price[0]:,.0f}")