document.addEventListener("DOMContentLoaded", function() {
    hideLoadingAnimation(); // Ensure the loading animation is hidden on page load
    loadQuestionBubbles(); // Load predefined question bubbles from the server
    closeContactModal();
});

document.getElementById('send-btn').addEventListener('click', function() {
    sendMessage();
});

function sendMessage() {
    let question = document.getElementById('question-input').value;

    if (question) {
        appendUserMessage(question);
        document.getElementById('question-input').value = '';  // Clear the input field
        showLoadingAnimation();  // Show loading animation

        // Send request to Flask server
        fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: question }),
        })
        .then(response => response.json())
        .then(data => {
            hideLoadingAnimation();  // Hide loading animation
            if (data.answer.toLowerCase().includes('contact')) {
                appendBotMessage("Do you wish to contact us?", true); // Show question with buttons
            } else if (data.answer.includes('|')) { // Check for tabular data
                appendBotMessage(buildTable(data.answer));
            } else {
                appendBotMessage(data.answer);
            }
        })
        .catch(error => {
            hideLoadingAnimation();  // Hide loading animation on error
            appendBotMessage("Sorry, something went wrong.");
        });
    }
}

function showLoadingAnimation() {
    document.getElementById('loading-container').classList.remove('hidden');
}

function hideLoadingAnimation() {
    document.getElementById('loading-container').classList.add('hidden');
}

function appendUserMessage(message) {
    const chatBox = document.getElementById('chat-box');

    // Create message container div
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message-container user-message';

    // Create profile image element
    const userImage = document.createElement('img');
    userImage.src = '/static/images/user.png';  // Path to user profile image
    userImage.alt = 'User';
    userImage.className = 'profile-bubble';

    // Create message content div
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.innerHTML = message;

    // Append the message content and image to the message container
    messageDiv.appendChild(messageContent); // Message first
    messageDiv.appendChild(userImage);      // Image after message

    // Append the message container to the chatBox
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;  // Scroll to the bottom
}

function appendBotMessage(message, isContactQuestion = false) {
    const chatBox = document.getElementById('chat-box');

    // Create message container
    const messageContainer = document.createElement('div');
    messageContainer.className = 'message-container bot-message';  // Ensure flex-start alignment

    // Create bot profile image (should appear on the left)
    const profileImg = document.createElement('img');
    profileImg.src = '/static/images/bot.png';  // Path to bot image
    profileImg.alt = 'Bot';
    profileImg.className = 'profile-bubble';

    // Create the bot label and message container
    const botLabel = document.createElement('strong');
    botLabel.className = 'bot-label';
    botLabel.textContent = 'MSI: ';

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message-content';
    messageDiv.innerHTML = message;

    // Append profile image, bot label, and message content
    messageContainer.appendChild(profileImg);  // Profile image first
    messageContainer.appendChild(botLabel);    // "Bot:" label
    messageContainer.appendChild(messageDiv);  // Bot message content

    // If it's a contact question, add Yes/No buttons
    if (isContactQuestion) {
        const buttonContainer = document.createElement('div');

        const yesButton = document.createElement('button');
        yesButton.className = 'question-btn';
        yesButton.textContent = 'Yes';
        yesButton.onclick = showContactModal;

        const noButton = document.createElement('button');
        noButton.className = 'question-btn';
        noButton.textContent = 'No';
        noButton.onclick = () => {
            buttonContainer.remove();  // Remove buttons when "No" is clicked
        };

        buttonContainer.appendChild(yesButton);
        buttonContainer.appendChild(noButton);
        messageDiv.appendChild(buttonContainer);
    }

    chatBox.appendChild(messageContainer);
    chatBox.scrollTop = chatBox.scrollHeight;  // Scroll to the bottom
}












function askPredefinedQuestion(question) {
    document.getElementById('question-input').value = question;
    sendMessage();
}

function buildTable(data) {
    const rows = data.split('\n');
    let table = '<table>';
    rows.forEach(row => {
        const cols = row.split('|');
        table += '<tr>';
        cols.forEach(col => {
            table += `<td>${col.trim()}</td>`;
        });
        table += '</tr>';
    });
    table += '</table>';
    return table;
}

// Update loadQuestionBubbles function to include the contact question
function loadQuestionBubbles() {
    fetch('/get_predefined_questions')
        .then(response => response.json())
        .then(questions => {
            const questionBubbles = document.getElementById('question-bubbles');
            questions.forEach(question => {
                const button = document.createElement('button');
                button.className = 'question-btn';
                button.textContent = question;
                button.onclick = () => {
                    if (question.toLowerCase() === 'contact') {
                        showContactModal();
                    } else {
                        askPredefinedQuestion(question);
                    }
                };
                questionBubbles.appendChild(button);
            });
        })
        .catch(error => console.error('Error fetching predefined questions:', error));
}

function showContactModal() {
    document.getElementById('contact-form').classList.remove('hidden');
    document.getElementById('overlay').style.display = 'block'; // Show the overlay
    document.getElementById('question-input').disabled = true; // Disable input
}

function hideContactForm() {
    document.getElementById('contact-form').classList.add('hidden');
    document.getElementById('overlay').style.display = 'none'; // Hide the overlay
    document.getElementById('question-input').disabled = false; // Enable input
}


// Optional: Handle form submission
function sendContactForm(event) {
    event.preventDefault(); // Prevent the form from submitting traditionally

    const name = document.getElementById('name').value;
    const phone = document.getElementById('phone').value;
    const message = document.getElementById('message').value;

    // Send contact details to the server
    fetch('/contact', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: name, phone: phone, message: message }),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message); // Log the server response
        hideContactForm(); // Hide the contact form after submission
    })
    .catch(error => {
        console.error('Error sending contact details:', error);
    });
}


document.getElementById('contact-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission behavior

    // Get the form data
    const formData = new FormData(this); // 'this' refers to the contact form

    // Example: Convert form data to a JSON object (optional, based on your needs)
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
    });

    // Here you can add your logic to send the data to the server
    // For example, using fetch to submit the form data:
    fetch('/submit_contact_form', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => {
        if (response.ok) {
            // Optionally handle a successful response
            console.log('Form submitted successfully!');
        } else {
            // Handle errors
            console.error('Error submitting form:', response.statusText);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });

    // Hide the contact form and overlay after submission
    hideContactForm(); // Hide form and overlay
});


// Handle contact form submission
document.getElementById('contact-form').addEventListener('submit', function(event) {
    event.preventDefault();
    // Handle form submission logic (e.g., sending data to the server)
    closeContactModal();
});
