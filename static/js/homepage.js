document.addEventListener("DOMContentLoaded", function () {
    const ctx = document.getElementById('spendingChart').getContext('2d');

    new Chart(ctx, {
        type: 'doughnut',  // Creates a circular chart
        data: {
            labels: ['Food', 'Shopping', 'Media', 'Transport'],
            datasets: [{
                data: [42, 36, 15, 5],  // Percentages
                backgroundColor: ['#FFA500', '#FF4500', '#8A2BE2', '#1E90FF'],  // Colors
                borderWidth: 1

            }]

        },
        options: {
            responsive: true,
            maintainAspectRatio: false,  // Allow custom size
            plugins: {
                legend: {
                    position: 'right'
                }
            }

        },


    });
});
