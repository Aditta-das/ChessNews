function showStatus(message, type) {
    const alertBox = document.getElementById('puzzle-status');
    alertBox.classList.remove('d-none');
    $puzzleStatus.text(message).removeClass("correct wrong info solved").addClass(type || "");
}