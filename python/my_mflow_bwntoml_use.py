import bentoml
import numpy as np
import pandas as pd

# Alternatively, load the model by specifying the model tag
bearing_model = bentoml.mlflow.load_model("bearing:latest")

print(f"Model loaded from bentoml: {bearing_model}")

data = [
    [111.0, 2.0, 322.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
    [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 10.00],
    [1.10, 1.20, 1.30, 1.40, 1.50, 1.60, 1.70, 1.80, 1.90, 11.00],
    [9.10, 9.20, 9.30, 9.40, 9.50, 9.60, 9.70, 9.80, 9.90, 19.00],
    [2210, 2220, 2230, 2240, 2250, 2260, 2270, 2280, 2290, 12200],
    [111.0, 2.0, 322.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
]
input_data = np.array(
    data
    #         "WEC: Production kWh_24HR" 2.0,
    #         "WEC: Production kWh_72HR": 2.0,
    #         "WEC: Production kWh_08HR": 2.0,
    #         "WEC: Production kWh": 2.0,
    #         "Inverter averages_72HR": 2.0,
    #         "Inverter averages_24HR": 2.0,
    #         "WEC: Operating Hours_24HR": 2.0,
    #         "WEC: Operating Hours_08HR": 2.0,
    #         "WEC: Operating Hours_72HR": 2.0,
    #         "WEC: min. reactive Power_72HR": 2.0,
    # ]
)

arr = np.array(data)  # shape (1,10)

cols = [
    "WEC: Production kWh_24HR",
    "WEC: Production kWh_72HR",
    "WEC: Production kWh_08HR",
    "WEC: Production kWh",
    "Inverter averages_72HR",
    "Inverter averages_24HR",
    "WEC: Operating Hours_24HR",
    "WEC: Operating Hours_08HR",
    "WEC: Operating Hours_72HR",
    "WEC: min. reactive Power_72HR",
]
df = pd.DataFrame(arr, columns=cols).astype(float)  # ensure float dtyp
res = bearing_model.predict(df)
print(res)
