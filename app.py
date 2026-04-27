# GitHub User Finder - приложение для поиска пользователей GitHub

# ----- 1. Подключаем нужные библиотеки -----
import tkinter as tk  # Для создания окошек и кнопок
from tkinter import ttk, messagebox  # Для стильных кнопок и сообщений
import requests  # Для запросов к сайту GitHub
import json  # Для сохранения избранного
import os  # Для проверки существования файлов

# ----- 2. Настройки программы -----
FAVORITES_FILE = "favorites.json"  # Файл, где хранятся любимые пользователи
GITHUB_API = "https://api.github.com/users/"  # Адрес для поиска на GitHub

# ----- 3. Главный класс программы -----
class GitHubUserFinder:
    def __init__(self, root):
        """Этот код создаёт всё, что ты видишь в окне программы"""
        self.root = root
        self.root.title("GitHub User Finder")  # Заголовок окна
        self.root.geometry("650x600")  # Размер окна (ширина x высота)
        self.root.resizable(False, False)  # Запрещаем менять размер окна
        
        # Загружаем сохранённых пользователей из файла
        self.favorites = self.load_favorites()
        
        # --- Создаём поле для ввода ---
        label = tk.Label(root, text="Введите имя пользователя GitHub:", 
                        font=("Arial", 12, "bold"))
        label.pack(pady=10)  # pady - отступ сверху и снизу
        
        self.search_entry = tk.Entry(root, width=40, font=("Arial", 11))
        self.search_entry.pack(pady=5)
        self.search_entry.bind("<Return>", lambda x: self.search_user())  # Поиск по Enter
        
        # --- Кнопка поиска ---
        self.search_btn = tk.Button(root, text="[??] НАЙТИ", 
                                   command=self.search_user,
                                   bg="#2c3e50", fg="white",
                                   font=("Arial", 10, "bold"),
                                   padx=20, pady=5)
        self.search_btn.pack(pady=10)
        
        # --- Рамка для результатов ---
        self.results_frame = tk.LabelFrame(root, text="[??] Информация о пользователе", 
                                          font=("Arial", 10, "bold"),
                                          padx=10, pady=10)
        self.results_frame.pack(fill="both", padx=10, pady=10, expand=True)
        
        self.info_text = tk.Text(self.results_frame, height=10, width=60,
                                font=("Arial", 10), wrap=tk.WORD)
        self.info_text.pack()
        
        # --- Кнопка добавления в избранное ---
        self.fav_btn = tk.Button(root, text="[??] ДОБАВИТЬ В ИЗБРАННОЕ", 
                                command=self.add_to_favorites,
                                bg="#e67e22", fg="white",
                                font=("Arial", 10, "bold"))
        self.fav_btn.pack(pady=5)
        self.fav_btn.pack_forget()  # Скрываем кнопку до первого поиска
        
        # --- Список избранного ---
        tk.Label(root, text="[?] ИЗБРАННЫЕ ПОЛЬЗОВАТЕЛИ:", 
                font=("Arial", 10, "bold")).pack(pady=(10,0))
        
        # Создаём рамку для списка и кнопок
        fav_frame = tk.Frame(root)
        fav_frame.pack(fill="both", padx=10, pady=5)
        
        self.fav_listbox = tk.Listbox(fav_frame, height=5, font=("Arial", 10))
        self.fav_listbox.pack(side="left", fill="both", expand=True)
        
        # Скролл-бар для списка
        scrollbar = tk.Scrollbar(fav_frame, orient="vertical", 
                                command=self.fav_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.fav_listbox.config(yscrollcommand=scrollbar.set)
        
        # Привязываем двойной клик для просмотра избранного
        self.fav_listbox.bind('<Double-Button-1>', self.view_favorite)
        
        # --- Кнопка удаления из избранного ---
        self.del_btn = tk.Button(root, text="[???] УДАЛИТЬ ИЗ ИЗБРАННОГО", 
                                command=self.remove_favorite,
                                bg="#c0392b", fg="white",
                                font=("Arial", 9, "bold"))
        self.del_btn.pack(pady=5)
        
        # Обновляем отображение списка
        self.update_favorites_list()
        
        # Сохраняем последнего найденного пользователя
        self.current_user = None
    
    def search_user(self):
        """Ищет пользователя на GitHub"""
        username = self.search_entry.get().strip()
        
        # Проверяем, не пустое ли поле (пункт 5 задания)
        if not username:
            messagebox.showerror("Ошибка", "Поле поиска не может быть пустым!")
            return
        
        # Очищаем текстовое поле
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, "[?] Поиск пользователя...")
        self.root.update()
        
        try:
            # Отправляем запрос к GitHub API
            response = requests.get(GITHUB_API + username)
            
            if response.status_code == 200:  # 200 означает "найдено"
                user = response.json()  # Превращаем ответ в понятные данные
                self.current_user = user
                self.display_user_info(user)
                self.fav_btn.pack()  # Показываем кнопку "Добавить"
            else:
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, f"[?] Пользователь '{username}' не найден на GitHub")
                self.fav_btn.pack_forget()  # Прячем кнопку
                
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Нет подключения к интернету!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Что-то пошло не так: {e}")
    
    def display_user_info(self, user):
        """Показывает информацию о пользователе в красивом виде"""
        # Получаем данные (если чего-то нет, ставим "Не указано")
        login = user.get('login', 'Неизвестно')
        name = user.get('name', 'Не указано')
        bio = user.get('bio', 'Нет описания')
        company = user.get('company', 'Не указано')
        location = user.get('location', 'Не указано')
        public_repos = user.get('public_repos', 0)
        followers = user.get('followers', 0)
        following = user.get('following', 0)
        created_at = user.get('created_at', 'Неизвестно')[:10]  # Берём только дату
        url = user.get('html_url', '#')
        
        # Формируем красивый текст
        info = f"""
+==========================================================+
|                    [??] ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ                |
+==========================================================+
|                                                          |
|   Логин:        {login}                                  
|   Имя:          {name}                                   
|   О себе:       {bio}                                    
|   Компания:     {company}                                
|   Локация:      {location}                               
|                                                          |
|   [??] Репозиториев:   {public_repos}                      
|   [??] Подписчиков:    {followers}                         
|   [??] Подписан:       {following}                         
|   [??] Регистрация:    {created_at}                        
|                                                          |
|   [??] Ссылка: {url}                                       
|                                                          |
+==========================================================+
"""
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info)
    
    def add_to_favorites(self):
        """Добавляет текущего пользователя в избранное"""
        if not self.current_user:
            messagebox.showerror("Ошибка", "Нет пользователя для добавления")
            return
        
        username = self.current_user['login']
        
        if username in self.favorites:
            messagebox.showwarning("Предупреждение", 
                                  f"Пользователь '{username}' уже в избранном!")
            return
        
        # Сохраняем только важную информацию
        fav_data = {
            'login': username,
            'name': self.current_user.get('name', ''),
            'bio': self.current_user.get('bio', ''),
            'company': self.current_user.get('company', ''),
            'location': self.current_user.get('location', ''),
            'public_repos': self.current_user.get('public_repos', 0),
            'followers': self.current_user.get('followers', 0),
            'html_url': self.current_user.get('html_url', '#')
        }
        
        self.favorites[username] = fav_data
        self.save_favorites()
        self.update_favorites_list()
        messagebox.showinfo("Успех", f"[?] {username} добавлен в избранное!")
    
    def update_favorites_list(self):
        """Обновляет список избранного в окне"""
        self.fav_listbox.delete(0, tk.END)
        for username in self.favorites.keys():
            self.fav_listbox.insert(tk.END, f"[?] {username}")
    
    def view_favorite(self, event):
        """Показывает информацию о выбранном избранном пользователе"""
        selection = self.fav_listbox.curselection()
        if selection:
            # Убираем "[?] " из имени (4 символа + пробел)
            username = self.fav_listbox.get(selection[0])[5:]
            user_data = self.favorites[username]
            self.current_user = user_data
            self.display_user_info(user_data)
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, username)
            self.fav_btn.pack()
    
    def remove_favorite(self):
        """Удаляет выбранного пользователя из избранного"""
        selection = self.fav_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления")
            return
        
        # Убираем "[?] " из имени (5 символов - 4 буквы + пробел)
        username = self.fav_listbox.get(selection[0])[5:]
        
        if messagebox.askyesno("Подтверждение", f"Удалить {username} из избранного?"):
            del self.favorites[username]
            self.save_favorites()
            self.update_favorites_list()
            
            # Если удалили того, кто сейчас на экране
            if self.current_user and self.current_user.get('login') == username:
                self.fav_btn.pack_forget()
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, "Пользователь удалён из избранного")
            
            messagebox.showinfo("Успех", f"Пользователь {username} удалён")
    
    def load_favorites(self):
        """Загружает избранное из файла"""
        if os.path.exists(FAVORITES_FILE):
            try:
                with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_favorites(self):
        """Сохраняет избранное в файл JSON"""
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, indent=4, ensure_ascii=False)

# ----- 4. Запуск программы -----
if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()