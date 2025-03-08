document.addEventListener("DOMContentLoaded", function () {
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById("expense-form").addEventListener("submit", savePayment);
    document.querySelectorAll(".edit-btn").forEach(button => button.addEventListener("click", editPayment));
    document.querySelectorAll(".paid-btn").forEach(button => {
        button.addEventListener("click", function () {
            const row = this.closest("tr");
            const paymentId = row.getAttribute("data-id");
            markAsPaid(paymentId, row);
        });
    });
}

async function savePayment(event) {
    event.preventDefault();

    let paymentId = document.getElementById("payment-id").value;
    let date = document.getElementById("date").value;
    let category = document.getElementById("category").value;
    let amount = document.getElementById("amount").value;
    let description = document.getElementById("description").value;
    let currency = document.getElementById("currency").value;  // Add this line

    let url = paymentId ? `/finance/edit-payment/${paymentId}/` : "/finance/add-payment/";
    let method = "POST";

    let response = await fetch(url, {
        method: method,
        body: JSON.stringify({ date, category, amount, description, currency }),  // Include currency
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        }
    });

    let result = await response.json();
    if (result.message) {
        window.location.reload(); // reload page
    }
}

function formatDate(dateString) {
    let date = new Date(dateString);
    return date.toISOString().split("T")[0]; // transfer to YYYY-MM-DD
}

function editPayment(event) {
    let row = event.target.closest("tr");
    let paymentId = row.getAttribute("data-id");
    let category = row.cells[0].getAttribute("data-category");
    let date = row.cells[1].textContent;
    let amount = row.cells[2].textContent;
    let description = row.cells[3].textContent;
    let currency = row.cells[4].textContent;  // Add this line

    document.getElementById("payment-id").value = paymentId;
    document.getElementById("category").value = category;
    document.getElementById("date").value = formatDate(date);
    document.getElementById("amount").value = amount;
    document.getElementById("description").value = description;
    document.getElementById("currency").value = currency;  // Add this line

    document.getElementById("delete-btn").classList.remove("hidden");
    document.getElementById("delete-btn").addEventListener("click", function () {
        deletePayment(paymentId, row);
    });
}

async function deletePayment(paymentId, row) {
    let response = await fetch(`/finance/delete-payment/${paymentId}/`, {
        method: "DELETE",
        headers: {
            "X-CSRFToken": getCookie("csrftoken")
        }
    });
    let result = await response.json();
    if (result.message) {
        row.remove();
        resetForm();
    }
}

async function markAsPaid(paymentId, row) {
    if (confirm("Mark this payment as paid? It will be added to your expense record.")) {
        let response = await fetch(`/finance/mark-payment-paid/${paymentId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Content-Type": "application/json"
            }
        });

        let result = await response.json();
        if (result.message) {
            alert(result.message);
            row.remove(); // Remove from the upcoming payments list
        }
    }
}

function resetForm() {
    document.getElementById("payment-id").value = "";
    document.getElementById("date").value = "";
    document.getElementById("category").value = "";
    document.getElementById("amount").value = "";
    document.getElementById("description").value = "";
    document.getElementById("delete-btn").classList.add("hidden");
}

// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.getElementById('add-payment-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {
        category: formData.get('category'),
        amount: formData.get('amount'),
        currency: formData.get('currency'),  // Ensure this is included
        date: formData.get('date'),
        description: formData.get('description'),
    };

    fetch("{% url 'add_upcoming_payment' %}", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
            window.location.reload();
        } else {
            alert(data.error);
        }
    });
});