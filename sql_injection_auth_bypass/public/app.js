document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const data = new FormData(form);
        const resultBox = document.getElementById(
            form.id === "vulnerable-form" ? "vulnerable-result" : "secure-result"
        );

        resultBox.className = "result";
        resultBox.textContent = "Checking credentials...";

        try {
            const response = await fetch(form.dataset.endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    username: data.get("username"),
                    password: data.get("password")
                })
            });

            const result = await response.json();
            resultBox.textContent = result.message +
                (result.user ? ` (user: ${result.user})` : "");
            resultBox.classList.add(result.success ? "ok" : "fail");
        } catch (error) {
            resultBox.textContent = "Could not reach the server. Check that it is running.";
            resultBox.classList.add("fail");
        }
    });
});
