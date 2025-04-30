// Инициализация Telegram WebApp
const tg = window.Telegram.WebApp;
tg.expand(); // Расширяем приложение на весь экран

// Получение данных из Telegram
let user = null;
if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
    user = tg.initDataUnsafe.user;
    document.getElementById('user-info').textContent = `Пользователь: ${user.username || user.first_name}`;
}

// Базовый URL API бота
const API_BASE_URL = window.location.origin + '/api';

// Элементы DOM для аутентификации
const authCard = document.getElementById('auth-card');
const loginInput = document.getElementById('login');
const authBtn = document.getElementById('auth-btn');
const confirmGroup = document.getElementById('confirm-group');
const codeInput = document.getElementById('code');
const confirmBtn = document.getElementById('confirm-btn');

// Элементы DOM для проверки кампуса
const campusCard = document.getElementById('campus-card');
const checkLoginInput = document.getElementById('check-login');
const checkBtn = document.getElementById('check-btn');
const checkAllBtn = document.getElementById('checkall-btn');
const checkResults = document.getElementById('check-results');

// Элементы DOM для друзей
const friendsCard = document.getElementById('friends-card');
const friendLoginInput = document.getElementById('friend-login');
const addFriendBtn = document.getElementById('add-friend-btn');
const removeFriendBtn = document.getElementById('remove-friend-btn');
const listFriendsBtn = document.getElementById('list-friends-btn');
const friendsList = document.getElementById('friends-list');

// Элементы DOM для peer-review
const reviewCard = document.getElementById('review-card');
const reviewLoginInput = document.getElementById('review-login');
const reviewDateInput = document.getElementById('review-date');
const setReviewBtn = document.getElementById('set-review-btn');
const listReviewsBtn = document.getElementById('list-reviews-btn');
const reviewsList = document.getElementById('reviews-list');

// Элементы DOM для статистики
const statsCard = document.getElementById('stats-card');
const myXpBtn = document.getElementById('myxp-btn');
const myLevelBtn = document.getElementById('mylevel-btn');
const myProjectsBtn = document.getElementById('myprojects-btn');
const mySkillsBtn = document.getElementById('myskills-btn');
const myBadgesBtn = document.getElementById('mybadges-btn');
const logTimeBtn = document.getElementById('logtime-btn');
const statsResults = document.getElementById('stats-results');

// Функция для отображения сообщения об ошибке/успехе
function showMessage(element, message, isError = false) {
    element.innerHTML = `<div class="${isError ? 'error' : 'success'}">${message}</div>`;
}

// Проверяем авторизацию пользователя
async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE_URL}/check-auth`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ tg_id: user?.id }),
        });
        
        const data = await response.json();
        
        if (data.authenticated) {
            // Если пользователь авторизован, показываем другие карточки
            authCard.style.display = 'none';
            campusCard.style.display = 'block';
            friendsCard.style.display = 'block';
            reviewCard.style.display = 'block';
            statsCard.style.display = 'block';
        }
    } catch (error) {
        console.error('Ошибка при проверке аутентификации:', error);
    }
}

// Обработчик для кнопки аутентификации
authBtn.addEventListener('click', async () => {
    const login = loginInput.value.trim();
    if (!login) {
        showMessage(authCard, 'Введите логин', true);
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                tg_id: user?.id,
                login: login 
            }),
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage(authCard, 'Код отправлен в Rocket.Chat!');
            confirmGroup.style.display = 'block';
        } else {
            showMessage(authCard, data.message || 'Ошибка при отправке кода', true);
        }
    } catch (error) {
        console.error('Ошибка при авторизации:', error);
        showMessage(authCard, 'Ошибка при авторизации', true);
    }
});

// Обработчик для кнопки подтверждения
confirmBtn.addEventListener('click', async () => {
    const code = codeInput.value.trim();
    if (!code) {
        showMessage(authCard, 'Введите код подтверждения', true);
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/confirm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                tg_id: user?.id,
                code: code 
            }),
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage(authCard, 'Вы успешно авторизованы!');
            // Показываем другие карточки
            setTimeout(() => {
                authCard.style.display = 'none';
                campusCard.style.display = 'block';
                friendsCard.style.display = 'block';
                reviewCard.style.display = 'block';
                statsCard.style.display = 'block';
            }, 1000);
        } else {
            showMessage(authCard, data.message || 'Неверный код подтверждения', true);
        }
    } catch (error) {
        console.error('Ошибка при подтверждении:', error);
        showMessage(authCard, 'Ошибка при подтверждении', true);
    }
});

// Обработчик для кнопки проверки
checkBtn.addEventListener('click', async () => {
    const login = checkLoginInput.value.trim();
    
    try {
        const response = await fetch(`${API_BASE_URL}/check`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                tg_id: user?.id,
                login: login 
            }),
        });
        
        const data = await response.json();
        
        if (data.success) {
            checkResults.innerHTML = data.message;
        } else {
            showMessage(checkResults, data.message || 'Ошибка при проверке', true);
        }
    } catch (error) {
        console.error('Ошибка при проверке:', error);
        showMessage(checkResults, 'Ошибка при проверке', true);
    }
});

// Обработчик для кнопки проверки всех друзей
checkAllBtn.addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/checkall`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ tg_id: user?.id }),
        });
        
        const data = await response.json();
        
        if (data.success) {
            checkResults.innerHTML = data.message;
        } else {
            showMessage(checkResults, data.message || 'Ошибка при проверке друзей', true);
        }
    } catch (error) {
        console.error('Ошибка при проверке друзей:', error);
        showMessage(checkResults, 'Ошибка при проверке друзей', true);
    }
});

// Обработчик для кнопки добавления друга
addFriendBtn.addEventListener('click', async () => {
    const login = friendLoginInput.value.trim();
    if (!login) {
        showMessage(friendsList, 'Введите логин друга', true);
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/addfriend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                tg_id: user?.id,
                login: login 
            }),
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage(friendsList, 'Друг успешно добавлен!');
            friendLoginInput.value = '';
        } else {
            showMessage(friendsList, data.message || 'Ошибка при добавлении друга', true);
        }
    } catch (error) {
        console.error('Ошибка при добавлении друга:', error);
        showMessage(friendsList, 'Ошибка при добавлении друга', true);
    }
});

// Обработчик для кнопки удаления друга
removeFriendBtn.addEventListener('click', async () => {
    const login = friendLoginInput.value.trim();
    if (!login) {
        showMessage(friendsList, 'Введите логин друга', true);
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/removefriend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                tg_id: user?.id,
                login: login 
            }),
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage(friendsList, 'Друг успешно удален!');
            friendLoginInput.value = '';
        } else {
            showMessage(friendsList, data.message || 'Ошибка при удалении друга', true);
        }
    } catch (error) {
        console.error('Ошибка при удалении друга:', error);
        showMessage(friendsList, 'Ошибка при удалении друга', true);
    }
});

// Обработчик для кнопки списка друзей
listFriendsBtn.addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/listfriends`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ tg_id: user?.id }),
        });
        
        const data = await response.json();
        
        if (data.success) {
            friendsList.innerHTML = data.message;
        } else {
            showMessage(friendsList, data.message || 'Ошибка при получении списка друзей', true);
        }
    } catch (error) {
        console.error('Ошибка при получении списка друзей:', error);
        showMessage(friendsList, 'Ошибка при получении списка друзей', true);
    }
});

// Обработчик для кнопки установки peer-review
setReviewBtn.addEventListener('click', async () => {
    const login = reviewLoginInput.value.trim();
    const date = reviewDateInput.value;
    
    if (!login || !date) {
        showMessage(reviewsList, 'Введите логин и дату', true);
        return;
    }
    
    try {
        const isoDate = new Date(date).toISOString().split('.')[0];
        
        const response = await fetch(`${API_BASE_URL}/setreview`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                tg_id: user?.id,
                login: login,
                date: isoDate
            }),
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage(reviewsList, 'Peer-review успешно запланирован!');
            reviewLoginInput.value = '';
            reviewDateInput.value = '';
        } else {
            showMessage(reviewsList, data.message || 'Ошибка при планировании peer-review', true);
        }
    } catch (error) {
        console.error('Ошибка при планировании peer-review:', error);
        showMessage(reviewsList, 'Ошибка при планировании peer-review', true);
    }
});

// Обработчик для кнопки списка peer-review
listReviewsBtn.addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/listreviews`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ tg_id: user?.id }),
        });
        
        const data = await response.json();
        
        if (data.success) {
            reviewsList.innerHTML = data.message;
        } else {
            showMessage(reviewsList, data.message || 'Ошибка при получении списка peer-review', true);
        }
    } catch (error) {
        console.error('Ошибка при получении списка peer-review:', error);
        showMessage(reviewsList, 'Ошибка при получении списка peer-review', true);
    }
});

// Обработчики для кнопок статистики
myXpBtn.addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/myxp`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ tg_id: user?.id }),
        });
        
        const data = await response.json();
        
        if (data.success) {
            statsResults.innerHTML = data.message;
        } else {
            showMessage(statsResults, data.message || 'Ошибка при получении XP', true);
        }
    } catch (error) {
        console.error('Ошибка при получении XP:', error);
        showMessage(statsResults, 'Ошибка при получении XP', true);
    }
});

myLevelBtn.addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/mylevel`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ tg_id: user?.id }),
        });
        
        const data = await response.json();
        
        if (data.success) {
            statsResults.innerHTML = data.message;
        } else {
            showMessage(statsResults, data.message || 'Ошибка при получении уровня', true);
        }
    } catch (error) {
        console.error('Ошибка при получении уровня:', error);
        showMessage(statsResults, 'Ошибка при получении уровня', true);
    }
});

myProjectsBtn.addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/myprojects`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ tg_id: user?.id }),
        });
        
        const data = await response.json();
        
        if (data.success) {
            statsResults.innerHTML = data.message;
        } else {
            showMessage(statsResults, data.message || 'Ошибка при получении проектов', true);
        }
    } catch (error) {
        console.error('Ошибка при получении проектов:', error);
        showMessage(statsResults, 'Ошибка при получении проектов', true);
    }
});

mySkillsBtn.addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/myskills`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ tg_id: user?.id }),
        });
        
        const data = await response.json();
        
        if (data.success) {
            statsResults.innerHTML = data.message;
        } else {
            showMessage(statsResults, data.message || 'Ошибка при получении навыков', true);
        }
    } catch (error) {
        console.error('Ошибка при получении навыков:', error);
        showMessage(statsResults, 'Ошибка при получении навыков', true);
    }
});

myBadgesBtn.addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/mybadges`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ tg_id: user?.id }),
        });
        
        const data = await response.json();
        
        if (data.success) {
            statsResults.innerHTML = data.message;
        } else {
            showMessage(statsResults, data.message || 'Ошибка при получении значков', true);
        }
    } catch (error) {
        console.error('Ошибка при получении значков:', error);
        showMessage(statsResults, 'Ошибка при получении значков', true);
    }
});

logTimeBtn.addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/logtime`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ tg_id: user?.id }),
        });
        
        const data = await response.json();
        
        if (data.success) {
            statsResults.innerHTML = data.message;
        } else {
            showMessage(statsResults, data.message || 'Ошибка при получении времени', true);
        }
    } catch (error) {
        console.error('Ошибка при получении времени:', error);
        showMessage(statsResults, 'Ошибка при получении времени', true);
    }
});

// При загрузке страницы проверяем авторизацию пользователя
document.addEventListener('DOMContentLoaded', () => {
    if (user) {
        checkAuth();
    }
});
