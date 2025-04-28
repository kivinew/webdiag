from flask import Flask, render_template, url_for

app = Flask(__name__)

# Меню сайта
menu = [
    {"name": "На главную", "url": "home"},
    {"name": "1 линия", "url": "level1"},
    {"name": "2 линия", "url": "level2"},
    {"name": "3 линия", "url": "level3"},
    {"name": "Помощь", "url": "help"},
    {"name": "Сообщить о проблеме", "url": "report"},
    {"name": "О портале", "url": "about"}
]

@app.route("/")
@app.route("/home")
def home():
    print(url_for('home'))
    # меню 6 пунктов
    current_menu = menu[1:7]
    return render_template("home.html", 
                        title="Выбери уровень поддержки:", 
                        menu=current_menu)

@app.route("/about")
def about():
    print(url_for("about"))
    # 
    current_menu = menu[0:1] + menu[4:6]
    return render_template("about.html", 
                        title="Информация о портале", 
                        menu=current_menu)
@app.route("/level1")
def level1():
    print(url_for("level1"))
    # Берем с 4го по 6й пункт
    current_menu = menu[1:7]
    return render_template("level1.html", 
                        title="1 линия", 
                        menu=current_menu)
@app.route("/level2")
def level2():
    print(url_for("level2"))
    # 
    current_menu = menu[1:7]
    return render_template("level2.html", 
                        title="2 линия", 
                        menu=current_menu)
@app.route("/level3")
def level3():
    print(url_for("level3"))
    # Берем с 4го по 6й пункт
    current_menu = menu[1:7]
    return render_template("level3.html", 
                        title="3 линия", 
                        menu=current_menu)

@app.route("/help")
def help():
    print(url_for("help"))
    # Берем с 4го по 6й пункт
    current_menu = menu[0:1] + menu[5:6]
    return render_template("help.html", 
                        title="Помощь по порталу диагностики", 
                        menu=current_menu)

@app.route("/report")
def report():
    print(url_for("report"))
    # 6й пункт меню
    current_menu = menu[0:1] + menu[6:]
    return render_template("report.html", 
                        title="Сообщите о проблеме", 
                        menu=current_menu)

@app.errorhandler(404)
def page_not_found(e):
    print(f"404 Error: {e}")
    # Берем только последний пункт "На главную"
    error_menu = [menu[-1]]
    return render_template("404.html", 
                        title="Страница не найдена", 
                        menu=error_menu), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
