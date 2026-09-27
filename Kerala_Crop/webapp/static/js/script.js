document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       MAIN YIELD PREDICTION
    ===================================================== */

    const predictionForm =
        document.getElementById("predictionForm");

    const predictionButton =
        document.getElementById("predictButton");

    if (predictionForm) {

        predictionForm.addEventListener("submit", function () {

            if (predictionButton) {

                predictionButton.innerHTML =
                    "⏳ Analyzing...";

                predictionButton.disabled = true;

            }

        });

    }


    /* =====================================================
       SCROLL TO YIELD PREDICTION RESULT
    ===================================================== */

    const predictionResult =
        document.getElementById("predictionResult");

    if (predictionResult) {

        setTimeout(function () {

            predictionResult.scrollIntoView({
                behavior: "smooth",
                block: "center"
            });

        }, 300);

    }


   


    /* =====================================================
       TOOL 1
       PRODUCTION & LAND CALCULATOR
    ===================================================== */

    const landForm =
        document.getElementById(
            "landCalculatorForm"
        );


    if (landForm) {

        landForm.addEventListener(
            "submit",
            function (event) {

                const cropElement =
                    document.getElementById(
                        "calcCrop"
                    );

                const landElement =
                    document.getElementById(
                        "availableLand"
                    );

                const productionElement =
                    document.getElementById(
                        "desiredProduction"
                    );


                const crop =
                    cropElement
                        ? cropElement.value
                        : "";


                const availableLand =
                    landElement
                        ? landElement.value
                        : "";


                const desiredProduction =
                    productionElement
                        ? productionElement.value
                        : "";


                if (!crop) {

                    event.preventDefault();

                    alert(
                        "Please select a crop."
                    );

                    return;

                }


                if (
                    availableLand === "" ||
                    parseFloat(availableLand) <= 0
                ) {

                    event.preventDefault();

                    alert(
                        "Please enter valid available land."
                    );

                    return;

                }


                if (
                    desiredProduction === "" ||
                    parseFloat(desiredProduction) <= 0
                ) {

                    event.preventDefault();

                    alert(
                        "Please enter valid desired production."
                    );

                    return;

                }


                const button =
                    landForm.querySelector(
                        ".tool-button"
                    );


                if (button) {

                    button.disabled = true;

                    button.innerHTML =
                        "⏳ Calculating...";

                }

            }
        );

    }


    /* =====================================================
       TOOL 2
       CROP REQUIREMENT GUIDE
    ===================================================== */

    const requirementForm =
        document.getElementById(
            "requirementForm"
        );


    if (requirementForm) {

        requirementForm.addEventListener(
            "submit",
            function (event) {

                const cropElement =
                    document.getElementById(
                        "requirementCrop"
                    );


                const crop =
                    cropElement
                        ? cropElement.value
                        : "";


                if (!crop) {

                    event.preventDefault();

                    alert(
                        "Please select a crop."
                    );

                    return;

                }


                const button =
                    requirementForm.querySelector(
                        ".tool-button"
                    );


                if (button) {

                    button.disabled = true;

                    button.innerHTML =
                        "⏳ Loading...";

                }

            }
        );

    }
});






//     /* =====================================================
//        weather API integration
//     ===================================================== */

// document.addEventListener("DOMContentLoaded", function () {

//     /* =====================================================
//        GET HTML ELEMENTS
//     ===================================================== */

//     const weatherButton =
//         document.getElementById("getWeatherButton");

//     const weatherStatus =
//         document.getElementById("weatherStatus");

//     const rainfallInput =
//         document.getElementById("rainfall");

//     const temperatureInput =
//         document.getElementById("temperature");

//     const humidityInput =
//         document.getElementById("humidity");


//     /* =====================================================
//        CHECK REQUIRED ELEMENTS
//     ===================================================== */

//     if (!weatherButton) {
//         console.error("getWeatherButton not found.");
//         return;
//     }

//     if (!weatherStatus) {
//         console.error("weatherStatus not found.");
//         return;
//     }

//     if (!rainfallInput) {
//         console.error("rainfall input not found.");
//         return;
//     }

//     if (!temperatureInput) {
//         console.error("temperature input not found.");
//         return;
//     }

//     if (!humidityInput) {
//         console.error("humidity input not found.");
//         return;
//     }


//     /* =====================================================
//        WEATHER BUTTON
//     ===================================================== */

//     weatherButton.addEventListener("click", function () {


//         /* =================================================
//            CHECK GEOLOCATION SUPPORT
//         ================================================= */

//         if (!navigator.geolocation) {

//             weatherStatus.textContent =
//                 "❌ Geolocation is not supported by your browser.";

//             return;
//         }


//         /* =================================================
//            BUTTON LOADING
//         ================================================= */

//         weatherButton.disabled = true;

//         weatherButton.textContent =
//             "⏳ Getting Location...";

//         weatherStatus.textContent =
//             "Please allow location access in your browser.";


//         /* =================================================
//            GET CURRENT LOCATION
//         ================================================= */

//         navigator.geolocation.getCurrentPosition(

//             /* =================================================
//                LOCATION SUCCESS
//             ================================================= */

//             function (position) {

//                 const latitude =
//                     position.coords.latitude;

//                 const longitude =
//                     position.coords.longitude;


//                 console.log(
//                     "Latitude:",
//                     latitude
//                 );

//                 console.log(
//                     "Longitude:",
//                     longitude
//                 );


//                 /* =================================================
//                    UPDATE STATUS
//                 ================================================= */

//                 weatherButton.textContent =
//                     "⏳ Getting Weather...";

//                 weatherStatus.textContent =
//                     "Fetching current weather conditions...";


//                 /* =================================================
//                    CREATE DJANGO WEATHER URL
//                 ================================================= */

//                 const weatherURL =
//                     "{% url 'get_weather' %}" +
//                     "?lat=" +
//                     encodeURIComponent(latitude) +
//                     "&lon=" +
//                     encodeURIComponent(longitude);


//                 console.log(
//                     "Weather URL:",
//                     weatherURL
//                 );


//                 /* =================================================
//                    SEND REQUEST TO DJANGO
//                 ================================================= */

//                 fetch(weatherURL)

//                     /* =================================================
//                        READ DJANGO RESPONSE
//                     ================================================= */

//                     .then(function (response) {

//                         console.log(
//                             "Django status:",
//                             response.status
//                         );


//                         /*
//                          * Read response as TEXT first.
//                          *
//                          * This prevents:
//                          *
//                          * Unexpected token '<'
//                          *
//                          * because Django may return HTML
//                          * for a 404 or server error.
//                          */

//                         return response.text().then(
//                             function (text) {

//                                 console.log(
//                                     "Django response:",
//                                     text
//                                 );


//                                 /* =====================================
//                                    HTTP ERROR
//                                 ===================================== */

//                                 if (!response.ok) {

//                                     throw new Error(
//                                         "Django error " +
//                                         response.status +
//                                         ": " +
//                                         text.substring(0, 200)
//                                     );

//                                 }


//                                 /* =====================================
//                                    CONVERT TEXT TO JSON
//                                 ===================================== */

//                                 try {

//                                     return JSON.parse(text);

//                                 }

//                                 catch (error) {

//                                     console.error(
//                                         "Invalid JSON response:",
//                                         text
//                                     );


//                                     throw new Error(
//                                         "Django returned HTML instead of JSON. " +
//                                         "Check the get_weather URL and view."
//                                     );

//                                 }

//                             }
//                         );

//                     })


//                     /* =================================================
//                        PROCESS WEATHER JSON
//                     ================================================= */

//                     .then(function (data) {

//                         console.log(
//                             "Weather JSON:",
//                             data
//                         );


//                         /* =============================================
//                            CHECK SUCCESS
//                         ============================================= */

//                         if (!data.success) {

//                             throw new Error(
//                                 data.error ||
//                                 "Unable to get weather data."
//                             );

//                         }


//                         /* =============================================
//                            GET VALUES
//                         ============================================= */

//                         const temperature =
//                             data.temperature;

//                         const humidity =
//                             data.humidity;

//                         const rainfall =
//                             data.rainfall;


//                         /* =============================================
//                            CHECK TEMPERATURE
//                         ============================================= */

//                         if (
//                             temperature === null ||
//                             temperature === undefined
//                         ) {

//                             throw new Error(
//                                 "Temperature data is unavailable."
//                             );

//                         }


//                         /* =============================================
//                            CHECK HUMIDITY
//                         ============================================= */

//                         if (
//                             humidity === null ||
//                             humidity === undefined
//                         ) {

//                             throw new Error(
//                                 "Humidity data is unavailable."
//                             );

//                         }


//                         /* =============================================
//                            CHECK RAINFALL
//                         ============================================= */

//                         if (
//                             rainfall === null ||
//                             rainfall === undefined
//                         ) {

//                             throw new Error(
//                                 "Rainfall data is unavailable."
//                             );

//                         }


//                         /* =============================================
//                            FILL FORM INPUTS
//                         ============================================= */

//                         temperatureInput.value =
//                             temperature;

//                         humidityInput.value =
//                             humidity;

//                         rainfallInput.value =
//                             rainfall;


//                         /* =============================================
//                            SUCCESS MESSAGE
//                         ============================================= */

//                         weatherStatus.innerHTML =
//                             "✅ Weather updated successfully." +
//                             "<br>" +
//                             "🌡️ " +
//                             temperature +
//                             " °C &nbsp; | &nbsp;" +
//                             "💧 " +
//                             humidity +
//                             " % &nbsp; | &nbsp;" +
//                             "🌧️ " +
//                             rainfall +
//                             " mm";


//                         /* =============================================
//                            RESET BUTTON
//                         ============================================= */

//                         weatherButton.textContent =
//                             "📍 Update Weather";

//                         weatherButton.disabled =
//                             false;

//                     })


//                     /* =================================================
//                        WEATHER / DJANGO ERROR
//                     ================================================= */

//                     .catch(function (error) {

//                         console.error(
//                             "Weather error:",
//                             error
//                         );


//                         weatherStatus.textContent =
//                             "❌ " +
//                             (
//                                 error.message ||
//                                 "Unable to get weather."
//                             );


//                         weatherButton.textContent =
//                             "📍 Try Again";

//                         weatherButton.disabled =
//                             false;

//                     });

//             },


//             /* =================================================
//                LOCATION ERROR
//             ================================================= */

//             function (error) {

//                 console.error(
//                     "Location error:",
//                     error
//                 );


//                 let message =
//                     "❌ Unable to get your location.";


//                 /* =============================================
//                    PERMISSION DENIED
//                 ============================================= */

//                 if (
//                     error.code ===
//                     error.PERMISSION_DENIED
//                 ) {

//                     message =
//                         "❌ Location permission was denied. " +
//                         "Please allow location access and try again.";

//                 }


//                 /* =============================================
//                    LOCATION UNAVAILABLE
//                 ============================================= */

//                 else if (
//                     error.code ===
//                     error.POSITION_UNAVAILABLE
//                 ) {

//                     message =
//                         "❌ Your location is currently unavailable.";

//                 }


//                 /* =============================================
//                    TIMEOUT
//                 ============================================= */

//                 else if (
//                     error.code ===
//                     error.TIMEOUT
//                 ) {

//                     message =
//                         "❌ Location request timed out. " +
//                         "Please try again.";

//                 }


//                 /* =============================================
//                    SHOW LOCATION ERROR
//                 ============================================= */

//                 weatherStatus.textContent =
//                     message;


//                 weatherButton.textContent =
//                     "📍 Try Again";

//                 weatherButton.disabled =
//                     false;

//             },


//             /* =================================================
//                GEOLOCATION OPTIONS
//             ================================================= */

//             {
//                 enableHighAccuracy: true,

//                 timeout: 15000,

//                 maximumAge: 300000
//             }

//         );

//     });

// });
