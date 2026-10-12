# ============================================================
# IMPORTS
# ============================================================

import os
import joblib
import pandas as pd
import requests

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render


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

PRODUCTION_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "random_forest_production_yield.pkl"
)


# ============================================================
# CROP LIST
# ============================================================

CROP_LIST = [
    "Arecanut",
    "Banana",
    "Betel leaves",
    "Cardamom",
    "Cashew",
    "Cloves",
    "Cocoa",
    "Coconut",
    "Coffee",
    "Ginger",
    "Jack",
    "Mango",
    "Nutmeg",
    "Paddy",
    "Pappaya",
    "Pepper",
    "Pineapple",
    "Plantain",
    "Rubber",
    "Tapioca",
    "Tea",
    "Turmeric"
]


# ============================================================
# LOAD MODEL
# ============================================================

def load_model(model_path, model_name):

    try:

        model = joblib.load(model_path)

        # Handle an old dictionary-style saved model
        if isinstance(model, dict):

            if "model" in model:

                model = model["model"]

            else:

                raise ValueError(
                    f"{model_name} is a dictionary but "
                    f"does not contain a usable 'model'."
                )

        print()
        print("=" * 70)
        print(f"✅ {model_name} loaded successfully")
        print("Path:", model_path)

        if hasattr(model, "feature_names_in_"):

            print(
                "Features:",
                list(model.feature_names_in_)
            )

        print("=" * 70)

        return model

    except Exception as e:

        print()
        print("=" * 70)
        print(f"❌ ERROR loading {model_name}")
        print("Path:", model_path)
        print("Error:", e)
        print("=" * 70)

        return None


# ============================================================
# LOAD MAIN YIELD MODEL
# ============================================================

yield_model = load_model(
    YIELD_MODEL_PATH,
    "Random Forest Crop Yield Model"
)


# ============================================================
# LOAD TOOL 1 MODEL
# ============================================================

production_yield_model = load_model(
    PRODUCTION_MODEL_PATH,
    "Random Forest Production Model"
)


# ============================================================
# EXPECTED MAIN MODEL FEATURES
# ============================================================

EXPECTED_YIELD_FEATURES = [

    "Crop",

    "Area",

    "Area_Cent",

    "Soil_Type",

    "Soil_pH",

    "Nitrogen_N_kg_ha",

    "Phosphorus_P_kg_ha",

    "Potassium_K_kg_ha",

    "Rainfall_mm",

    "Temperature_C",

    "Humidity_percent",

    "Irrigation_Level",

    "Season"
]


# ============================================================
# PREDICTION HELPER
# ============================================================

def predict_crop_yield(model, data):

    if model is None:

        raise ValueError(
            "Random Forest yield model could not be loaded."
        )

    df = data.copy()

    # --------------------------------------------------------
    # If sklearn saved feature names are available,
    # use EXACTLY those columns and order.
    # --------------------------------------------------------

    if hasattr(model, "feature_names_in_"):

        model_features = list(
            model.feature_names_in_
        )

        missing = [

            feature

            for feature in model_features

            if feature not in df.columns
        ]

        if missing:

            raise ValueError(
                "The saved Random Forest model requires "
                f"missing features: {missing}"
            )

        df = df[model_features]

    else:

        missing = [

            feature

            for feature in EXPECTED_YIELD_FEATURES

            if feature not in df.columns
        ]

        if missing:

            raise ValueError(
                "Missing model features: "
                f"{missing}"
            )

        df = df[EXPECTED_YIELD_FEATURES]

    # --------------------------------------------------------
    # PREDICT
    # --------------------------------------------------------

    prediction = model.predict(df)

    prediction = float(prediction[0])

    if prediction < 0:

        prediction = 0.0

    return prediction


# ============================================================
# HOME
# ============================================================

def index(request):

    return render(
        request,
        "index.html",
        {
            "crop_list": CROP_LIST
        }
    )


# ============================================================
# CROP YIELD PREDICTION
# ============================================================

def yield_prediction(request):

    # --------------------------------------------------------
    # DEFAULT OUTPUT
    # --------------------------------------------------------

    predicted_yield = None

    predicted_total_production = None

    predicted_tonnes = None

    top_recommendations = []

    crop_suitable = None

    error = None

    prediction_done = False


    # --------------------------------------------------------
    # DEFAULT INPUT VALUES
    # --------------------------------------------------------

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

        # ----------------------------------------------------
        # FORM VALUES
        # ----------------------------------------------------

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
        ).strip().lower()

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


        # ====================================================
        # VALIDATION
        # ====================================================

        if not crop:

            error = "Please select a crop."

        elif crop not in CROP_LIST:

            error = "Please select a valid crop."

        elif not area_value:

            error = "Please enter cultivated area."

        elif not soil_type:

            error = "Please select soil type."

        elif not soil_ph:

            error = "Please enter soil pH."

        elif not nitrogen:

            error = "Please enter nitrogen value."

        elif not phosphorus:

            error = "Please enter phosphorus value."

        elif not potassium:

            error = "Please enter potassium value."

        elif not rainfall:

            error = "Please enter rainfall."

        elif not temperature:

            error = "Please enter temperature."

        elif not humidity:

            error = "Please enter humidity."

        elif not irrigation:

            error = "Please select irrigation level."

        elif not season:

            error = "Please select season."

        elif yield_model is None:

            error = (
                "Random Forest crop yield model "
                "could not be loaded."
            )

        else:

            try:

                # =================================================
                # NUMERIC VALUES
                # =================================================

                area = float(area_value)

                soil_ph_value = float(soil_ph)

                nitrogen_value = float(nitrogen)

                phosphorus_value = float(phosphorus)

                potassium_value = float(kalium_value) if False else float(potassium)

                rainfall_value = float(rainfall)

                temperature_value = float(temperature)

                humidity_value = float(humidity)


                # =================================================
                # VALIDATION
                # =================================================

                if area <= 0:

                    raise ValueError(
                        "Cultivated area must be greater than 0."
                    )

                if soil_ph_value <= 0 or soil_ph_value > 14:

                    raise ValueError(
                        "Soil pH must be between 0 and 14."
                    )

                if nitrogen_value < 0:

                    raise ValueError(
                        "Nitrogen cannot be negative."
                    )

                if phosphorus_value < 0:

                    raise ValueError(
                        "Phosphorus cannot be negative."
                    )

                if potassium_value < 0:

                    raise ValueError(
                        "Potassium cannot be negative."
                    )

                if rainfall_value < 0:

                    raise ValueError(
                        "Rainfall cannot be negative."
                    )

                if humidity_value < 0 or humidity_value > 100:

                    raise ValueError(
                        "Humidity must be between 0 and 100."
                    )


                # =================================================
                # AREA CONVERSION
                # =================================================

                if area_unit == "cent":

                    area_cent = area

                    area_hectare = (
                        area / 247.105
                    )

                elif area_unit == "acre":

                    area_hectare = (
                        area * 0.404686
                    )

                    area_cent = (
                        area_hectare * 247.105
                    )

                elif area_unit == "hectare":

                    area_hectare = area

                    area_cent = (
                        area * 247.105
                    )

                else:

                    raise ValueError(
                        "Invalid area unit."
                    )


                # =================================================
                # SAME FARMING CONDITIONS FOR ALL CROPS
                # =================================================

                common_data = {

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
                        season
                }


                # =================================================
                # CURRENT SELECTED CROP
                # =================================================

                selected_data = {

                    "Crop":
                        crop,

                    **common_data
                }


                selected_df = pd.DataFrame(
                    [selected_data]
                )


                # =================================================
                # PREDICT SELECTED CROP YIELD
                # =================================================

                predicted_yield = predict_crop_yield(
                    yield_model,
                    selected_df
                )


                # =================================================
                # TOTAL PRODUCTION
                #
                # predicted_yield = kg/hectare
                #
                # area_hectare = hectare
                #
                # total = kg/hectare × hectare
                # =================================================

                predicted_total_production = (

                    predicted_yield
                    *
                    area_hectare

                )


                predicted_total_production = round(
                    predicted_total_production,
                    2
                )


                # =================================================
                # TONNES
                #
                # IMPORTANT:
                # ALWAYS CONVERT TOTAL KG TO TONNES.
                #
                # 1000 kg = 1 tonne
                # =================================================

                predicted_tonnes = round(

                    predicted_total_production
                    /
                    1000,

                    2

                )


                # =================================================
                # DEBUG OUTPUT
                # =================================================

                print()
                print("=" * 70)
                print("SELECTED CROP PREDICTION")
                print("=" * 70)

                print(
                    "Crop:",
                    crop
                )

                print(
                    "Area:",
                    area,
                    area_unit
                )

                print(
                    "Area hectare:",
                    area_hectare
                )

                print(
                    "Predicted yield kg/ha:",
                    predicted_yield
                )

                print(
                    "Total production kg:",
                    predicted_total_production
                )

                print(
                    "Total production tonnes:",
                    predicted_tonnes
                )

                print("=" * 70)


                # =================================================
                # TOP 3 RECOMMENDATIONS
                #
                # VERY IMPORTANT:
                #
                # Every crop is predicted using:
                #
                # 1. SAME area
                # 2. SAME soil
                # 3. SAME pH
                # 4. SAME N
                # 5. SAME P
                # 6. SAME K
                # 7. SAME rainfall
                # 8. SAME temperature
                # 9. SAME humidity
                # 10. SAME irrigation
                # 11. SAME season
                #
                # ONLY "Crop" changes.
                # =================================================

                recommendation_results = []


                for recommendation_crop in CROP_LIST:

                    recommendation_data = {

                        "Crop":
                            recommendation_crop,

                        **common_data
                    }


                    recommendation_df = pd.DataFrame(
                        [recommendation_data]
                    )


                    # ------------------------------------------------
                    # Predict this crop using SAME model
                    # ------------------------------------------------

                    recommendation_yield = predict_crop_yield(

                        yield_model,

                        recommendation_df

                    )


                    # ------------------------------------------------
                    # Total production
                    # ------------------------------------------------

                    recommendation_production = (

                        recommendation_yield
                        *
                        area_hectare

                    )


                    recommendation_production = round(
                        recommendation_production,
                        2
                    )


                    # ------------------------------------------------
                    # Tonnes
                    # ------------------------------------------------

                    recommendation_tonnes = round(

                        recommendation_production
                        /
                        1000,

                        2

                    )


                    recommendation_results.append({

                        "crop":
                            recommendation_crop,

                        "yield":
                            round(
                                recommendation_yield,
                                2
                            ),

                        "production":
                            recommendation_production,

                        "tonnes":
                            recommendation_tonnes

                    })


                # =================================================
                # SORT BY TOTAL PRODUCTION
                #
                # HIGHEST → LOWEST
                # =================================================

                recommendation_results.sort(

                    key=lambda item:
                        item["production"],

                    reverse=True

                )


                # =================================================
                # TOP 3
                # =================================================

                top_recommendations = (

                    recommendation_results[:3]

                )


                # =================================================
                # CHECK WHETHER SELECTED CROP IS TOP 3
                # =================================================

                top_crop_names = [

                    item["crop"]

                    for item in top_recommendations

                ]


                crop_suitable = (

                    crop in top_crop_names

                )


                # =================================================
                # DEBUG TOP 3
                # =================================================

                print()
                print("=" * 70)
                print("TOP 3 CROP PRODUCTION")
                print("=" * 70)

                for item in top_recommendations:

                    print(

                        item["crop"],
                        "->",
                        item["production"],
                        "kg ->",
                        item["tonnes"],
                        "tonnes"

                    )

                print("=" * 70)


                prediction_done = True


            except ValueError as e:

                error = str(e)

            except Exception as e:

                error = (
                    f"Prediction error: {str(e)}"
                )

                print(
                    "PREDICTION ERROR:",
                    e
                )


    # ============================================================
    # CONTEXT
    # ============================================================

    context = {

        # --------------------------------------------------------
        # Crop list
        # --------------------------------------------------------

        "crop_list":
            CROP_LIST,


        # --------------------------------------------------------
        # Form values
        # --------------------------------------------------------

        "crop":
            crop,

        "area_value":
            area_value,

        "area_unit":
            area_unit,

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


        # --------------------------------------------------------
        # Prediction
        # --------------------------------------------------------

        "predicted_yield":
            predicted_yield,

        "predicted_total_production":
            predicted_total_production,

        "predicted_tonnes":
            predicted_tonnes,


        # --------------------------------------------------------
        # Recommendations
        # --------------------------------------------------------

        "top_recommendations":
            top_recommendations,

        "crop_suitable":
            crop_suitable,


        # --------------------------------------------------------
        # Status
        # --------------------------------------------------------

        "prediction_done":
            prediction_done,

        "error":
            error
    }


    # ============================================================
    # RENDER
    # ============================================================

    return render(

        request,

        "yield_prediction.html",

        context

    )


# ============================================================
# PRODUCTION & LAND CALCULATOR — TOOL 1
# ============================================================

def production_land_calculator(request):

    # ========================================================
    # DEFAULT VALUES
    # ========================================================

    tool1_result = False

    tool1_error = None

    tool1_crop = ""

    tool1_desired_production = ""

    tool1_production_unit = "kg"

    tool1_available_land = ""

    tool1_land_unit = "cent"

    tool1_required_cent = 0

    tool1_required_acre = 0

    tool1_required_hectare = 0

    tool1_land_sufficient = False

    tool1_extra_cent = 0

    tool1_extra_acre = 0

    tool1_extra_hectare = 0


    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        crop = request.POST.get(
            "crop",
            ""
        ).strip()

        available_land_value = request.POST.get(
            "available_land",
            ""
        ).strip()

        land_unit = request.POST.get(
            "land_unit",
            "cent"
        ).strip().lower()

        desired_production_value = request.POST.get(
            "desired_production",
            ""
        ).strip()

        production_unit = request.POST.get(
            "production_unit",
            "kg"
        ).strip().lower()


        # ====================================================
        # KEEP FORM VALUES
        # ====================================================

        tool1_crop = crop

        tool1_available_land = (
            available_land_value
        )

        tool1_land_unit = land_unit

        tool1_desired_production = (
            desired_production_value
        )

        tool1_production_unit = (
            production_unit
        )


        # ====================================================
        # VALIDATION
        # ====================================================

        if not crop:

            tool1_error = (
                "Please select a crop."
            )

        elif crop not in CROP_LIST:

            tool1_error = (
                "Please select a valid crop."
            )

        elif not available_land_value:

            tool1_error = (
                "Please enter available land."
            )

        elif not desired_production_value:

            tool1_error = (
                "Please enter desired production."
            )

        elif land_unit not in [

            "cent",
            "acre",
            "hectare"

        ]:

            tool1_error = (
                "Invalid land unit."
            )

        elif production_unit not in [

            "kg",
            "tonne"

        ]:

            tool1_error = (
                "Invalid production unit."
            )

        elif production_yield_model is None:

            tool1_error = (
                "Random Forest production model "
                "could not be loaded."
            )

        else:

            try:

                available_land = float(
                    available_land_value
                )

                desired_production = float(
                    desired_production_value
                )


                # =================================================
                # VALIDATE NUMBERS
                # =================================================

                if available_land < 0:

                    raise ValueError(
                        "Available land cannot be negative."
                    )

                if desired_production <= 0:

                    raise ValueError(
                        "Desired production must be "
                        "greater than 0."
                    )


                # =================================================
                # TOOL 1 MODEL
                # =================================================

                prediction_data = pd.DataFrame({

                    "Crop": [
                        crop
                    ]

                })


                predicted_yield = (

                    production_yield_model
                    .predict(
                        prediction_data
                    )[0]

                )


                predicted_yield = float(
                    predicted_yield
                )


                if predicted_yield <= 0:

                    raise ValueError(
                        "The Random Forest production model "
                        "returned an invalid yield."
                    )


                # =================================================
                # DESIRED PRODUCTION → KG
                # =================================================

                if production_unit == "tonne":

                    desired_kg = (

                        desired_production
                        *
                        1000

                    )

                else:

                    desired_kg = (
                        desired_production
                    )


                # =================================================
                # LAND → HECTARE
                # =================================================

                if land_unit == "cent":

                    available_hectare = (

                        available_land
                        /
                        247.105

                    )

                elif land_unit == "acre":

                    available_hectare = (

                        available_land
                        *
                        0.404686

                    )

                else:

                    available_hectare = (
                        available_land
                    )


                # =================================================
                # REQUIRED LAND
                # =================================================

                required_hectare = (

                    desired_kg
                    /
                    predicted_yield

                )


                required_cent = (

                    required_hectare
                    *
                    247.105

                )


                required_acre = (

                    required_hectare
                    /
                    0.404686

                )


                # =================================================
                # LAND SUFFICIENCY
                # =================================================

                land_sufficient = (

                    available_hectare
                    >=
                    required_hectare

                )


                # =================================================
                # EXTRA LAND
                # =================================================

                extra_hectare = max(

                    required_hectare
                    -
                    available_hectare,

                    0

                )


                extra_cent = (

                    extra_hectare
                    *
                    247.105

                )


                extra_acre = (

                    extra_hectare
                    /
                    0.404686

                )


                # =================================================
                # STORE
                # =================================================

                tool1_required_hectare = round(
                    required_hectare,
                    2
                )

                tool1_required_cent = round(
                    required_cent,
                    2
                )

                tool1_required_acre = round(
                    required_acre,
                    2
                )

                tool1_extra_hectare = round(
                    extra_hectare,
                    2
                )

                tool1_extra_cent = round(
                    extra_cent,
                    2
                )

                tool1_extra_acre = round(
                    extra_acre,
                    2
                )

                tool1_land_sufficient = (
                    land_sufficient
                )

                tool1_result = True


            except ValueError as e:

                tool1_error = str(e)

            except Exception as e:

                tool1_error = (
                    f"Prediction error: {str(e)}"
                )


    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        "crop_list":
            CROP_LIST,

        "tool1_result":
            tool1_result,

        "tool1_error":
            tool1_error,

        "tool1_crop":
            tool1_crop,

        "tool1_desired_production":
            tool1_desired_production,

        "tool1_production_unit":
            tool1_production_unit,

        "tool1_available_land":
            tool1_available_land,

        "tool1_land_unit":
            tool1_land_unit,

        "tool1_required_cent":
            tool1_required_cent,

        "tool1_required_acre":
            tool1_required_acre,

        "tool1_required_hectare":
            tool1_required_hectare,

        "tool1_land_sufficient":
            tool1_land_sufficient,

        "tool1_extra_cent":
            tool1_extra_cent,

        "tool1_extra_acre":
            tool1_extra_acre,

        "tool1_extra_hectare":
            tool1_extra_hectare
    }


    return render(

        request,

        "index.html",

        context

    )


# ============================================================
# LOCATION-BASED WEATHER
# ============================================================

def get_weather(request):

    latitude = request.GET.get(
        "lat"
    )

    longitude = request.GET.get(
        "lon"
    )


    if not latitude or not longitude:

        return JsonResponse({

            "success": False,

            "error":
                "Latitude or longitude is missing."

        }, status=400)


    try:

        url = (
            "https://api.open-meteo.com/v1/forecast"
        )


        params = {

            "latitude":
                latitude,

            "longitude":
                longitude,

            "current":
                "temperature_2m,"
                "relative_humidity_2m,"
                "precipitation",

            "temperature_unit":
                "celsius",

            "precipitation_unit":
                "mm",

            "timezone":
                "auto"
        }


        response = requests.get(

            url,

            params=params,

            timeout=15

        )


        response.raise_for_status()


        weather_data = (
            response.json()
        )


        current = weather_data.get(

            "current",

            {}

        )


        return JsonResponse({

            "success":
                True,

            "temperature":
                current.get(
                    "temperature_2m"
                ),

            "humidity":
                current.get(
                    "relative_humidity_2m"
                ),

            "rainfall":
                current.get(
                    "precipitation",
                    0
                )

        })


    except requests.exceptions.RequestException:

        return JsonResponse({

            "success":
                False,

            "error":
                "Could not connect to weather service."

        }, status=503)


    except Exception as e:

        print(
            "WEATHER ERROR:",
            e
        )


        return JsonResponse({

            "success":
                False,

            "error":
                "Weather service error."

        }, status=500)