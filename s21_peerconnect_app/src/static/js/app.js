// static/js/app.js
const API_BASE_URL = `${window.location.origin}/api`; 
const S21_API_BASE_URL = `${window.location.origin}/s21_api`; 
const PR_API_BASE_URL = `${window.location.origin}/api/pr`; // Peer Review API

document.addEventListener("DOMContentLoaded", () => {
    const mainContent = document.getElementById("app-root");
    const navLinks = document.getElementById("nav-links");
    let currentCalendarDate = new Date(2025, 4, 1); // May 2025 for consistency

    function router() {
        const hash = window.location.hash || "#dashboard"; 
        mainContent.innerHTML = ""; 

        const accessToken = localStorage.getItem("accessToken");
        updateNav(accessToken);

        if (!accessToken && hash !== "#login") {
            window.location.hash = "#login"; 
            return; 
        }

        switch (hash) {
            case "#login":
                if (accessToken) { 
                    window.location.hash = "#dashboard";
                    return;
                }
                renderLoginPage(mainContent);
                break;
            case "#dashboard":
                renderDashboardPage(mainContent);
                break;
            case "#profile":
                renderProfilePage(mainContent);
                break;
            case "#calendar":
                renderCalendarPage(mainContent);
                break;
            case "#notifications": // New route
                renderNotificationsPage(mainContent);
                break;
            case "#friends": // New route
                renderFriendsPage(mainContent);
                break;
            case "#settings": // New route
                renderSettingsPage(mainContent);
                break;
            case "#logout":
                logout();
                break;
            default:
                mainContent.innerHTML = "<h2>Страница не найдена</h2>";
        }
    }

    function updateNav(isLoggedIn) {
        const loginLink = navLinks.querySelector("a[href=\"#login\"]");
        const logoutLink = navLinks.querySelector("a[href=\"#logout\"]");
        const dashboardLink = navLinks.querySelector("a[href=\"#dashboard\"]");
        const profileLink = navLinks.querySelector("a[href=\"#profile\"]");
        const calendarLink = navLinks.querySelector("a[href=\"#calendar\"]");
        // Add new nav links selectors here if they exist in index.html
        const notificationsLink = navLinks.querySelector("a[href=\"#notifications\"]");
        const friendsLink = navLinks.querySelector("a[href=\"#friends\"]");
        const settingsLink = navLinks.querySelector("a[href=\"#settings\"]");

        if (isLoggedIn) {
            if (loginLink) loginLink.parentElement.style.display = "none";
            if (logoutLink) logoutLink.parentElement.style.display = "list-item";
            if (dashboardLink) dashboardLink.parentElement.style.display = "list-item";
            if (profileLink) profileLink.parentElement.style.display = "list-item";
            if (calendarLink) calendarLink.parentElement.style.display = "list-item";
            if (notificationsLink) notificationsLink.parentElement.style.display = "list-item";
            if (friendsLink) friendsLink.parentElement.style.display = "list-item";
            if (settingsLink) settingsLink.parentElement.style.display = "list-item";
        } else {
            if (loginLink) loginLink.parentElement.style.display = "list-item";
            if (logoutLink) logoutLink.parentElement.style.display = "none";
            if (dashboardLink) dashboardLink.parentElement.style.display = "none";
            if (profileLink) profileLink.parentElement.style.display = "none";
            if (calendarLink) calendarLink.parentElement.style.display = "none";
            if (notificationsLink) notificationsLink.parentElement.style.display = "none";
            if (friendsLink) friendsLink.parentElement.style.display = "none";
            if (settingsLink) settingsLink.parentElement.style.display = "none";
        }
    }

    function renderLoginPage(container) {
        // ... (login page code remains the same)
        container.innerHTML = `
            <div class="login-container">
                <h2>Вход в S21 PeerConnect</h2>
                <div id="error-message-login" class="error-message" style="display:none;"></div>
                <form id="login-form">
                    <div class="form-group">
                        <label for="username">Логин Школы 21:</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Пароль:</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit" class="btn">Войти</button>
                </form>
            </div>
        `;

        const loginForm = document.getElementById("login-form");
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const username = loginForm.username.value;
            const password = loginForm.password.value;
            const errorDiv = document.getElementById("error-message-login");
            errorDiv.style.display = "none"; errorDiv.textContent = "";
            try {
                const response = await fetch(`${API_BASE_URL}/auth/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, password }),
                });
                const data = await response.json();
                if (response.ok) {
                    localStorage.setItem("accessToken", data.access_token);
                    localStorage.setItem("userLogin", data.user_school21_login);
                    window.location.hash = "#dashboard";
                } else {
                    errorDiv.textContent = data.error || data.details || "Ошибка входа.";
                    errorDiv.style.display = "block";
                }
            } catch (error) {
                console.error("Login error:", error);
                errorDiv.textContent = "Сетевая ошибка.";
                errorDiv.style.display = "block";
            }
        });
    }

    function renderDashboardPage(container) {
        // ... (dashboard page code remains the same)
        const userLogin = localStorage.getItem("userLogin");
        container.innerHTML = `
            <h2>Панель управления</h2>
            <p>Добро пожаловать, ${userLogin || "Пользователь"}!</p>
            <p>Здесь будет основная информация и быстрые ссылки.</p>
            <p><a href="#calendar">Календарь ревью</a></p>
            <p><a href="#profile">Мой профиль</a></p>
            <p><a href="#notifications">Уведомления</a></p>
            <p><a href="#friends">Друзья/Пиры</a></p>
            <p><a href="#settings">Настройки</a></p>
        `;
    }

    async function renderProfilePage(container) {
        // ... (profile page code remains the same)
        const userLogin = localStorage.getItem("userLogin");
        if (!userLogin) {
            container.innerHTML = "<p>Ошибка: пользователь не найден.</p>";
            return;
        }
        container.innerHTML = "<h2>Мой профиль</h2><div id=\"profile-data-container\"><p>Загрузка...</p></div>";
        const profileDataContainer = document.getElementById("profile-data-container");
        try {
            const meResponse = await fetch(`${S21_API_BASE_URL}/me?user_login=${userLogin}`);
            const meData = await meResponse.json();
            if (!meResponse.ok) throw new Error(meData.details || meData.error || "Failed to load profile");
            const pointsResponse = await fetch(`${S21_API_BASE_URL}/mypoints?user_login=${userLogin}`);
            const pointsData = await pointsResponse.json();
            if (!pointsResponse.ok) throw new Error(pointsData.details || pointsData.error || "Failed to load XP");
            const projectsResponse = await fetch(`${S21_API_BASE_URL}/myprojects?user_login=${userLogin}&limit=50`);
            const projectsData = await projectsResponse.json();
            if (!projectsResponse.ok) throw new Error(projectsData.details || projectsData.error || "Failed to load projects");
            let projectsHTML = "<p>Нет проектов.</p>";
            if (projectsData && projectsData.data && projectsData.data.length > 0) {
                projectsHTML = "<ul>" + projectsData.data.map(p => `<li>${p.project.name} - Статус: ${p.status} (${p.finalMark !== null ? p.finalMark + ", " : ""} Попытка: ${p.occurrence})</li>`).join("") + "</ul>";
            }
            profileDataContainer.innerHTML = `
                <p><strong>Логин:</strong> ${meData.login || "N/A"}</p>
                <p><strong>Email:</strong> ${meData.email || "N/A"}</p>
                <p><strong>Имя:</strong> ${meData.firstName || ""} ${meData.lastName || ""}</p>
                <p><strong>Уровень:</strong> ${meData.level !== undefined ? meData.level : "N/A"}</p>
                <p><strong>XP:</strong> ${pointsData.totalXp !== undefined ? pointsData.totalXp : "N/A"}</p>
                <h3>Мои проекты:</h3>${projectsHTML}
            `;
        } catch (error) {
            console.error("Profile fetch error:", error);
            profileDataContainer.innerHTML = `<p class="error-message">Не удалось загрузить профиль: ${error.message}</p>`;
        }
    }

    async function renderCalendarPage(container) {
        // ... (calendar page code remains largely the same)
        const userLogin = localStorage.getItem("userLogin");
        container.innerHTML = `
            <h2>Календарь Peer Review</h2>
            <div id="slot-creation-form-container">
                <h3>Создать новый слот</h3>
                <form id="create-slot-form">
                    <div class="form-group">
                        <label for="slot-start-time">Время начала (YYYY-MM-DDTHH:MM):</label>
                        <input type="datetime-local" id="slot-start-time" required>
                    </div>
                    <div class="form-group">
                        <label for="slot-end-time">Время окончания (YYYY-MM-DDTHH:MM):</label>
                        <input type="datetime-local" id="slot-end-time" required>
                    </div>
                    <div class="form-group">
                        <label for="slot-project-name">Проект (необязательно):</label>
                        <input type="text" id="slot-project-name">
                    </div>
                    <button type="submit" class="btn">Создать слот</button>
                    <div id="error-message-slot-create" class="error-message" style="display:none;"></div>
                </form>
            </div>
            <div class="calendar-container">
                <div class="calendar-header">
                    <button id="prev-month">‹ Пред.</button>
                    <h3 id="month-year"></h3>
                    <button id="next-month">След. ›</button>
                </div>
                <div class="calendar-grid-header">
                    ${["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"].map(day => `<div class="calendar-day-header">${day}</div>`).join("")}
                </div>
                <div class="calendar-grid" id="calendar-grid-main"></div>
            </div>
            <div id="slot-details-modal" class="modal" style="display:none;">
                <div class="modal-content">
                    <span class="close-button">&times;</span>
                    <h4>Детали слота</h4>
                    <p id="modal-slot-creator"></p>
                    <p id="modal-slot-time"></p>
                    <p id="modal-slot-project"></p>
                    <p id="modal-slot-status"></p>
                    <button id="modal-book-button" class="btn" style="display:none;">Записаться</button>
                    <button id="modal-cancel-button" class="btn btn-danger" style="display:none;">Отменить слот</button>
                    <div id="error-message-slot-action" class="error-message" style="display:none;"></div>
                </div>
            </div>
        `;
        const monthYearEl = document.getElementById("month-year");
        const calendarGridEl = document.getElementById("calendar-grid-main");
        await displayCalendar(currentCalendarDate, calendarGridEl, monthYearEl, userLogin);
        document.getElementById("prev-month").addEventListener("click", async () => {
            currentCalendarDate.setMonth(currentCalendarDate.getMonth() - 1);
            await displayCalendar(currentCalendarDate, calendarGridEl, monthYearEl, userLogin);
        });
        document.getElementById("next-month").addEventListener("click", async () => {
            currentCalendarDate.setMonth(currentCalendarDate.getMonth() + 1);
            await displayCalendar(currentCalendarDate, calendarGridEl, monthYearEl, userLogin);
        });
        const createSlotForm = document.getElementById("create-slot-form");
        createSlotForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const startTime = document.getElementById("slot-start-time").value;
            const endTime = document.getElementById("slot-end-time").value;
            const projectName = document.getElementById("slot-project-name").value;
            const errorDiv = document.getElementById("error-message-slot-create");
            errorDiv.style.display = "none"; errorDiv.textContent = "";
            try {
                const response = await fetch(`${PR_API_BASE_URL}/slots?user_login=${userLogin}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ start_time: startTime, end_time: endTime, project_name: projectName }),
                });
                const data = await response.json();
                if (response.ok) {
                    alert("Слот успешно создан!");
                    createSlotForm.reset();
                    await displayCalendar(currentCalendarDate, calendarGridEl, monthYearEl, userLogin);
                } else {
                    errorDiv.textContent = data.error || "Ошибка создания слота.";
                    errorDiv.style.display = "block";
                }
            } catch (error) {
                console.error("Slot creation error:", error);
                errorDiv.textContent = "Сетевая ошибка при создании слота.";
                errorDiv.style.display = "block";
            }
        });
        const modal = document.getElementById("slot-details-modal");
        const closeButton = modal.querySelector(".close-button");
        closeButton.onclick = function() { modal.style.display = "none"; }
        window.onclick = function(event) { if (event.target == modal) { modal.style.display = "none"; } }
    }

    async function displayCalendar(date, gridEl, monthYearEl, currentUserLogin) {
        // ... (displayCalendar logic remains the same)
        gridEl.innerHTML = "";
        const year = date.getFullYear();
        const month = date.getMonth(); 
        monthYearEl.textContent = `${date.toLocaleString("ru-RU", { month: "long" })} ${year}`;
        const firstDayOfMonth = new Date(year, month, 1);
        const lastDayOfMonth = new Date(year, month + 1, 0);
        const daysInMonth = lastDayOfMonth.getDate();
        let startingDayOfWeek = (firstDayOfMonth.getDay() + 6) % 7; 
        for (let i = 0; i < startingDayOfWeek; i++) {
            gridEl.insertAdjacentHTML("beforeend", `<div class="calendar-day empty"></div>`);
        }
        let slotsForMonth = [];
        try {
            const response = await fetch(`${PR_API_BASE_URL}/slots?month=${year}-${String(month + 1).padStart(2, '0')}&user_login=${currentUserLogin}`);
            if (response.ok) { slotsForMonth = await response.json(); }
            else { console.error("Failed to fetch slots for month"); }
        } catch (error) { console.error("Error fetching slots:", error); }
        for (let day = 1; day <= daysInMonth; day++) {
            const dayCell = document.createElement("div");
            dayCell.classList.add("calendar-day");
            dayCell.innerHTML = `<span class="day-number">${day}</span>`;
            const today = new Date();
            if (year === today.getFullYear() && month === today.getMonth() && day === today.getDate()) {
                dayCell.classList.add("today");
            }
            const slotsContainer = document.createElement("div");
            slotsContainer.classList.add("slots-in-day");
            const currentDateISONoTime = new Date(year, month, day).toISOString().split('T')[0];
            slotsForMonth.forEach(slot => {
                const slotStartDate = new Date(slot.start_time);
                if (slotStartDate.toISOString().split('T')[0] === currentDateISONoTime) {
                    const slotEl = document.createElement("div");
                    slotEl.classList.add("calendar-slot", `slot-status-${slot.status}`);
                    slotEl.textContent = `${new Date(slot.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} (${slot.creator_user_login})`;
                    slotEl.dataset.slotId = slot.id;
                    slotEl.addEventListener("click", () => showSlotDetails(slot, currentUserLogin));
                    slotsContainer.appendChild(slotEl);
                }
            });
            dayCell.appendChild(slotsContainer);
            gridEl.appendChild(dayCell);
        }
    }

    async function showSlotDetails(slot, currentUserLogin) {
        // ... (showSlotDetails logic remains the same)
        const modal = document.getElementById("slot-details-modal");
        document.getElementById("modal-slot-creator").textContent = `Создатель: ${slot.creator_user_login}`;
        document.getElementById("modal-slot-time").textContent = `Время: ${new Date(slot.start_time).toLocaleString()} - ${new Date(slot.end_time).toLocaleString()}`;
        document.getElementById("modal-slot-project").textContent = `Проект: ${slot.project_name || "Не указан"}`;
        document.getElementById("modal-slot-status").textContent = `Статус: ${slot.status}`;
        const bookButton = document.getElementById("modal-book-button");
        const cancelButton = document.getElementById("modal-cancel-button");
        const errorDiv = document.getElementById("error-message-slot-action");
        errorDiv.style.display = "none"; errorDiv.textContent = "";
        bookButton.style.display = "none"; cancelButton.style.display = "none";
        bookButton.onclick = null; cancelButton.onclick = null;
        if (slot.status === "available" && slot.creator_user_login !== currentUserLogin) {
            bookButton.style.display = "block";
            bookButton.onclick = async () => {
                try {
                    const response = await fetch(`${PR_API_BASE_URL}/slots/${slot.id}/book?user_login=${currentUserLogin}`, { method: "POST" });
                    const data = await response.json();
                    if (response.ok) {
                        alert("Слот успешно забронирован!");
                        modal.style.display = "none";
                        await displayCalendar(currentCalendarDate, document.getElementById("calendar-grid-main"), document.getElementById("month-year"), currentUserLogin);
                    } else { errorDiv.textContent = data.error || "Ошибка бронирования."; errorDiv.style.display = "block"; }
                } catch (err) { errorDiv.textContent = "Сетевая ошибка."; errorDiv.style.display = "block"; }
            };
        }
        if (slot.status !== "cancelled" && slot.status !== "completed" && (slot.creator_user_login === currentUserLogin || (slot.status === "booked" && slot.booker_user_login === currentUserLogin))) {
            cancelButton.style.display = "block";
            cancelButton.onclick = async () => {
                if (!confirm("Вы уверены, что хотите отменить этот слот?")) return;
                try {
                    const response = await fetch(`${PR_API_BASE_URL}/slots/${slot.id}/cancel?user_login=${currentUserLogin}`, { method: "POST" });
                    const data = await response.json();
                    if (response.ok) {
                        alert("Слот отменен.");
                        modal.style.display = "none";
                        await displayCalendar(currentCalendarDate, document.getElementById("calendar-grid-main"), document.getElementById("month-year"), currentUserLogin);
                    } else { errorDiv.textContent = data.error || "Ошибка отмены."; errorDiv.style.display = "block"; }
                } catch (err) { errorDiv.textContent = "Сетевая ошибка."; errorDiv.style.display = "block"; }
            };
        }
        modal.style.display = "block";
    }

    function renderNotificationsPage(container) {
        container.innerHTML = `
            <h2>Уведомления</h2>
            <p>Здесь будут отображаться уведомления о статусе ваших peer review, новых слотах и т.д.</p>
            <p><em>(Функционал в разработке)</em></p>
        `;
    }

    function renderFriendsPage(container) {
        container.innerHTML = `
            <h2>Друзья/Пиры</h2>
            <p>Здесь можно будет управлять списком друзей/пиров, видеть их доступность для ревью и т.д.</p>
            <p>Команды бота (<code>/addfriend</code>, <code>/removefriend</code>, <code>/listfriends</code>) будут интегрированы здесь.</p>
            <p><em>(Функционал в разработке)</em></p>
        `;
    }

    function renderSettingsPage(container) {
        container.innerHTML = `
            <h2>Настройки</h2>
            <p>Здесь можно будет настроить уведомления, привязать/отвязать Telegram аккаунт и другие параметры.</p>
            <p><em>(Функционал в разработке)</em></p>
        `;
    }

    function logout() {
        localStorage.removeItem("accessToken");
        localStorage.removeItem("userLogin");
        window.location.hash = "#login";
    }

    router();
    window.addEventListener("hashchange", router);
});

