
function showAjaxPopup(message) {
    const popup = document.getElementById('ajax-popup');
    const popupMessage = document.getElementById('ajax-popup-message');

    if (popup && popupMessage) {
        popupMessage.textContent = message;
        popup.style.display = 'block'; // Показываем окно

        setTimeout(() => {
            popup.style.opacity = 1; // Показать плавно
            setTimeout(() => {
                popup.style.opacity = 0; // Скрыть плавно
                setTimeout(() => {
                    popup.style.display = 'none'; // Прячем полностью
                }, 500);
            }, 5000);
        }, 100);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const djangoMessagesContainer = document.getElementById('django-messages');
    if (djangoMessagesContainer) {
        const messages = djangoMessagesContainer.querySelectorAll('.alert');
        messages.forEach(function(messageElement) {
            const message = messageElement.textContent.trim();
            if (message) {
                showAjaxPopup(message);

                // Удаляем сообщение из DOM
                messageElement.remove();

                // Сброс страницы после показа сообщения
                setTimeout(() => {
                    popup.style.display = 'none'; // Прячем полностью
                }, 5000);
            }
        });
    }

    // Закрытие всплывающего окна
    const closeAjaxButton = document.getElementById('close-ajax-popup');
    if (closeAjaxButton) {
        closeAjaxButton.addEventListener('click', function() {
            const popup = document.getElementById('ajax-popup');
            if (popup) {
                popup.style.opacity = 0;
                setTimeout(() => {
                    popup.style.display = 'none';
                }, 500);
            }
        });
    }
});