document.addEventListener("DOMContentLoaded", function () {
    let searchBtn = document.getElementById("search-btn");

    if (!searchBtn) {
        console.error("Error: Cannot find #search-btn");
        return;
    }

    console.log("find Search button, start listening Click event");

    const urlParams = new URLSearchParams(window.location.search);
    document.getElementById("start_date").value = urlParams.get("start_date") || "";
    document.getElementById("end_date").value = urlParams.get("end_date") || "";
    document.getElementById("category").value = urlParams.get("category") || "ALL";

    searchBtn.addEventListener("click", function () {
        let startDate = document.getElementById("start_date").value;
        let endDate = document.getElementById("end_date").value;
        let category = document.getElementById("category").value;
        let encodedCategory = encodeURIComponent(category);

        console.log("Search clicked:", { startDate, endDate, category });

        let url = `/finance/income-record/?start_date=${startDate}&end_date=${endDate}&category=${encodedCategory}`;
        console.log("Redirecting to:", url);
        window.location.href = url;
    });
});
