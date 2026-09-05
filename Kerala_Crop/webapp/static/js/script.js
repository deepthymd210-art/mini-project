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