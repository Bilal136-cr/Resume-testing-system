function updateTotalWeight() {
    let total = 0;
    document.querySelectorAll('input[name="weight[]"]').forEach(input => {
        total += parseInt(input.value) || 0;
    });
    document.getElementById("total-weight").innerText = total;

    const totalDisplay = document.getElementById("total-weight");
    if (total > 100) {
        totalDisplay.style.color = "red";
    } else if (total === 100) {
        totalDisplay.style.color = "green";
    } else {
        totalDisplay.style.color = "orange";
    }
}

function addCriteria() {
    const container = document.getElementById("criteria-container");
    const div = document.createElement("div");
    div.classList.add("criteria-group");

    div.innerHTML = `
        <input type="text" name="keyword[]" placeholder="Keyword (e.g., Django)" required>
        <input type="number" name="weight[]" placeholder="Weight (e.g., 3)" min="1" required>
        <button type="button" onclick="this.parentElement.remove(); updateTotalWeight()">Remove</button>
    `;
    container.appendChild(div);
    updateTotalWeight();
}

document.addEventListener('input', function (e) {
    if (e.target.name === 'weight[]') {
        updateTotalWeight();
    }
});

// Initial call to calculate on load (for page reload)
document.addEventListener('DOMContentLoaded', updateTotalWeight);
