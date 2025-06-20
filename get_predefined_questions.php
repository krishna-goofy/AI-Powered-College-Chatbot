<?php
header('Content-Type: application/json');

// Array of predefined questions
$questions = [
    "What is the admission process?",
    "What courses do you offer?",
    "Where is the campus located?",
    "How to apply for scholarships?",
    "What is the fee structure?"
];

// Return the questions as JSON
echo json_encode($questions);
?>
