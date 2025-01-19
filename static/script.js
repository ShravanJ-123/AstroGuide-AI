document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("astroForm").addEventListener("submit", function(event) {
        event.preventDefault();

        let data = {
            dob: document.getElementById("dob").value,
            tob: document.getElementById("tob").value,
            lat: document.getElementById("lat").value,
            lon: document.getElementById("lon").value,
            planet: document.getElementById("planet").value
        };

        fetch('/api/horoscope', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById("output").innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
            } else {
                document.getElementById("output").innerHTML = `
                    <h3>Horoscope Results:</h3>
                    <p><strong>General Prediction:</strong> ${data.general_prediction}</p>
                    <p><strong>Personalized Prediction:</strong> ${data.personalised_prediction}</p>
                    <p><strong>Qualities:</strong> ${data.qualities_long}</p>
                    <p><strong>Gayatri Mantra:</strong> ${data.gayatri_mantra}</p>
                `;
            }
        })
        .catch(error => {
            console.error("Error fetching horoscope:", error);
            document.getElementById("output").innerHTML = `<p style="color: red;">Error: Could not fetch horoscope.</p>`;
        });
    });
});
