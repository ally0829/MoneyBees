// Get references to the form and confirm button
const form = document.getElementById('settings-form');
const confirmBtn = document.getElementById('confirm-btn');

// Get the initial values of the form fields
const initialValues = {
    first_name: form.querySelector('[name="first_name"]').value,
    last_name: form.querySelector('[name="last_name"]').value,
    email: form.querySelector('[name="email"]').value,
    password: form.querySelector('[name="password"]').value,
    currency: form.querySelector('[name="currency"]').value,
};


document.getElementById("inpb1").onclick = function (event) {
    hidePassword(event); // Hide password if another field is clicked
    toggleInput("inp1");
    event.stopPropagation();
};

document.getElementById("inpb5").onclick = function (event) {
    hidePassword(event); // Hide password if another field is clicked
    toggleInput("inp5");
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

    // Function to check if the form has changed
function checkFormChanges() {
    const currentValues = {
            first_name: form.querySelector('[name="first_name"]').value,
            last_name: form.querySelector('[name="last_name"]').value,
            email: form.querySelector('[name="email"]').value,
            password: form.querySelector('[name="password"]').value,
            currency: form.querySelector('[name="currency"]').value,
        };

        // Compare initial values with current values
        const hasChanges = Object.keys(initialValues).some(
            key => initialValues[key] !== currentValues[key]
        );

        // Show or hide the Confirm button based on changes
        if (hasChanges) {
            confirmBtn.style.display = 'block';
        } else {
            confirmBtn.style.display = 'none';
        }
}

    // Add event listeners to form fields
form.querySelectorAll('input, select').forEach(field => {
    field.addEventListener('input', checkFormChanges);
    field.addEventListener('change', checkFormChanges);
});

// Initial check in case the form is pre-filled with changes
checkFormChanges();


// Get the CSRF token from the meta tag
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

document.getElementById('confirmDelete').onclick = function() {
    console.log("Confirm Delete button clicked!"); // Debugging

    // Close the dialog
    const dialog = document.getElementById("deleteButtonDialog");
    dialog.close();

    // Get the delete URL
    const deleteUrl = "/finance/delete-account/";

    // Send a POST request to delete the account
    fetch(deleteUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,  // Use the CSRF token from the meta tag
        },
        body: JSON.stringify({}),  // No data needed in the body
    })
    .then(response => {
        if (response.redirected) {
            // Redirect to the login page after successful deletion
            window.location.href = response.url;
        } else {
            console.error("Failed to delete account:", response.statusText);
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
};
