document.getElementById("settingsButton").onclick = function () {
    location.href = "/finance/settings";
};

document.getElementById("notificationButton").onclick = function () {
    document.getElementById("notifDialog").showModal();
}

document.getElementById("closeNotifDialogBtn").onclick = function () {
    document.getElementById("notifDialog").close();
}

document.getElementById("FAQ").onclick = function () {
    location.href = "/finance/faq";
};

document.getElementById("contactUsButton").onclick = function () {
    document.getElementById("contactDialog").showModal();
}

document.getElementById("closeContactDialog").onclick = function () {
    document.getElementById("contactDialog").close();
}

document.getElementById("closeContactDialogBtn").onclick = function () {
    document.getElementById("contactDialog").close();
}

document.getElementById("notifToggle").addEventListener("change", function () {
    const isEnabled = this.checked;

    fetch("/finance/toggle-notifications/", {
        method: "POST",

        headers: {
            "X-CSRFToken": "{{ csrf_token }}",
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ enabled: isEnabled }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert("Notification preferences updated successfully.");
            } else {
                alert("Failed to update notification preferences.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
        });
});