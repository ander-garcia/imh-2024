from pathlib import Path

import bentoml

with bentoml.SyncHTTPClient("http://localhost:3000") as client:
    # result = client.render(
    #     image=[Path("./descarga.jpg")],
    # )
    # print(result)

    result = client.predict(
        images=[Path("./descarga.jpg")],
    )
    print(result)
