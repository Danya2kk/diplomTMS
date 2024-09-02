$(document).ready(function() {
    // Функция для показа всплывающего окна с сообщением
    function showPopup(message, popupId) {
        const popup = document.getElementById(popupId);
        const popupMessage = popup.querySelector('.popup-message');
        if (popup && popupMessage) {
            popupMessage.textContent = message;
            popup.style.display = 'block';
            popup.classList.remove('fade-out');
            popup.classList.add('fade-in');

            // Скрыть сообщение через 3 секунды
            setTimeout(() => {
                popup.classList.remove('fade-in');
                popup.classList.add('fade-out');
                setTimeout(() => {
                    popup.style.display = 'none';
                }, 500); // Задержка для анимации исчезновения
            }, 3000); // Задержка до начала исчезновения
        }
    }

    // Проверяем наличие сообщений из Django
    $('#django-messages .alert').each(function() {
        // Показываем сообщение
        showPopup($(this).text(), 'success-popup');

        // Удаляем сообщение из DOM через 3 секунды (для улучшения производительности)
        setTimeout(() => {
            $(this).remove();
        }, 3000); // Убедитесь, что это значение совпадает с задержкой в showPopup
    });

    // Закрытие всплывающего окна
    $('#close-popup').click(function() {
        $('#success-popup').fadeOut();
    });

    $('#close-ajax-popup').click(function() {
        $('#ajax-popup').fadeOut();
    });
});
