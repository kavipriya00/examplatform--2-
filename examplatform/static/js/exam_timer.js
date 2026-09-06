document.addEventListener("DOMContentLoaded", function () {
    const timerEl = document.getElementById("timer");
    const form = document.getElementById("exam-form");
    if (!timerEl || !form) return;

    let secondsLeft = parseInt(timerEl.dataset.minutes, 10) * 60;

    function updateDisplay() {
        const m = Math.floor(secondsLeft / 60);
        const s = secondsLeft % 60;
        timerEl.textContent = `Time left: ${m}:${s.toString().padStart(2, "0")}`;
    }

    updateDisplay();
    const interval = setInterval(function () {
        secondsLeft--;
        updateDisplay();
        if (secondsLeft <= 0) {
            clearInterval(interval);
            form.submit(); // auto-submit when time runs out
        }
    }, 1000);
});
