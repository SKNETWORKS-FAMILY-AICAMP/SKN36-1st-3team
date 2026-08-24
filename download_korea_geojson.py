from pathlib import Path

import requests


ROOT_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = (
    ROOT_DIR
    / "data"
    / "geo"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "korea_sido.geojson"
)


# 대한민국 시도 단위 단순화 GeoJSON
URL = (
    "https://raw.githubusercontent.com/"
    "southkorea/southkorea-maps/master/"
    "kostat/2013/json/skorea_provinces_geo_simple.json"
)


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("대한민국 시도 GeoJSON 다운로드 중...")


    response = requests.get(
        URL,
        timeout=30
    )

    response.raise_for_status()


    OUTPUT_FILE.write_bytes(
        response.content
    )


    print(
        "저장 완료:",
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()


    import json

with open(
    "data/geo/korea_sido.geojson",
    "r",
    encoding="utf-8"
) as f:

    geo = json.load(f)


print(
    "feature 개수:",
    len(geo["features"])
)


for feature in geo["features"]:

    print(
        feature["properties"]
    )