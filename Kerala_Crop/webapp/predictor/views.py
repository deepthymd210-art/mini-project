import os
import joblib
import pandas as pd
import requests

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render


# ============================================================
# PATHS
# ============================================================

MODEL_DIR = os.path.join(
    settings.BASE_DIR.parent,
    "models"
)

DATA_DIR = os.path.join(
    settings.BASE_DIR.parent,
    "data"
)

YIELD_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "random_forest_crop_yield.pkl"
)

DATASET_PATH = os.path.join(
    DATA_DIR,
    "kerala_crop_project_final_15000_recent.csv"
)


# ============================================================
# LOAD DATASET
# ============================================================

try:
    df = pd.read_csv(DATASET_PATH)
    print("Dataset loaded successfully.")

except Exception as e:
    df = pd.DataFrame()
    print("Dataset loading error:", e)


# ============================================================
# LOAD YIELD MODEL
# ============================================================

try:
    yield_model = joblib.load(YIELD_MODEL_PATH)
    print("Yield model loaded successfully.")

except Exception as e:
    yield_model = None
    print("Yield model loading error:", e)


# ============================================================
# CROP LIST
# ============================================================

def get_crop_list():

    if df.empty or "Crop" not in df.columns:
        return []

    return sorted(
        df["Crop"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )


# ============================================================
# HOME PAGE
# ============================================================

def index(request):

    return render(
        request,
        "index.html",
        {
            "crop_list": get_crop_list()
        }
    )


# ============================================================
# TOOL 1
# PRODUCTION & LAND CALCULATOR
# ============================================================

def production_land_calculator(request):

    context = {
        "crop_list": get_crop_list()
    }

    if request.method != "POST":
        return render(
            request,
            "index.html",
            context
        )

    try:

        # ----------------------------------------------------
        # USER INPUT
        # ----------------------------------------------------

        crop = request.POST.get(
            "crop",
            ""
        ).strip()

        available_land = float(
            request.POST.get(
                "available_land",
                0
            )
        )

        land_unit = request.POST.get(
            "land_unit",
            "cent"
        ).strip().lower()

        desired_production = float(
            request.POST.get(
                "desired_production",
                0
            )
        )

        production_unit = request.POST.get(
            "production_unit",
            "kg"
        ).strip().lower()


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not crop:
            raise ValueError(
                "Please select a crop."
            )

        if available_land <= 0:
            raise ValueError(
                "Please enter valid available land."
            )

        if desired_production <= 0:
            raise ValueError(
                "Please enter valid desired production."
            )

        if land_unit not in {
            "cent",
            "acre",
            "hectare"
        }:
            raise ValueError(
                "Invalid land unit."
            )

        if production_unit not in {
            "kg",
            "tonne"
        }:
            raise ValueError(
                "Invalid production unit."
            )


        # ----------------------------------------------------
        # FIND CROP DATA
        # ----------------------------------------------------

        crop_data = df[
            df["Crop"]
            .astype(str)
            .str.strip()
            .str.lower()
            == crop.lower()
        ]


        if crop_data.empty:
            raise ValueError(
                f"No data found for {crop}."
            )


        # ----------------------------------------------------
        # GET CROP YIELD
        # ----------------------------------------------------

        yield_values = pd.to_numeric(
            crop_data["Yield_kg_ha"],
            errors="coerce"
        ).dropna()


        if yield_values.empty:
            raise ValueError(
                f"Yield data is not available for {crop}."
            )


        yield_kg_ha = yield_values.mean()


        # ----------------------------------------------------
        # DESIRED PRODUCTION → KG
        # ----------------------------------------------------

        if production_unit == "tonne":
            desired_kg = desired_production * 1000
        else:
            desired_kg = desired_production


        # ----------------------------------------------------
        # REQUIRED LAND
        # ----------------------------------------------------

        required_hectare = (
            desired_kg / yield_kg_ha
        )

        required_cent = (
            required_hectare * 247.105
        )

        required_acre = (
            required_hectare / 0.404686
        )


        # ----------------------------------------------------
        # AVAILABLE LAND → HECTARE
        # ----------------------------------------------------

        if land_unit == "cent":

            available_hectare = (
                available_land / 247.105
            )

        elif land_unit == "acre":

            available_hectare = (
                available_land * 0.404686
            )

        else:

            available_hectare = available_land


        # ----------------------------------------------------
        # LAND SUFFICIENCY
        # ----------------------------------------------------

        land_sufficient = (
            available_hectare >= required_hectare
        )


        # ----------------------------------------------------
        # EXTRA LAND REQUIRED
        # ----------------------------------------------------

        extra_hectare = max(
            required_hectare - available_hectare,
            0
        )

        extra_cent = (
            extra_hectare * 247.105
        )

        extra_acre = (
            extra_hectare / 0.404686
        )


        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        context.update({

            "tool1_result": True,

            "tool1_crop": crop,

            "tool1_yield": round(
                yield_kg_ha,
                2
            ),

            "tool1_required_hectare": round(
                required_hectare,
                2
            ),

            "tool1_required_acre": round(
                required_acre,
                2
            ),

            "tool1_required_cent": round(
                required_cent,
                2
            ),

            "tool1_available_land":
                available_land,

            "tool1_land_unit":
                land_unit,

            "tool1_desired_production":
                desired_production,

            "tool1_production_unit":
                production_unit,

            "tool1_land_sufficient":
                land_sufficient,

            "tool1_extra_hectare": round(
                extra_hectare,
                2
            ),

            "tool1_extra_acre": round(
                extra_acre,
                2
            ),

            "tool1_extra_cent": round(
                extra_cent,
                2
            ),
        })


    except (ValueError, TypeError) as e:

        context["tool1_error"] = str(e)


    except Exception as e:

        context["tool1_error"] = (
            "Calculation error: " + str(e)
        )


    return render(
        request,
        "index.html",
        context
    )


# ============================================================
# TOOL 2
# CROP REQUIREMENT GUIDE
# ============================================================

def crop_requirement_guide(request):

    context = {
        "crop_list": get_crop_list()
    }

    if request.method != "POST":

        return render(
            request,
            "index.html",
            context
        )


    crop = request.POST.get(
        "crop",
        ""
    ).strip()


    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not crop:

        context["tool2_error"] = (
            "Please select a crop."
        )

        return render(
            request,
            "index.html",
            context
        )


    # --------------------------------------------------------
    # FIND CROP DATA
    # --------------------------------------------------------

    crop_data = df[
        df["Crop"]
        .astype(str)
        .str.strip()
        .str.lower()
        == crop.lower()
    ].copy()


    if crop_data.empty:

        context["tool2_error"] = (
            f"No data found for {crop}."
        )

        return render(
            request,
            "index.html",
            context
        )


    # --------------------------------------------------------
    # NUMERIC RANGE
    # --------------------------------------------------------

    def get_range(column):

        values = pd.to_numeric(
            crop_data[column],
            errors="coerce"
        ).dropna()


        if values.empty:
            return "Not available"


        minimum = values.min()
        maximum = values.max()


        if minimum == maximum:
            return f"{minimum:.2f}"


        return (
            f"{minimum:.2f} - "
            f"{maximum:.2f}"
        )


    # --------------------------------------------------------
    # TEXT VALUES
    # --------------------------------------------------------

    def get_values(column):

        values = (
            crop_data[column]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )

        return ", ".join(values)


    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    context.update({

        "tool2_result": True,

        "tool2_crop": crop,

        "tool2_soil":
            get_values("Soil_Type"),

        "tool2_ph":
            get_range("Soil_pH"),

        "tool2_nitrogen":
            get_range(
                "Nitrogen_N_kg_ha"
            ),

        "tool2_phosphorus":
            get_range(
                "Phosphorus_P_kg_ha"
            ),

        "tool2_potassium":
            get_range(
                "Potassium_K_kg_ha"
            ),

        "tool2_rainfall":
            get_range(
                "Rainfall_mm"
            ),

        "tool2_temperature":
            get_range(
                "Temperature_C"
            ),

        "tool2_humidity":
            get_range(
                "Humidity_percent"
            ),

        "tool2_irrigation":
            get_values(
                "Irrigation_Level"
            ),

        "tool2_season":
            get_values(
                "Season"
            ),
    })


    return render(
        request,
        "index.html",
        context
    )


# ============================================================
# YIELD PREDICTION
# ============================================================

def yield_prediction(request):

    predicted_yield = None
    predicted_tonnes = None
    top_recommendations = []
    crop_suitable = None
    error = None


    # --------------------------------------------------------
    # DEFAULT VALUES
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


    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        try:

            # ------------------------------------------------
            # GET INPUTS
            # ------------------------------------------------

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


            # ------------------------------------------------
            # VALIDATION
            # ------------------------------------------------

            required_fields = {
                "crop": crop,
                "cultivated area": area_value,
                "soil type": soil_type,
                "soil pH": soil_ph,
                "nitrogen value": nitrogen,
                "phosphorus value": phosphorus,
                "potassium value": potassium,
                "rainfall": rainfall,
                "temperature": temperature,
                "humidity": humidity,
                "irrigation level": irrigation,
                "season": season,
            }


            for field_name, value in required_fields.items():

                if not value:

                    raise ValueError(
                        f"Please enter/select {field_name}."
                    )


            # ------------------------------------------------
            # NUMERIC VALUES
            # ------------------------------------------------

            area = float(area_value)
            soil_ph_value = float(soil_ph)
            nitrogen_value = float(nitrogen)
            phosphorus_value = float(phosphorus)
            potassium_value = float(potassium)
            rainfall_value = float(rainfall)
            temperature_value = float(temperature)
            humidity_value = float(humidity)


            if area <= 0:

                raise ValueError(
                    "Cultivated area must be greater than 0."
                )


            # ------------------------------------------------
            # AREA CONVERSION
            # ------------------------------------------------

            if area_unit == "hectare":

                area_hectare = area

            elif area_unit == "acre":

                area_hectare = (
                    area * 0.404686
                )

            elif area_unit == "cent":

                area_hectare = (
                    area / 247.105
                )

            else:

                raise ValueError(
                    "Invalid area unit."
                )


            area_cent = (
                area_hectare * 247.105
            )


            # ------------------------------------------------
            # CHECK MODEL
            # ------------------------------------------------

            if yield_model is None:

                raise ValueError(
                    "Yield model is not available."
                )


            # ------------------------------------------------
            # CREATE MODEL INPUT
            # ------------------------------------------------

            def create_crop_input(crop_name):

                return pd.DataFrame([{

                    "Crop": crop_name,

                    "Area": area_hectare,

                    "Area_Cent": area_cent,

                    "Soil_Type": soil_type,

                    "Soil_pH": soil_ph_value,

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


            # ------------------------------------------------
            # SELECTED CROP
            # ------------------------------------------------

            selected_input = create_crop_input(
                crop
            )

            yield_per_hectare = float(
                yield_model.predict(
                    selected_input
                )[0]
            )

            yield_per_hectare = max(
                yield_per_hectare,
                0
            )


            # ------------------------------------------------
            # TOTAL PRODUCTION
            # ------------------------------------------------

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


            # ------------------------------------------------
            # TOP 3 CROPS
            # ------------------------------------------------
            # No crop recommendation model is used.
            # The yield model tests every crop using
            # the same user-entered farming conditions.
            # ------------------------------------------------

            all_crops = get_crop_list()

            all_crop_production = []


            for test_crop in all_crops:

                crop_input = create_crop_input(
                    test_crop
                )

                crop_yield = float(
                    yield_model.predict(
                        crop_input
                    )[0]
                )

                crop_yield = max(
                    crop_yield,
                    0
                )

                crop_production = (
                    crop_yield
                    * area_hectare
                )

                all_crop_production.append({

                    "crop":
                        test_crop,

                    "production":
                        round(
                            crop_production,
                            2
                        ),

                    "tonnes":
                        round(
                            crop_production / 1000,
                            2
                        ),
                })


            # ------------------------------------------------
            # SORT HIGHEST → LOWEST
            # ------------------------------------------------

            all_crop_production.sort(
                key=lambda item: item["production"],
                reverse=True
            )


            # ------------------------------------------------
            # TOP 3 ONLY
            # ------------------------------------------------

            top_recommendations = (
                all_crop_production[:3]
            )


            # ------------------------------------------------
            # ADD RANK
            # ------------------------------------------------

            for rank, item in enumerate(
                top_recommendations,
                start=1
            ):

                item["rank"] = rank


            # ------------------------------------------------
            # SELECTED CROP STATUS
            # ------------------------------------------------

            if top_recommendations:

                crop_suitable = any(
                    item["crop"].lower()
                    == crop.lower()
                    for item in top_recommendations
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


    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

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


# ============================================================
# LOCATION-BASED WEATHER
# ============================================================

def get_weather(request):

    latitude = request.GET.get("lat")
    longitude = request.GET.get("lon")


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
                "auto",
        }


        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        weather_data = response.json()

        current = weather_data.get(
            "current",
            {}
        )


        return JsonResponse({

            "success": True,

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
                ),
        })


    except requests.exceptions.RequestException:

        return JsonResponse({

            "success": False,

            "error":
                "Could not connect to weather service."

        }, status=503)


    except Exception as e:

        print(
            "WEATHER ERROR:",
            e
        )

        return JsonResponse({

            "success": False,

            "error":
                "Weather service error."

        }, status=500)