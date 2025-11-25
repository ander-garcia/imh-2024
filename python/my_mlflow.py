import random
from datetime import date
from random import shuffle

import mlflow
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier as GBC
from sklearn.ensemble import RandomForestClassifier as RFC
from sklearn.linear_model import LogisticRegression as LOG
from sklearn.metrics import *
from sklearn.metrics import f1_score
from sklearn.model_selection import *
from sklearn.neural_network import MLPClassifier as MLC

F1_results = []  # Inicializar la lista de resultados de la puntuación F1
negativelogloss_results = []  # Inicializar la lista de resultados de la pérdida logarítmica negativa

# Garantizar la repetibilidad en nuestros métodos no deterministas
random.seed(0)


def CalcF1Score(y_true, y_pred):
    f1 = f1_score(y_true, y_pred, labels=[0, 1], average="macro")
    return f1


def CalcNegativeLogLoss(y_true_bool, y_pred_prob):
    ytrue, ypred, Labels = y_true_bool, y_pred_prob, [0, 1]
    return -log_loss(ytrue, ypred, labels=Labels)


# Create labels for the model types:
ModelNames = ["LOG", "RFC", "GBC", "MLC"]


# Generates a new model instance given a model label:
def GenerateModel(MName):
    if MName == "LOG":
        # Logistic Regression
        return LOG()
    if MName == "RFC":
        # Random Forest Classifier
        return RFC()
    if MName == "GBC":
        # Gradient Boosting Classifier
        return GBC()
    if MName == "MLC":
        # Multilayer Perceptron Classifier
        Layers = [50, 50]
        return MLC(Layers)


features_dataset = "./data/features_scaled.csv"
dataframe_features = pd.read_csv(features_dataset)
dataframe_features["DateTime"] = pd.to_datetime(dataframe_features["DateTime"])

# add const variable to be leveraged in regression modeling
dataframe_features["const"] = [1] * len(dataframe_features)

outcomes_dataset = "./data/outcomes_bool.csv"

dataframe_outcomes = pd.read_csv(outcomes_dataset)
dataframe_outcomes["DateTime"] = pd.to_datetime(dataframe_outcomes["DateTime"])
YVarsList = list(dataframe_outcomes.columns)[1:]  # YVars = variable de salida
YVars24 = [a for a in YVarsList if "_24" in a]
YVars48 = [a for a in YVarsList if "_48" in a]
YVars72 = [a for a in YVarsList if "_72" in a]

# Initializamos la variable de salida para la ventana de 72-hr
YVars = YVars24 + YVars48 + YVars72
fallos = {}
no_fallos = {}
for YVar in YVars:  # ["AF_72", "EF_72", "FF_72", "GF_72", "MF_72"]:
    total = len(dataframe_outcomes)
    fallos[YVar] = dataframe_outcomes[YVar].sum()
    no_fallos[YVar] = total - fallos[YVar]
    print(f"Total de fallos para {YVar}: {fallos[YVar]}")
    print(f"Total de no fallos para {YVar}: {no_fallos[YVar]}\n")


top_features_linear = "./data/top_features_linear.csv"
feats_linear = pd.read_csv(top_features_linear)
top_features_nonlinear = "./data/top_features_nonlinear.csv"
feats_nonlinear = pd.read_csv(top_features_nonlinear)

Short = 10  # Número de variables principales a incluir en una lista CORTA.
Long = 20  # Número de variables principales a incluir en una lista LARGA.

# Crear conjuntos de características lineales
Linear_Short = list(feats_linear["Feature"])[
    :Short
]  # Lista corta de características lineales
Linear_Long = list(feats_linear["Feature"])[
    :Long
]  # Lista larga de características lineales

# Crear conjuntos de características no lineales
NonLinear_Short = list(feats_nonlinear["Feature"])[
    :Short
]  # Lista corta de características no lineales
NonLinear_Long = list(feats_nonlinear["Feature"])[
    :Long
]  # Lista larga de características no lineales

# Crear conjuntos híbridos de características lineales y no lineales, eliminando las repetidas
Hybrid_Short = list(
    set(Linear_Short + NonLinear_Short)
)  # Lista corta de características híbridas
Hybrid_Long = list(
    set(Linear_Long + NonLinear_Long)
)  # Lista larga de características híbridas
FeatureSetNames = [
    "LNS",
    "LNL",
    "NLS",
    "NLL",
    "HBS",
    "HBL",
]  # Create labels for each feature set:
GetFeatureSet = {
    "LNS": Linear_Short,
    "LNL": Linear_Long,
    "NLS": NonLinear_Short,
    "NLL": NonLinear_Long,
    "HBS": Hybrid_Short,
    "HBL": Hybrid_Long,
}

# Define sample size of training set
training_sample_size = 1000
total_length = len(dataframe_features)
index_list = list(range(total_length))

for i in range(10):
    shuffle(index_list)

# Produce list of indices of our training and test datasets
training_index = index_list[:training_sample_size]
test_index = index_list[training_sample_size:]

print("Total length of dataset:", total_length)
print("Total length of training sample:", len(training_index))
print("Total length of test sample:", len(test_index))

dataframe_xtrain = dataframe_features.loc[
    training_index
]  # Features training data-frame
dataframe_xtest = dataframe_features.loc[test_index]  # Features test data-frame
dataframe_ytrain = dataframe_outcomes.loc[
    training_index
]  # Outcomes training data-frame
dataframe_ytest = dataframe_outcomes.loc[test_index]  # Outcomes test data-frame

mlflow.set_tracking_uri("http://localhost:5000")


for YVar in YVars:
    # Create a new experiment

    mlflow.set_experiment(f"{YVar}-{date.today().isoformat()}")
    print("Creando modelo para", YVar + "...")
    y_train = dataframe_ytrain[YVar]
    y_test = dataframe_ytest[YVar]
    with mlflow.start_run(run_name=f"{YVar}-{date.today().isoformat()}", nested=True):
        # Ciclar a través de los modelos que fueron predefinidos en un paso anterior
        for model_name in ModelNames:
            for feature in [FeatureSetNames[0]]:
                with mlflow.start_run(
                    run_name=f"{model_name}-{YVar}-{feature}-{date.today().isoformat()}",
                    nested=True,
                ):
                    mlflow.sklearn.autolog(log_models=True)
                    mlflow.set_tags(
                        {
                            "dataset_version": "v1.0.1",
                            "environment": "dev",
                            "team": "deusto_ml",
                            "experiment_phase": "lab5",
                        }
                    )
                    mlflow.set_tag("user", "agarcia")
                    # Special notes tag for documentation
                    mlflow.set_tag(
                        "mlflow.note.content",
                        "Práctica de laboratorio 5:"
                        "Feature extraction and model training",
                    )

                    mlflow.log_param("feature", feature)

                    # Entrenar el modelo
                    features = GetFeatureSet[feature]
                    X_train = dataframe_xtrain[features]
                    model = GenerateModel(model_name)
                    model.fit(X_train, y_train)

                    # Probar el modelo
                    X_test = dataframe_xtest[features]

                    # Predecir clases y calcular la puntuación F1:
                    y_preds = model.predict(X_test)
                    F1_score = CalcF1Score(y_test, y_preds)
                    result = [
                        round(F1_score, 8),
                        YVar,
                        model_name,
                        feature,
                        y_test.tolist(),
                        y_preds.tolist(),
                    ]
                    F1_results.append(result)

                    # Predecir probabilidades y calcular la puntuación de la pérdida logarítmica negativa:
                    probability_predictions = model.predict_proba(X_test)[:, 1]
                    negativelogloss_score = CalcNegativeLogLoss(
                        y_test, probability_predictions
                    )
                    result = [
                        round(negativelogloss_score, 8),
                        YVar,
                        model_name,
                        feature,
                    ]
                    negativelogloss_results.append(result)
                    # assuming the scores have been calculated and stored in the respective variables
                    # mlflow.log_artifact(model)
                    mlflow.sklearn.log_model(
                        model,
                        name=f"model_{model_name}-{YVar}",
                        tags={"date": date.today().isoformat()},
                        registered_model_name=f"model_{model_name}-{YVar}",
                    )

                    mlflow.log_metric("f1", F1_score)
                    mlflow.log_metric("negativelogloss_score", negativelogloss_score)


print("¡Experimentos completados!")
