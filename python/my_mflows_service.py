import os

import bentoml
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

# Minimal image spec including scikit-learn
demo_image = bentoml.images.Image(python_version="3.12").python_packages("scikit-learn")


class ErrorPrediction(BaseModel):
    error: str = Field(description="The predicted  error in the input data")
    confidence: float = Field(
        description="The confidence of the prediction, a value between 0 and 1"
    )


@bentoml.service(
    image=demo_image,
    resources={"cpu": "2"},
    traffic={"timeout": 10},
)
class AggRFClassifier:
    # Retrieve the latest version of the sklearn model from the BentoML model store
    bento_model = bentoml.models.BentoModel("bearing:latest")

    def __init__(self):
        # Load the scikit-learn model saved as a Bento model
        self.model = bentoml.mlflow.load_model(self.bento_model)

        # Try to configure CPU parallelism if the estimator supports `n_jobs`.
        # scikit-learn estimators typically don't use GPU, so we only tune CPU threads.
        if hasattr(self.model, "n_jobs"):
            nthreads = os.getenv("OMP_NUM_THREADS")
            if nthreads:
                try:
                    nthreads = max(int(nthreads), 1)
                except Exception:
                    nthreads = 1
            else:
                nthreads = 1
            try:
                self.model.n_jobs = nthreads
            except Exception:
                # Some estimators may not allow setting n_jobs after creation; ignore safely.
                pass

    @bentoml.api
    def predict(self, data: list) -> dict:
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
        df = pd.DataFrame(arr, columns=cols).astype(float)  # ensure float dtype

        prediction = self.model.predict(df)

        return {"prediction": prediction.tolist()}
