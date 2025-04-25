from flask import Flask, render_template, url_for

app = Flask(__name__)

# Меню теперь словарь, где ключ - название пункта, значение - URL
menu = [{"name": "1 линия", "url": "level1"},
    {"name": "2 линия", "url": "level2"},
    {"name": "3 линия", "url": "leve3"},
    {"name": "Помощь", "url": "help"},
    {"name": "Сообщить о проблеме", "url": "report"}]

@app.route("/")
def home():
    print(url_for('home'))
    # Передаем только нужные пункты меню (первые 3)
    current_menu = {k: menu[k] for k in list(menu.keys())[:3]}
    return render_template("home.html", 
                         title="Выбери уровень поддержки:", 
                         menu=current_menu)

@app.route("/about")
def about():
    print(url_for("about"))
    # Передаем часть пунктов меню (с 3го по 5й)
    current_menu = {k: menu[k] for k in list(menu.keys())[2:5]}
    return render_template("about.html", 
                         title="Информация о портале техподдержки КЭС", 
                         menu=current_menu)

@app.errorhandler(404)
def page_not_found(e):
    print(f"404 Error: {e}")
    # Для страницы 404 передаем только пункт "На главную"
    error_menu = {"На главную": menu["На главную"]}
    return render_template("404.html", 
                         title="Страница не найдена", 
                         menu=error_menu), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
