// Проверка, что приложение открыто в Telegram Web App
if (typeof window.Telegram === 'undefined' || typeof window.Telegram.WebApp === 'undefined') {
    // Перенаправляем на страницу с информацией о том, что приложение доступно только в Telegram
    window.location.href = "https://yourwebsite.com/not-supported"; // Замените на свой URL
} else {
    const tg = window.Telegram.WebApp;
    
    // Проверка, есть ли пользовательская информация в initDataUnsafe
    const user = tg.initDataUnsafe?.user;
    
    if (!user) {
        // Если пользователь не авторизован, перенаправляем на страницу с просьбой авторизоваться
        window.location.href = "https://t.me/oweIt_bot/oweltapp"; // Замените на ваш URL
    } else {
        // Если данные пользователя получены, инициализируем приложение
        console.log('User data:', user);
        const fullName = `${user.first_name || ''} ${user.last_name || ''}`.trim();

        // Отправка данных пользователя на сервер
        fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                telegram_id: user.id,
                name: fullName,
                username: user.username,
                photo_url: user.photo_url
            })
        }).then(response => {
            if (response.ok) {
                console.log('User data saved successfully!');
            } else {
                console.error('Error saving user data.');
            }
        });
    }
}
