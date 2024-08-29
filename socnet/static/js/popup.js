function showPopup(message) {
    const popup = document.getElementById('success-popup');
    const popupMessage = document.getElementById('popup-message');
    if (popup && popupMessage) {
        popupMessage.textContent = message;
        popup.classList.remove('fade-out');
        popup.classList.add('fade-in');
        popup.style.display = 'block';

        setTimeout(() => {
            popup.classList.remove('fade-in');
            popup.classList.add('fade-out');
            setTimeout(() => {
                popup.style.display = 'none';
            }, 500);
        }, 3000);
    }
}