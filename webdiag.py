# TODO:
# 

from flask import Flask, render_template, url_for, request, flash, session, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fwlhflsiurghhgoliuharglih4liguhaol4'

# Меню сайта
menu = [
    {"name": "На главную", "url": "/home"},
    {"name": "1 линия", "url": "/level1"},
    {"name": "2 линия", "url": "/level2"},
    {"name": "3 линия", "url": "/level3"},
    {"name": "Войти", "url": "/login"},
    {"name": "Помощь", "url": "/help"},
    {"name": "Сообщить о проблеме", "url": "/report"},
    {"name": "О портале", "url": "/about"},
]

# Меню диагностики 1 линии
level1menu = [
    {"name": "Диагностика терминала", "url": "l1_diagnostics"},
    {"name": "Проверка связи", "url": "ping-test"},
    {"name": "Перезагрузка терминала", "url": "reboot"},
    ]

# Меню диагностики 2 линии
level2menu = [
    {"name": "Диагностика 2 линия", "url": "l2_diagnostics"},
    {"name": "Настройка", "url": "configuration"},
    {"name": "Удалённая помощь", "url": "remote"}
]

# Меню диагностики 3 линии
level3menu = []

@app.route("/")
@app.route("/home")
def home():
    print(url_for('home'))
    current_menu = menu[1:8]
    return render_template("home.html", title="Выбери уровень поддержки", menu=current_menu)
    
# маршруты для 1 линии
@app.route("/level1")
def level1():
    print(url_for("level1"))
    current_menu = menu[0:8]
    return render_template("level1.html", title="1 линия", menu=current_menu, contentmenu=level1menu)

@app.route("/l1/diagnostics")
def l1_diagnostics():
    current_menu = menu[0:8]
    return render_template("l1/diagnostics.html", 
                         title="Диагностика терминала",
                         menu=current_menu,
                         contentmenu=level1menu)

@app.route("/l1/ping-test")
def l1_ping_test():
    current_menu = menu[0:8]
    return render_template("l1/ping_test.html", 
                         title="Проверка связи",
                         menu=current_menu,
                         contentmenu=level1menu)

@app.route("/l1/reboot")
def l1_reboot():
    current_menu = menu[0:8]
    return render_template("l1/reboot.html", 
                         title="Перезагрузка терминала",
                         menu=current_menu,
                         contentmenu=level1menu)

# маршруты для 2 линии
@app.route("/level2")
def level2():
    print(url_for("level2"))
    current_menu = menu[0:8]
    return render_template("level2.html", 
                           title="2 линия", 
                           menu=current_menu, 
                           contentmenu=level2menu)
    
@app.route("/l2/diagnostics")
def diagnostics():
    print(url_for("diagnostics"))
    current_menu = menu[0:8]
    level2menu
    return render_template("l2/diagnostics.html", 
                           title="Диагностика сети",
                           menu=current_menu, 
                           contentmenu=level2menu)

@app.route("/l2/configuration")
def configuration():
    print(url_for("configuration"))
    current_menu = menu[0:8]
    return render_template("l2/configuration.html", 
                           title="Настройка оборудования", 
                           menu=current_menu, 
                           contentmenu=level2menu)

@app.route("/l2/remote")
def remote():
    print(url_for("remote"))
    current_menu = menu[0:8]
    return render_template("l2/remote.html", title="Удалённая помощь", menu=current_menu)
    
@app.route("/level3")
def level3():
    print(url_for("level3"))
    current_menu = menu[0:8]
    return render_template("level3.html", title="3 линия", menu=current_menu)

@app.route("/help")
def help():
    print(url_for("help"))
    current_menu = menu[0:8]
    return render_template("help.html", title="Помощь", menu=current_menu)

@app.route("/report", methods=["POST", "GET"])
def report():
    if request.method == 'POST':
        print(request.form)
        if len(request.form.get('username', '')) > 4:
            flash("Сообщение отправлено администратору")
        else:
            flash("Ошибка! Сообщение не отправлено!")
    print(url_for("report"))
    current_menu = menu[0:8]
    return render_template("report.html", title="Сообщите о проблеме", 
                        menu=current_menu)

@app.route("/about")
def about():
    print(url_for("about"))
    current_menu = menu[0:8]
    return render_template("about.html", 
                        title="Информация о портале", menu=current_menu)

@app.route("/login", methods=["POST", "GET"])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('psw')
        
        if username == "kivinew" and password == "11223344":
            session['userLogged'] = username
            return redirect(url_for('profile', username=username))
    current_menu = menu[0:8]
    return render_template("login.html", title="Авторизация на сайте", menu=current_menu)

@app.errorhandler(404)
def page_not_found(e):
    print(f"404 Error: {e}")
    error_menu = menu[0:1] + menu[4:6]
    return render_template("404.html", title="Страница не найдена",
        menu=error_menu, image_path="/images/404.jpg", image_alt="Страница не найдена"), 404

if __name__ == "__main__":
    app.run(host='10.2.18.100', port=5000, debug=True)
