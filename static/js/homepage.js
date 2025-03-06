document.addEventListener("DOMContentLoaded", function () {

    const today = new Date();
    const formattedDate = today.toLocaleDateString("en-US", { weekday: 'long', year: 'numeric', month: 'short', day: 'numeric' });
    document.getElementById("dateDisplay").textContent = formattedDate;


    fetch("/api/spending-summary/")
        .then(response => response.json())
        .then(data => {
            console.log("Spending Summary Data:", data);


            const labels = data.categories.map(category => category.category);
            const amounts = data.categories.map(category => Number(category.amount));
            const colors = ['#FFA500', '#FF4500', '#8A2BE2', '#1E90FF', '#FF1493'];


            document.getElementById("chartCenterText").textContent = `$${Number(data.total_spent).toLocaleString()}`;


            const categoryInfo = document.getElementById("categoryInfo");
            categoryInfo.innerHTML = "";
            data.categories.forEach((category, index) => {
                const div = document.createElement("div");
                div.classList.add("category-item");
                div.innerHTML = `
                <div style="display: flex; align-items: center;">
                    <div class="color-box" style="background: ${colors[index % colors.length]}"></div>
                    <span>${category.category}</span>
                </div>
                <span>${category.percentage}%</span>
            `;
                categoryInfo.appendChild(div);
            });

            // render the pie chart
            const ctx = document.getElementById("spendingChart").getContext("2d");
            if (window.myChart) window.myChart.destroy();
            window.myChart = new Chart(ctx, {
                type: "doughnut",
                data: {
                    labels: labels,
                    datasets: [{
                        data: amounts,
                        backgroundColor: colors,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    aspectRatio: window.innerWidth < 768 ? 1 : 1.5,
                    cutout: "80%",
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        })
        .catch(error => console.error("Error fetching spending summary:", error));

    // fetch the upcoming expense
    fetch("/api/upcoming-expenses/")
        .then(response => response.json())
        .then(data => {
            console.log("Upcoming Payments Data:", data);
            const upcomingList = document.getElementById("upcomingPaymentsList");
            upcomingList.innerHTML = data.upcoming_expenses.length === 0
                ? "<p>No upcoming payments</p>"
                : data.upcoming_expenses.map(payment => `
                    <div class="payment-item">
                        <span>${payment.category}</span> <span>-$${payment.amount} (Due: ${payment.due_date})</span>
                    </div>
                `).join('');
        })
        .catch(error => console.error("Error fetching upcoming expenses:", error));

    // fetch the expense target
    fetch("/api/expense-targets/")
        .then(response => response.json())
        .then(data => {
            console.log("Expense Targets Data:", data);
            const targetSection = document.getElementById("expenseTargetList");
            targetSection.innerHTML = data.expense_targets.length === 0
                ? "<p>No expense targets set</p>"
                : data.expense_targets.map(target => {
                    const progressWidth = Math.min((target.current_spent / target.target_amount) * 100, 100);
                    return `
                        <div class="target-item">
                            <div class="target-category">${target.category}</div>
                            <div class="target-progress-container">
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${progressWidth}%;"></div>
                                </div>
                                <div class="target-amount">$${target.current_spent} / $${target.target_amount}</div>
                            </div>
                        </div>
                    `;
                }).join('');
        })
        .catch(error => console.error("Error fetching expense targets:", error));


    document.getElementById("editExpenseTargetModal").addEventListener("show.bs.modal", function () {
        fetch("/api/categories/")
            .then(response => response.json())
            .then(data => {
                const categorySelect = document.getElementById("categorySelect");
                categorySelect.innerHTML = data.categories.map(category => `<option value="${category.id}">${category.name}</option>`).join('');
            })
            .catch(error => console.error("Error loading categories:", error));

        fetch("/api/get-current-user/")
            .then(response => response.json())
            .then(data => {
                document.getElementById("userSelect").innerHTML = `<option value="${data.user_id}" selected>${data.username}</option>`;
            })
            .catch(error => console.error("Error loading user:", error));

        document.getElementById("monthInput").value = new Date().toISOString().slice(0, 7);
    });


    document.getElementById("saveExpenseTarget").addEventListener("click", function () {
        const user = document.getElementById("userSelect").value;
        const category = document.getElementById("categorySelect").value;
        const amount = document.getElementById("amountInput").value;
        const month = document.getElementById("monthInput").value;

        if (!user || !category || !amount || !month) {
            alert("Please fill in all fields.");
            return;
        }

        fetch("/api/expense-targets/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({ user, category, amount, month })
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert("Failed to save expense target.");
                } else {
                    alert("Expense target saved successfully!");
                    location.reload();
                }
            })
            .catch(error => alert("Failed to save expense target."));
    });


    function getCSRFToken() {
        return document.cookie.split("; ").find(row => row.startsWith("csrftoken"))?.split("=")[1];
    }
});
