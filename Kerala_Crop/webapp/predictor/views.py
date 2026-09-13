import os
import joblib
import pandas as pd

from django.conf import settings
from django.shortcuts import render


# ============================================================
# MODEL PATHS
# ============================================================

MODEL_DIR = os.path.join(
    settings.BASE_DIR.parent,
    "models"
)

YIELD_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "random_forest_crop_yield.pkl"
)

CROP_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "crop_recommendation_model.pkl"
)


# ============================================================
# LOAD YIELD MODEL
# ============================================================

try:

    yield_model = joblib.load(
        YIELD_MODEL_PATH
    )

    print("Yield model loaded successfully.")

except Exception as e:

    yield_model = None

    print(
        "Yield model loading error:",
        e
    )


# ============================================================
# LOAD CROP RECOMMENDATION MODEL
# ============================================================

try:

    crop_package = joblib.load(
        CROP_MODEL_PATH
    )

    crop_model = crop_package["model"]

    crop_feature_encoders = (
        crop_package["feature_encoders"]
    )

    crop_target_encoder = (
        crop_package["target_encoder"]
    )

    crop_features = (
        crop_package["features"]
    )

    print(
        "Crop recommendation model loaded successfully."
    )

except Exception as e:

    crop_model = None

    crop_feature_encoders = {}

    crop_target_encoder = None

    crop_features = []

    print(
        "Crop recommendation model loading error:",
        e
    )



def index(request):

    return render(
        request,
        "index.html"
    )



# ============================================================
# YIELD PREDICTION VIEW
# ============================================================

def yield_prediction(request):

    predicted_yield = None

    predicted_tonnes = None

    top_recommendations = []

    crop_suitable = None

    error = None


    # ========================================================
    # DEFAULT FORM VALUES
    # ========================================================

    crop = ""

    area_value = ""

    area_unit = "hectare"

    soil_type = ""

    soil_ph = ""

    nitrogen = ""

    phosphorus = ""

    potassium = ""

    rainfall = ""

    temperature = ""

    humidity = ""

    irrigation = ""

    season = ""


    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        try:

            # =================================================
            # GET VALUES FROM HTML
            # =================================================

            crop = request.POST.get(
                "crop",
                ""
            ).strip()

            area_value = request.POST.get(
                "area",
                ""
            ).strip()

            area_unit = request.POST.get(
                "area_unit",
                "hectare"
            ).strip()

            soil_type = request.POST.get(
                "soil_type",
                ""
            ).strip()

            soil_ph = request.POST.get(
                "soil_ph",
                ""
            ).strip()

            nitrogen = request.POST.get(
                "nitrogen",
                ""
            ).strip()

            phosphorus = request.POST.get(
                "phosphorus",
                ""
            ).strip()

            potassium = request.POST.get(
                "potassium",
                ""
            ).strip()

            rainfall = request.POST.get(
                "rainfall",
                ""
            ).strip()

            temperature = request.POST.get(
                "temperature",
                ""
            ).strip()

            humidity = request.POST.get(
                "humidity",
                ""
            ).strip()

            irrigation = request.POST.get(
                "irrigation",
                ""
            ).strip()

            season = request.POST.get(
                "season",
                ""
            ).strip()


            # =================================================
            # VALIDATION
            # =================================================

            if not crop:
                raise ValueError(
                    "Please select a crop."
                )

            if not area_value:
                raise ValueError(
                    "Please enter cultivated area."
                )

            if not soil_type:
                raise ValueError(
                    "Please select soil type."
                )

            if not soil_ph:
                raise ValueError(
                    "Please enter soil pH."
                )

            if not nitrogen:
                raise ValueError(
                    "Please enter nitrogen value."
                )

            if not phosphorus:
                raise ValueError(
                    "Please enter phosphorus value."
                )

            if not potassium:
                raise ValueError(
                    "Please enter potassium value."
                )

            if not rainfall:
                raise ValueError(
                    "Please enter rainfall."
                )

            if not temperature:
                raise ValueError(
                    "Please enter temperature."
                )

            if not humidity:
                raise ValueError(
                    "Please enter humidity."
                )

            if not irrigation:
                raise ValueError(
                    "Please select irrigation level."
                )

            if not season:
                raise ValueError(
                    "Please select season."
                )


            # =================================================
            # CONVERT NUMERIC VALUES
            # =================================================

            area = float(area_value)

            soil_ph_value = float(soil_ph)

            nitrogen_value = float(nitrogen)

            phosphorus_value = float(phosphorus)

            potassium_value = float(potassium)

            rainfall_value = float(rainfall)

            temperature_value = float(temperature)

            humidity_value = float(humidity)


            # =================================================
            # AREA
            # =================================================

            if area <= 0:

                raise ValueError(
                    "Cultivated area must be greater than 0."
                )


            if area_unit == "hectare":

                area_hectare = area

                area_cent = (
                    area_hectare * 247.105
                )


            elif area_unit == "acre":

                area_hectare = (
                    area * 0.404686
                )

                area_cent = (
                    area_hectare * 247.105
                )


            elif area_unit == "cent":

                area_cent = area

                area_hectare = (
                    area / 247.105
                )


            else:

                raise ValueError(
                    "Invalid area unit."
                )


            # =================================================
            # YIELD MODEL
            # =================================================

            if yield_model is None:

                raise ValueError(
                    "Yield model is not available."
                )


            yield_input = pd.DataFrame([{

                "Crop":
                    crop,

                "Area":
                    area_hectare,

                "Area_Cent":
                    area_cent,

                "Soil_Type":
                    soil_type,

                "Soil_pH":
                    soil_ph_value,

                "Nitrogen_N_kg_ha":
                    nitrogen_value,

                "Phosphorus_P_kg_ha":
                    phosphorus_value,

                "Potassium_K_kg_ha":
                    potassium_value,

                "Rainfall_mm":
                    rainfall_value,

                "Temperature_C":
                    temperature_value,

                "Humidity_percent":
                    humidity_value,

                "Irrigation_Level":
                    irrigation,

                "Season":
                    season,

            }])


            # =================================================
            # PREDICT SELECTED CROP
            # =================================================

            yield_per_hectare = float(
                yield_model.predict(
                    yield_input
                )[0]
            )


            yield_per_hectare = max(
                yield_per_hectare,
                0
            )


            # =================================================
            # TOTAL PRODUCTION
            # =================================================

            total_production = (
                yield_per_hectare
                * area_hectare
            )


            predicted_yield = round(
                total_production,
                2
            )

            predicted_tonnes = round(
                total_production / 1000,
                2
            )


            # =================================================
            # CROP RECOMMENDATION
            # =================================================

            if crop_model is not None:

                recommendation_input = pd.DataFrame([{

                    "Soil_Type":
                        soil_type,

                    "Soil_pH":
                        soil_ph_value,

                    "Nitrogen_N_kg_ha":
                        nitrogen_value,

                    "Phosphorus_P_kg_ha":
                        phosphorus_value,

                    "Potassium_K_kg_ha":
                        potassium_value,

                    "Rainfall_mm":
                        rainfall_value,

                    "Temperature_C":
                        temperature_value,

                    "Humidity_percent":
                        humidity_value,

                    "Irrigation_Level":
                        irrigation,

                    "Season":
                        season,

                }])


                # =================================================
                # ENCODE CATEGORICAL VALUES
                # =================================================

                for column, encoder in (
                    crop_feature_encoders.items()
                ):

                    if column in recommendation_input.columns:

                        recommendation_input[column] = (
                            encoder.transform(
                                recommendation_input[column]
                            )
                        )


                # =================================================
                # FEATURE ORDER
                # =================================================

                recommendation_input = (
                    recommendation_input[
                        crop_features
                    ]
                )


                # =================================================
                # GET PROBABILITIES
                # =================================================

                probabilities = (
                    crop_model.predict_proba(
                        recommendation_input
                    )[0]
                )


                # =================================================
                # TOP 3 CROPS
                # =================================================

                top_indices = (
                    probabilities
                    .argsort()[::-1][:3]
                )


                top_class_codes = (
                    crop_model.classes_[
                        top_indices
                    ]
                )


                top_crops = (
                    crop_target_encoder.inverse_transform(
                        top_class_codes
                    )
                )


                # =================================================
                # PRODUCTION FOR EACH RECOMMENDED CROP
                # =================================================

                for rank, recommended_crop in enumerate(
                    top_crops,
                    start=1
                ):

                    recommended_input = pd.DataFrame([{

                        "Crop":
                            recommended_crop,

                        "Area":
                            area_hectare,

                        "Area_Cent":
                            area_cent,

                        "Soil_Type":
                            soil_type,

                        "Soil_pH":
                            soil_ph_value,

                        "Nitrogen_N_kg_ha":
                            nitrogen_value,

                        "Phosphorus_P_kg_ha":
                            phosphorus_value,

                        "Potassium_K_kg_ha":
                            potassium_value,

                        "Rainfall_mm":
                            rainfall_value,

                        "Temperature_C":
                            temperature_value,

                        "Humidity_percent":
                            humidity_value,

                        # USER'S SELECTION
                        "Irrigation_Level":
                            irrigation,

                        # USER'S SELECTION
                        "Season":
                            season,

                    }])


                    recommended_yield = float(
                        yield_model.predict(
                            recommended_input
                        )[0]
                    )


                    recommended_yield = max(
                        recommended_yield,
                        0
                    )


                    recommended_production = (
                        recommended_yield
                        * area_hectare
                    )


                    top_recommendations.append({

                        "rank":
                            rank,

                        "crop":
                            recommended_crop,

                        "production":
                            round(
                                recommended_production,
                                2
                            ),

                        "tonnes":
                            round(
                                recommended_production / 1000,
                                2
                            ),

                    })


                # =================================================
                # SUITABILITY
                # =================================================

                if top_recommendations:

                    best_crop = (
                        top_recommendations[0]["crop"]
                    )

                    crop_suitable = (
                        crop.lower()
                        ==
                        best_crop.lower()
                    )


        except ValueError as e:

            error = str(e)

            predicted_yield = None

            predicted_tonnes = None

            top_recommendations = []

            crop_suitable = None


        except Exception as e:

            error = (
                "Prediction error: "
                + str(e)
            )

            predicted_yield = None

            predicted_tonnes = None

            top_recommendations = []

            crop_suitable = None


    # ============================================================
    # CONTEXT
    # ============================================================

    context = {

        "predicted_yield":
            predicted_yield,

        "predicted_tonnes":
            predicted_tonnes,

        "top_recommendations":
            top_recommendations,

        "crop_suitable":
            crop_suitable,

        "area_value":
            area_value,

        "area_unit":
            area_unit,

        "crop":
            crop,

        "soil_type":
            soil_type,

        "soil_ph":
            soil_ph,

        "nitrogen":
            nitrogen,

        "phosphorus":
            phosphorus,

        "potassium":
            potassium,

        "rainfall":
            rainfall,

        "temperature":
            temperature,

        "humidity":
            humidity,

        "irrigation":
            irrigation,

        "season":
            season,

        "error":
            error,
    }


    return render(
        request,
        "yield_prediction.html",
        context
    )