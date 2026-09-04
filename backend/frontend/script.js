async function analyzePayment() {

    console.log("BUTTON CLICKED");

    // ==========================================
    // GET FORM VALUES
    // ==========================================

    const amount = parseFloat(
        document.getElementById("amount").value
    );

    const country =
        document.getElementById("country").value.trim();

    const failureReason =
        document.getElementById("failure_reason").value;

    const threeDsSupported =
        document.getElementById("three_ds_supported").checked;


    // ==========================================
    // GET RESULT ELEMENTS
    // ==========================================

    const loadingElement =
        document.getElementById("loading");

    const resultElement =
        document.getElementById("result");

    const errorElement =
        document.getElementById("error");

    const statusElement =
        document.getElementById("status");

    const strategyElement =
        document.getElementById("strategy");

    const retryAfterElement =
        document.getElementById("retry");

    const maxRetriesElement =
        document.getElementById("maxRetries");

    const recommendationElement =
        document.getElementById("message");


    // ==========================================
    // VALIDATION
    // ==========================================

    if (isNaN(amount) || amount <= 0) {
        alert("Please enter a valid payment amount.");
        return;
    }

    if (!country) {
        alert("Please enter the country.");
        return;
    }


    // ==========================================
    // SHOW LOADING
    // ==========================================

    loadingElement.classList.remove("hidden");
    resultElement.classList.add("hidden");
    errorElement.classList.add("hidden");


    // ==========================================
    // PAYMENT DATA
    // ==========================================

    const paymentData = {
        amount: amount,
        country: country,
        failure_reason: failureReason,
        three_ds_supported: threeDsSupported
    };


    try {

        // ==========================================
        // STEP 1: ANALYZE PAYMENT
        // ==========================================

        console.log("Sending payment data:", paymentData);

        const analyzeResponse = await fetch(
            "http://127.0.0.1:8000/payment/analyze",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(paymentData)
            }
        );


        if (!analyzeResponse.ok) {
            throw new Error(
                "Payment analysis failed: HTTP " +
                analyzeResponse.status
            );
        }


        const analysis =
            await analyzeResponse.json();

        console.log("Analysis response:", analysis);


        // ==========================================
        // STEP 2: GET RETRY DECISION
        // ==========================================

        const retryResponse = await fetch(
            "http://127.0.0.1:8000/payment/retry",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(paymentData)
            }
        );


        if (!retryResponse.ok) {
            throw new Error(
                "Retry decision failed: HTTP " +
                retryResponse.status
            );
        }


        const retry =
            await retryResponse.json();

        console.log("Retry response:", retry);


        // ==========================================
        // STEP 3: DISPLAY STATUS
        // ==========================================

        statusElement.textContent =
            analysis.recommended_action ||
            retry.status ||
            "-";


        // ==========================================
        // DISPLAY STRATEGY
        // ==========================================

        strategyElement.textContent =
            retry.strategy || "-";


        // ==========================================
        // DISPLAY RETRY TIME
        // ==========================================

        const seconds =
            retry.retry_after_seconds;


        if (seconds === 0) {

            retryAfterElement.textContent =
                "Immediately";

        } else if (seconds >= 3600) {

            const hours = seconds / 3600;

            retryAfterElement.textContent =
                hours +
                (hours === 1 ? " hour" : " hours");

        } else if (seconds >= 60) {

            const minutes = seconds / 60;

            retryAfterElement.textContent =
                minutes +
                (minutes === 1 ? " minute" : " minutes");

        } else if (seconds !== undefined && seconds !== null) {

            retryAfterElement.textContent =
                seconds + " seconds";

        } else {

            retryAfterElement.textContent = "-";
        }


        // ==========================================
        // DISPLAY MAX RETRIES
        // ==========================================

        maxRetriesElement.textContent =
            retry.max_retries !== undefined &&
            retry.max_retries !== null
                ? retry.max_retries
                : "-";


        // ==========================================
        // DISPLAY RECOMMENDATION
        // ==========================================

        recommendationElement.textContent =
            analysis.message ||
            retry.message ||
            "No recommendation available.";


        // ==========================================
        // SHOW RESULT
        // ==========================================

        loadingElement.classList.add("hidden");
        resultElement.classList.remove("hidden");


    } catch (error) {

        console.error("ERROR:", error);


        // Hide loading
        loadingElement.classList.add("hidden");


        // Hide result
        resultElement.classList.add("hidden");


        // Show error
        errorElement.classList.remove("hidden");

        errorElement.textContent =
            "Error: " +
            error.message +
            ". Make sure the FastAPI server is running.";
    }
}