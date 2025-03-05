document.getElementById("inpb1").onclick = function (event) {
    hidePassword(event); // Hide password if another field is clicked
    toggleInput("inp1");
    event.stopPropagation();
};

document.getElementById("inpb2").onclick = function (event) {
    hidePassword(event); // Hide password if another field is clicked
    toggleInput("inp2");
    event.stopPropagation();
};

document.getElementById("inpb3").onclick = function (event) {
    let inputField = document.getElementById("inp3");
    inputField.disabled = !inputField.disabled; // Toggle disabled state

    if (!inputField.disabled) {
        inputField.type = "text"; // Show password
        inputField.focus();
    } else {
        inputField.type = "password"; // Hide password when disabled
    }

    event.stopPropagation();
};

// Prevent hiding password when clicking inside the password input field
document.getElementById("inp3").addEventListener("click", function (event) {
    event.stopPropagation();
});

// Hide password when clicking anywhere else on the document (excluding the password field itself)
document.addEventListener("click", function (event) {
    hidePassword(event);
});

function hidePassword(event) {
    let passwordField = document.getElementById("inp3");

    // If the click target is NOT the password field or its button, hide the password
    if (event.target !== passwordField && event.target !== document.getElementById("inpb3")) {
        if (!passwordField.disabled) {
            passwordField.type = "password"; // Hide password
            passwordField.disabled = true; // Lock the field again
        }
    }
}

// Function to toggle input fields
function toggleInput(inputId) {
    let inputField = document.getElementById(inputId);
    inputField.disabled = !inputField.disabled;
    if (!inputField.disabled) {
        inputField.focus();
    }
}

document.getElementById("dlb").onclick = function() {
    document.getElementById("deleteButtonDialog").showModal();
}

document.getElementById("closeDialog").onclick = function() {
    document.getElementById("deleteButtonDialog").close();
}

document.getElementById("cancel").onclick = function() {
    document.getElementById("deleteButtonDialog").close();
}
