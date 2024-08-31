// Функция для отображения Django сообщений
function showDjangoPopup(message) {
    const popup = document.getElementById('django-popup');
    const popupMessage = document.getElementById('django-popup-message');
    
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
            }, 3000);
        }, 100);
    }
}

// Функция для отображения AJAX сообщений
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
            }, 3000);
        }, 100);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const closeDjangoButton = document.getElementById('close-django-popup');
    if (closeDjangoButton) {
        closeDjangoButton.addEventListener('click', function() {
            const popup = document.getElementById('django-popup');
            if (popup) {
                popup.style.opacity = 0;
                setTimeout(() => {
                    popup.style.display = 'none';
                }, 500);
            }
        });
    }

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
