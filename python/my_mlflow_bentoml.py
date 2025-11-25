from datetime import date

import bentoml
import mlflow
from sklearn.metrics import *
from sklearn.model_selection import *

mlflow.set_tracking_uri("http://localhost:5000")


mlflow_client = mlflow.tracking.MlflowClient()

metric = "f1"
experiment_name = "AF_48"
experiment_name = "AF_24"
current_experiment = dict(mlflow.get_experiment_by_name(experiment_name))
experiment_id = current_experiment["experiment_id"]

runs = mlflow_client.search_runs(
    [experiment_id],
    # filter_string=filter_string,
    # run_view_type=ViewType.ACTIVE_ONLY,
    order_by=[f"metrics.{metric} DESC"],
)


best_run = runs[0]


model_uri = f"runs:/{best_run.info.run_id}/model"
print(f"Loading model from: {model_uri}")
model = mlflow.sklearn.load_model(model_uri)
print(
    f"Best model loaded : {model} from run id {best_run.info.run_id} {best_run.info.run_name}"
)


bento_model = bentoml.mlflow.import_model(
    name="bearing",
    model_uri=model_uri,
    labels={
        "team": "bento",
        "stage": "dev",
        "f1": best_run.data.metrics.get("f1", 0),
        "training_date": str(date.today()),
    },
)
print(f"Model imported to bentoml: {bento_model}")
