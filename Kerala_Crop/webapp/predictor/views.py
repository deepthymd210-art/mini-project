import os
import joblib
import pandas as pd

from django.shortcuts import render
from django.conf import settings


# ============================================================
# MODEL DIRECTORY
# ============================================================

MODEL_DIR = os.path.join(
    settings.BASE_DIR.parent,
    "models"
)


# ============================================================
# MODEL PATHS
# ============================================================

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

    print(
        "Yield model loaded successfully."
    )

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

    print(
        "Recommendation features:",
        crop_features
    )

    print(
        "Soil types:",
        list(
            crop_feature_encoders[
                "Soil_Type"
            ].classes_
        )
    )

    print(
        "Irrigation levels:",
        list(
            crop_feature_encoders[
                "Irrigation_Level"
            ].classes_
        )
    )

    print(
        "Seasons:",
        list(
            crop_feature_encoders[
                "Season"
            ].classes_
        )
    )

except Exception as e:

    crop_model = None
    crop_feature_encoders = None
    crop_target_encoder = None
    crop_features = None

    print(
        "Crop recommendation model loading error:",
        e
    )


# ============================================================
# HOME
# ============================================================

def home(request):

    return render(
        request,
        "index.html"
    )


# ============================================================
# YIELD PREDICTION + CROP RECOMMENDATION
# ============================================================

def yield_prediction(request):

    predicted_yield = None

    predicted_tonnes = None

    recommended_crop = None

    crop_suitable = None

    error = None

    area_value = None

    area_unit = None


    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        try:

            # ==================================================
            # GET USER INPUT
            # ==================================================

            crop = request.POST.get(
                "crop",
                ""
            ).strip()

            area_text = request.POST.get(
                "area",
                ""
            ).strip()

            area_unit = request.POST.get(
                "area_unit",
                ""
            ).strip()

            soil_type = request.POST.get(
                "soil_type",
                ""
            ).strip()

            soil_ph_text = request.POST.get(
                "soil_ph",
                ""
            ).strip()

            nitrogen_text = request.POST.get(
                "nitrogen",
                ""
            ).strip()

            phosphorus_text = request.POST.get(
                "phosphorus",
                ""
            ).strip()

            potassium_text = request.POST.get(
                "potassium",
                ""
            ).strip()

            rainfall_text = request.POST.get(
                "rainfall",
                ""
            ).strip()

            temperature_text = request.POST.get(
                "temperature",
                ""
            ).strip()

            humidity_text = request.POST.get(
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


            # ==================================================
            # REQUIRED CHECK
            # ==================================================

            if not crop:

                raise ValueError(
                    "Please select a crop."
                )

            if not area_text:

                raise ValueError(
                    "Please enter the area."
                )

            if not area_unit:

                raise ValueError(
                    "Please select area unit."
                )

            if not soil_type:

                raise ValueError(
                    "Please select soil type."
                )

            if not soil_ph_text:

                raise ValueError(
                    "Please enter soil pH."
                )

            if not nitrogen_text:

                raise ValueError(
                    "Please enter nitrogen value."
                )

            if not phosphorus_text:

                raise ValueError(
                    "Please enter phosphorus value."
                )

            if not potassium_text:

                raise ValueError(
                    "Please enter potassium value."
                )

            if not rainfall_text:

                raise ValueError(
                    "Please enter rainfall."
                )

            if not temperature_text:

                raise ValueError(
                    "Please enter temperature."
                )

            if not humidity_text:

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


            # ==================================================
            # NUMERIC CONVERSION
            # ==================================================

            area = float(
                area_text
            )

            soil_ph = float(
                soil_ph_text
            )

            nitrogen = float(
                nitrogen_text
            )

            phosphorus = float(
                phosphorus_text
            )

            potassium = float(
                potassium_text
            )

            rainfall = float(
                rainfall_text
            )

            temperature = float(
                temperature_text
            )

            humidity = float(
                humidity_text
            )


            # ==================================================
            # AREA VALIDATION
            # ==================================================

            if area <= 0:

                raise ValueError(
                    "Area must be greater than 0."
                )

            area_value = area


            # ==================================================
            # DATASET VALUES
            # ==================================================

            valid_soils = [
                "Loamy",
                "Clay",
                "Sandy",
                "Silty"
            ]

            valid_irrigation = [
                "Low",
                "Medium",
                "High"
            ]

            valid_seasons = [
                "Kharif",
                "Perennial"
            ]


            if soil_type not in valid_soils:

                raise ValueError(
                    f"Invalid Soil Type: '{soil_type}'. "
                    f"Use: {', '.join(valid_soils)}"
                )


            if irrigation not in valid_irrigation:

                raise ValueError(
                    f"Invalid Irrigation Level: '{irrigation}'. "
                    f"Use: {', '.join(valid_irrigation)}"
                )


            if season not in valid_seasons:

                raise ValueError(
                    f"Invalid Season: '{season}'. "
                    f"Use: {', '.join(valid_seasons)}"
                )


            # ==================================================
            # AREA CONVERSION
            # ==================================================

            if area_unit == "hectare":

                area_hectare = area

                area_cent = (
                    area * 247.105
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


            # ==================================================
            # ==================================================
            # YIELD PREDICTION
            # ==================================================
            # ==================================================

            if yield_model is None:

                raise ValueError(
                    "Yield model could not be loaded."
                )


            # ==================================================
            # YIELD INPUT
            # ==================================================

            yield_input = pd.DataFrame({

                "Crop": [
                    crop
                ],

                "Area": [
                    area_hectare
                ],

                "Area_Cent": [
                    area_cent
                ],

                "Soil_Type": [
                    soil_type
                ],

                "Soil_pH": [
                    soil_ph
                ],

                "Nitrogen_N_kg_ha": [
                    nitrogen
                ],

                "Phosphorus_P_kg_ha": [
                    phosphorus
                ],

                "Potassium_K_kg_ha": [
                    potassium
                ],

                "Rainfall_mm": [
                    rainfall
                ],

                "Temperature_C": [
                    temperature
                ],

                "Humidity_percent": [
                    humidity
                ],

                "Irrigation_Level": [
                    irrigation
                ],

                "Season": [
                    season
                ]

            })


            # ==================================================
            # YIELD PREDICTION
            # ==================================================

            yield_per_hectare = float(

                yield_model.predict(
                    yield_input
                )[0]

            )


            # ==================================================
            # TOTAL YIELD
            # ==================================================

            predicted_yield_total = (

                yield_per_hectare
                *
                area_hectare

            )


            predicted_yield = round(
                predicted_yield_total,
                2
            
            )
            predicted_tonnes = round(
                predicted_yield / 1000,
                2
            )
            

            # ==================================================
            # ==================================================
            # CROP RECOMMENDATION
            # ==================================================
            # ==================================================

            if crop_model is None:

                raise ValueError(
                    "Crop recommendation model could not be loaded."
                )


            # ==================================================
            # RECOMMENDATION INPUT
            #
            # IMPORTANT:
            # DO NOT INCLUDE Crop
            # DO NOT INCLUDE Area
            # DO NOT INCLUDE Area_Cent
            # ==================================================

            crop_input = pd.DataFrame({

                "Soil_Type": [
                    soil_type
                ],

                "Soil_pH": [
                    soil_ph
                ],

                "Nitrogen_N_kg_ha": [
                    nitrogen
                ],

                "Phosphorus_P_kg_ha": [
                    phosphorus
                ],

                "Potassium_K_kg_ha": [
                    potassium
                ],

                "Rainfall_mm": [
                    rainfall
                ],

                "Temperature_C": [
                    temperature
                ],

                "Humidity_percent": [
                    humidity
                ],

                "Irrigation_Level": [
                    irrigation
                ],

                "Season": [
                    season
                ]

            })


            # ==================================================
            # APPLY SAVED ENCODERS
            # ==================================================

            for col in [

                "Soil_Type",
                "Irrigation_Level",
                "Season"

            ]:

                encoder = (
                    crop_feature_encoders[col]
                )

                value = str(
                    crop_input[col].iloc[0]
                )


                if value not in encoder.classes_:

                    raise ValueError(

                        f"Invalid {col}: '{value}'. "
                        f"Available values: "
                        f"{list(encoder.classes_)}"

                    )


                crop_input[col] = (

                    encoder.transform(
                        crop_input[col].astype(str)
                    )

                )


            # ==================================================
            # EXACT TRAINING FEATURES
            # ==================================================

            prediction_input = (
                crop_input[crop_features]
            )


            # ==================================================
            # PREDICT RECOMMENDED CROP
            # ==================================================

            recommendation_result = (

                crop_model.predict(
                    prediction_input
                )

            )


            # ==================================================
            # CONVERT LABEL TO CROP NAME
            # ==================================================

            recommended_crop = str(

                crop_target_encoder.inverse_transform(
                    recommendation_result
                )[0]

            )


            # ==================================================
            # CHECK SUITABILITY
            # ==================================================

            crop_suitable = (

                crop.lower().strip()
                ==
                recommended_crop.lower().strip()

            )


            # ==================================================
            # DEBUG INFORMATION
            # ==================================================

            print("\n")
            print("=" * 60)
            print("CROP RECOMMENDATION")
            print("=" * 60)

            print(
                "Selected crop      :",
                crop
            )

            print(
                "Soil type           :",
                soil_type
            )

            print(
                "Soil pH             :",
                soil_ph
            )

            print(
                "Nitrogen            :",
                nitrogen
            )

            print(
                "Phosphorus          :",
                phosphorus
            )

            print(
                "Potassium           :",
                potassium
            )

            print(
                "Rainfall            :",
                rainfall
            )

            print(
                "Temperature         :",
                temperature
            )

            print(
                "Humidity            :",
                humidity
            )

            print(
                "Irrigation          :",
                irrigation
            )

            print(
                "Season              :",
                season
            )

            print(
                "Recommended crop    :",
                recommended_crop
            )

            print(
                "Crop suitable       :",
                crop_suitable
            )

            print("=" * 60)


        except Exception as e:

            error = str(e)

            print(
                "Prediction error:",
                error
            )


    # ============================================================
    # RETURN PAGE
    # ============================================================

    return render(

        request,

        "yield_prediction.html",

        {

            "predicted_yield":
                predicted_yield,

            "predicted_tonnes":
                predicted_tonnes,

            "recommended_crop":
                recommended_crop,

            "crop_suitable":
                crop_suitable,

            "error":
                error,

            "area_value":
                area_value,

            "area_unit":
                area_unit

        }

    )