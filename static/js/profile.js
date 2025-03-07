document.getElementById("settingsButton").onclick = function() {
    location.href = "/finance/settings";  
};

document.getElementById("notificationButton").onclick = function() {
    document.getElementById("notifDialog").showModal();
}

document.getElementById("closeNotifDialogBtn").onclick = function() {
    document.getElementById("notifDialog").close();
}

document.getElementById("FAQ").onclick = function() {
    location.href = "/finance/faq";  
};

document.getElementById("contactUsButton").onclick = function() {
    document.getElementById("contactDialog").showModal();
}

document.getElementById("closeContactDialog").onclick = function() {
    document.getElementById("contactDialog").close();
}

document.getElementById("closeContactDialogBtn").onclick = function() {
    document.getElementById("contactDialog").close();
}