document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("predictionForm");
    const button = document.getElementById("predictButton");

    /* =====================================================
       PREDICT BUTTON
    ===================================================== */

    if (form) {

        form.addEventListener("submit", function () {

            if (button) {

                button.innerHTML = "⏳ Analyzing...";
                button.disabled = true;

            }

        });

    }


    /* =====================================================
       SCROLL TO RESULT
    ===================================================== */

    const result = document.getElementById("predictionResult");

    if (result) {

        setTimeout(function () {

            result.scrollIntoView({
                behavior: "smooth",
                block: "center"
            });

        }, 300);

    }

});


/* =====================================================
   TRY ANOTHER PREDICTION
===================================================== */

function resetPrediction() {

    /*
       Go to a fresh GET request.

       This removes the previous POST data
       and loads a completely new prediction page.
    */

    window.location.href = window.location.pathname;

}

// ============================================================
// CSRF TOKEN
// ============================================================

function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {
            cookie = cookie.trim();

            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }

    return cookieValue;
}


function calculateLand() {

    const cropElement = document.getElementById("calcCrop");
    const landElement = document.getElementById("availableLand");
    const landUnitElement = document.getElementById("landUnit");
    const productionElement = document.getElementById("desiredProduction");
    const productionUnitElement = document.getElementById("productionUnit");
    const resultBox = document.getElementById("landResult");

    // Get values
    const crop = cropElement.value.trim();
    const availableLand = landElement.value.trim();
    const landUnit = landUnitElement.value;
    const desiredProduction = productionElement.value.trim();
    const productionUnit = productionUnitElement.value;

    console.log("Crop selected:", crop);
    console.log("Available land:", availableLand);
    console.log("Land unit:", landUnit);
    console.log("Desired production:", desiredProduction);
    console.log("Production unit:", productionUnit);

    // Validation
    if (crop === "") {
        resultBox.innerHTML =
            "<p class='error'>⚠️ Please select a crop.</p>";
        return;
    }

    if (availableLand === "" || parseFloat(availableLand) <= 0) {
        resultBox.innerHTML =
            "<p class='error'>⚠️ Please enter available land.</p>";
        return;
    }

    if (desiredProduction === "" || parseFloat(desiredProduction) <= 0) {
        resultBox.innerHTML =
            "<p class='error'>⚠️ Please enter desired production.</p>";
        return;
    }

    resultBox.innerHTML =
        "<p>⏳ Calculating using AI model...</p>";

    const calculateUrl = resultBox.dataset.url;

    // CSRF token
    let csrfToken = "";

    const csrfInput =
        document.querySelector("[name=csrfmiddlewaretoken]");

    if (csrfInput) {
        csrfToken = csrfInput.value;
    }

    fetch(calculateUrl, {

        method: "POST",

        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },

        body: JSON.stringify({

            crop: crop,

            available_land:
                parseFloat(availableLand),

            land_unit: landUnit,

            desired_production:
                parseFloat(desiredProduction),

            production_unit: productionUnit
        })
    })

    .then(response => {

        if (!response.ok) {
            return response.text().then(text => {
                throw new Error(
                    "Server returned " +
                    response.status +
                    ": " +
                    text.substring(0, 200)
                );
            });
        }

        return response.json();
    })

    .then(data => {

        console.log("Server response:", data);

        if (!data.success) {
            throw new Error(
                data.error || "Prediction failed"
            );
        }

        resultBox.innerHTML = `

            <div class="result-card">

                <h3>🌱 Crop: ${data.crop}</h3>

                <p>
                    📐 <strong>Available Land:</strong>
                    ${data.available_land}
                    ${data.land_unit}
                </p>

                <p>
                    🎯 <strong>Desired Production:</strong>
                    ${data.desired_production}
                    ${data.production_unit}
                </p>

                <hr>

                <p>
                    🤖 <strong>AI Predicted Yield:</strong>
                    ${Number(data.predicted_yield).toFixed(2)}
                    kg/ha
                </p>

                <p>
                    🌾 <strong>Required Land:</strong>
                    ${Number(data.required_hectare).toFixed(4)}
                    hectare
                </p>

                <p>
                    📏 <strong>Required Land:</strong>
                    ${Number(data.required_cent).toFixed(2)}
                    cent
                </p>

                <p>
                    📏 <strong>Required Land:</strong>
                    ${Number(data.required_acre).toFixed(4)}
                    acre
                </p>

                <hr>

                <p>
                    📦 <strong>Production from Available Land:</strong>
                    ${Number(data.available_production_kg).toFixed(2)}
                    kg
                </p>

                <p>
                    ⚖️ <strong>Approximately:</strong>
                    ${Number(data.available_production_tonnes).toFixed(2)}
                    tonnes
                </p>

                <div class="${data.is_sufficient
                    ? "success-box"
                    : "warning-box"}">

                    ${data.message}

                </div>

            </div>
        `;
    })

    .catch(error => {

        console.error("Prediction error:", error);

        resultBox.innerHTML = `
            <div class="error">
                ❌ Prediction error: ${error.message}
            </div>
        `;
    });
}
// ============================================================
// TOOL 2
// CROP REQUIREMENT GUIDE
// ============================================================

function showCropRequirements() {

    const crop =
        document.getElementById(
            "requirementCrop"
        ).value;

    const soilType =
        document.getElementById(
            "requirementSoil"
        ).value;

    const result =
        document.getElementById(
            "cropRequirements"
        );


    // --------------------------------------------------------
    // NOTHING SELECTED
    // --------------------------------------------------------

    if (!crop || !soilType) {

        result.innerHTML = `

            <div class="requirement-placeholder">

                <span>
                    🌿
                </span>

                <p>
                    Select a crop and soil type to
                    view recommended requirements.
                </p>

            </div>

        `;

        return;
    }


    // --------------------------------------------------------
    // LOADING
    // --------------------------------------------------------

    result.innerHTML = `

        <div class="result-loading">
            ⏳ Analyzing crop and soil...
        </div>

    `;


    // --------------------------------------------------------
    // SEND DATA TO DJANGO
    // --------------------------------------------------------

    const formData = new FormData();

    formData.append(
        "crop",
        crop
    );

    formData.append(
        "soil_type",
        soilType
    );


    fetch(
        "/crop-requirements/",
        {

            method: "POST",

            headers: {

                "X-CSRFToken":
                    getCSRFToken()

            },

            body: formData

        }
    )

    .then(response => response.json())

    .then(data => {

        if (!data.success) {

            result.innerHTML = `

                <div class="result-error">

                    ⚠️ ${data.error}

                </div>

            `;

            return;
        }


        // ----------------------------------------------------
        // SOIL MATCH MESSAGE
        // ----------------------------------------------------

        let matchMessage = "";

        if (data.exact_soil_match) {

            matchMessage = `

                <div class="result-success">

                    ✅ Requirements based on
                    ${data.crop} + ${data.soil_type}
                    records.

                </div>

            `;

        } else {

            matchMessage = `

                <div class="result-warning">

                    ℹ️ Exact ${data.crop} +
                    ${data.soil_type} data was limited.
                    Values are estimated from available
                    ${data.crop} records.

                </div>

            `;

        }


        // ----------------------------------------------------
        // FORMAT VALUE
        // ----------------------------------------------------

        function value(value, unit = "") {

            if (
                value === null ||
                value === undefined
            ) {

                return "Not available";

            }

            return `${value} ${unit}`;

        }


        // ----------------------------------------------------
        // DISPLAY
        // ----------------------------------------------------

        result.innerHTML = `

            <div class="requirements-content">

                <h4>
                    🌱 ${data.crop}
                </h4>

                <p class="soil-selected">

                    Soil:
                    <strong>
                        ${data.soil_type}
                    </strong>

                </p>


                ${matchMessage}


                <div class="requirement-grid">


                    <div class="requirement-box">

                        <span>
                            🧪
                        </span>

                        <small>
                            Nitrogen (N)
                        </small>

                        <strong>
                            ${value(
                                data.nitrogen,
                                "kg/ha"
                            )}
                        </strong>

                    </div>


                    <div class="requirement-box">

                        <span>
                            🧪
                        </span>

                        <small>
                            Phosphorus (P)
                        </small>

                        <strong>
                            ${value(
                                data.phosphorus,
                                "kg/ha"
                            )}
                        </strong>

                    </div>


                    <div class="requirement-box">

                        <span>
                            🧪
                        </span>

                        <small>
                            Potassium (K)
                        </small>

                        <strong>
                            ${value(
                                data.potassium,
                                "kg/ha"
                            )}
                        </strong>

                    </div>


                    <div class="requirement-box">

                        <span>
                            ⚗️
                        </span>

                        <small>
                            Soil pH
                        </small>

                        <strong>
                            ${value(
                                data.soil_ph
                            )}
                        </strong>

                    </div>


                    <div class="requirement-box">

                        <span>
                            🌧️
                        </span>

                        <small>
                            Rainfall
                        </small>

                        <strong>
                            ${value(
                                data.rainfall,
                                "mm"
                            )}
                        </strong>

                    </div>


                    <div class="requirement-box">

                        <span>
                            🌡️
                        </span>

                        <small>
                            Temperature
                        </small>

                        <strong>
                            ${value(
                                data.temperature,
                                "°C"
                            )}
                        </strong>

                    </div>


                    <div class="requirement-box">

                        <span>
                            💧
                        </span>

                        <small>
                            Humidity
                        </small>

                        <strong>
                            ${value(
                                data.humidity,
                                "%"
                            )}
                        </strong>

                    </div>


                    <div class="requirement-box">

                        <span>
                            🚿
                        </span>

                        <small>
                            Irrigation
                        </small>

                        <strong>
                            ${value(
                                data.irrigation
                            )}
                        </strong>

                    </div>


                    <div class="requirement-box">

                        <span>
                            🌤️
                        </span>

                        <small>
                            Season
                        </small>

                        <strong>
                            ${value(
                                data.season
                            )}
                        </strong>

                    </div>


                </div>


                <p class="sample-info">

                    Based on
                    <strong>
                        ${data.sample_count}
                    </strong>
                    matching dataset records.

                </p>

            </div>

        `;

    })

    .catch(error => {

        console.error(error);

        result.innerHTML = `

            <div class="result-error">

                ⚠️ Unable to retrieve crop
                requirements.

            </div>

        `;

    });

}