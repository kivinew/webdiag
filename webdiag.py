# TODO:
#

from dotenv import load_dotenv
import subprocess
import sys
import os
import re
import paramiko
from flask import (
    Flask,
    render_template,
    url_for,
    request,
    flash,
    session,
    redirect,
    jsonify,
)

load_dotenv()
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

app = Flask(__name__)
app.json.ensure_ascii = False  # не экранировать кириллицу как \uXXXX
app.json.mimetype = "application/json; charset=utf-8"
app.config["SECRET_KEY"] = "fwlhflsiurghhgoliuharglih4liguhaol4"

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
    {"name": "Диагностика терминала", "url": "/level1/diagnostics"},
    {"name": "Проверка связи", "url": "/level1/pingtest"},
    {"name": "Перезагрузка терминала", "url": "/level1/reboot"},
]

# Меню диагностики 2 линии
level2menu = [
    {"name": "Диагностика 2 линия", "url": "/level2/diagnostics"},
    {"name": "Настройка", "url": "/level2/configuration"},
    {"name": "Удалённая помощь", "url": "/level2/remote"},
]

# Меню диагностики 3 линии
level3menu = [{""""""}]

HOST_RE = re.compile(r'^[A-Za-z0-9.-]{1,253}$')

def build_ping_cmd(host: str):
    if os.name == 'nt':
        # Windows: -n (count), -w (timeout ms)
        return ['ping', '-n', '4', '-w', '1000', host]
    else:
        # Linux/macOS: -c (count), -W (timeout s on Linux; macOS использует -W в секундах для "ttl expired", -t/-W отличаются между платформами)
        # Для простой совместимости используем -c и -W=1; при необходимости адаптируйте под конкретную ОС.
        return ['ping', '-c', '4', '-W', '1', host]

@app.post('/api/ping')
def api_ping():
    data = request.get_json(silent=True) or {}
    host = (data.get('host') or '').strip()
    if not host or not HOST_RE.match(host):
        return {'error': 'Некорректный хост'}, 400

    try:
        cmd = build_ping_cmd(host)
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',     # ключевая строка для кириллицы
            errors='replace',     # опционально: не падать на некорректных байтах
            timeout=6
        )
        payload = {
            'ok': res.returncode == 0,
            'code': res.returncode,
            'output': res.stdout or res.stderr
        }
        return payload, 200  # или jsonify(payload), если предпочитаете явный Response

    except subprocess.TimeoutExpired as e:
        return {'error': 'Таймаут выполнения', 'output': getattr(e, 'stdout', '')}, 504
    except Exception as e:
        return {'error': str(e)}, 500

@app.route("/")
@app.route("/home")
def home():
    print(url_for("home"))
    current_menu = menu[1:8]
    return render_template(
        "home.html", title="Выбери уровень поддержки", menu=current_menu
    )

# маршруты для 1 линии
@app.route("/level1")
def level1():
    # print(url_for("level1"))
    current_menu = menu[0:8]
    return render_template(
        "level1.html", title="1 линия", menu=current_menu, contentmenu=level1menu
    )

@app.route("/level1/diagnostics")
def l1_diagnostics():
    current_menu = menu[0:8]
    return render_template(
        "level1/l1_diagnostics.html",
        title="Диагностика терминала",
        menu=current_menu,
        contentmenu=level1menu,
    )

@app.route("/level1/pingtest")
def l1_pingtest():
    current_menu = menu[0:8]
    return render_template(
        "level1/l1_pingtest.html",
        title="Проверка связи",
        menu=current_menu,
        contentmenu=level1menu,
    )

@app.route("/level1/reboot")
def l1_reboot():
    current_menu = menu[0:8]
    return render_template(
        "level1/l1_reboot.html",
        title="Перезагрузка терминала",
        menu=current_menu,
        contentmenu=level1menu,
    )

# маршруты для 2 линии
@app.route("/level2")
def level2():
    # print(url_for("level2"))
    current_menu = menu[0:8]
    return render_template(
        "level2.html", title="2 линия", menu=current_menu, contentmenu=level2menu
    )

@app.route("/level2/diagnostics")
def l2_diagnostics():
    # print(url_for("l2_diagnostics"))
    current_menu = menu[0:8]
    level2menu
    return render_template(
        "level2/l2_diagnostics.html",
        title="Диагностика сети",
        menu=current_menu,
        contentmenu=level2menu,
    )

@app.route("/level2/configuration")
def configuration():
    # print(url_for("configuration"))
    current_menu = menu[0:8]
    return render_template(
        "level2/l2_configuration.html",
        title="Настройка оборудования",
        menu=current_menu,
        contentmenu=level2menu,
    )

@app.route("/level2/remote")
def remote():
    # print(url_for("remote"))
    current_menu = menu[0:8]
    return render_template(
        "level2/l2_remote.html", title="Удалённая помощь", menu=current_menu
    )

@app.route("/level3")
def level3():
    # print(url_for("level3"))
    current_menu = menu[0:8]
    return render_template("level3.html", title="3 линия", menu=current_menu)

@app.route("/help")
def help():
    # print(url_for("help"))
    current_menu = menu[0:8]
    return render_template("help.html", title="Помощь", menu=current_menu)


@app.route("/report", methods=["POST", "GET"])
def report():
    if request.method == "POST":
        print(request.form)
        if len(request.form.get("username", "")) > 4:
            flash("Сообщение отправлено администратору")
        else:
            flash("Ошибка! Сообщение не отправлено!")
    print(url_for("report"))
    current_menu = menu[0:8]
    return render_template(
        "report.html", title="Сообщите о проблеме", menu=current_menu
    )


@app.route("/about")
def about():
    # print(url_for("about"))
    current_menu = menu[0:8]
    return render_template(
        "about.html", title="Информация о портале", menu=current_menu
    )


@app.route("/login", methods=["POST", "GET"])
def login():
    if "userLogged" in session:
        return redirect(url_for("profile", username=session["userLogged"]))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("psw")

        if username == "kivinew" and password == "11223344":
            session["userLogged"] = username
            return redirect(url_for("profile", username=username))
    current_menu = menu[0:8]
    return render_template(
        "login.html", title="Авторизация на сайте", menu=current_menu
    )


@app.errorhandler(404)
def page_not_found(e):
    print(f"404 Error: {e}")
    error_menu = menu[0:1] + menu[4:6]
    return render_template(
        "404.html",
        title="Страница не найдена",
        menu=error_menu,
        image_path="/images/404.jpg",
        image_alt="Страница не найдена",
    ), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
