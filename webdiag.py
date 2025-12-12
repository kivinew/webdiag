# TODO:
# 1 - определение IP станции
# 2 - пинг с терминала по серийнику, ЛС

from dotenv import load_dotenv
import os, time
import asyncio
import telnetlib3, threading, re
from switches import HUAWEI_OLT
from flask import (
    Flask,
    render_template,
    url_for,
    request,
    flash,
    session,
    redirect,
)

load_dotenv()
OLT_IP = "172.16.17.232"
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

app = Flask(__name__)
# app.json.ensure_ascii = False  # не экранировать кириллицу как \uXXXX
# app.json.mimetype = "application/json; charset=utf-8"

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

#Проверка

# Меню диагностики 3 линии
level3menu = [{""""""}]

HOST_RE = re.compile(r'^[A-Za-z0-9.-]{1,253}$')

def decode_bytes(b: bytes) -> str:
    encs = (['cp866', 'utf-8', 'cp1251'] if os.name == 'nt' else ['utf-8'])
    for e in encs:
        try:
            return b.decode(e)
        except UnicodeDecodeError:
            pass
    return b.decode(encs[0], errors='replace')

async def remote_ping_wait(reader, timeout=20):
    t0 = asyncio.get_event_loop().time()
    lines = []
    while asyncio.get_event_loop().time() - t0 < timeout:
        line = await reader.readline()
        if line:
            lines.append(line.strip())
            if 'ONT remote-ping information' in line or 'Failure:' in line:
                extra = []
                if 'ONT remote-ping information' in line:
                    extra = [(await reader.readline()).strip() for _ in range(12)]
                raw = "\n".join(lines + extra)
                ip = re.search(r'IP address of ping\s*:\s*([\d.]+)', raw)
                recv = re.search(r'Receive packets\s*:\s*(\d+)', raw)
                lost = re.search(r'Lost packets\s*:\s*(\d+)', raw)
                received = int(recv.group(1)) if recv else 0
                lost_packets = int(lost.group(1)) if lost else -1
                ok = (received > 0) and (lost_packets < 2) and ('Failure:' not in line)
                return {
                    'ok': ok,
                    'ip': ip.group(1) if ip else None,
                    'received': received,
                    'lost': lost_packets,
                    'output': raw
                }
    return {'ok': False, 'ip': None, 'received': 0, 'lost': -1, 'output': 'Нет результата (таймаут)'}

def query_station(host, serial, olt_ip):
    res_data = {'ok': False, 'output': '', 'serialInfo': ''}
    
    def telnet_code():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def run_telnet():
            
            try:
                print(f"[TELNET] Connecting to OLT {olt_ip}...")
                reader, writer = await telnetlib3.open_connection(
                olt_ip, 
                port=23, 
                encoding='utf-8'
                )
                
                auth_log = []
                # Пример логина. Подстройте под свою станцию!
                print("[TELNET] Connected. Authorization...")
                if reader and writer:
                    auth_log.append(await reader.readuntil(b'name:'))
                    # print("[TELNET]", auth_log[-1].strip())
                    writer.write(f"{USERNAME}" + '\n')     # ваш логин
                    auth_log.append(await reader.readuntil(b'password:'))
                    # print("[TELNET]", auth_log[-1].strip())
                    writer.write(f"{PASSWORD}" + '\n')

                    motd = await reader.readuntil(b'>')
                    # print("[TELNET] MOTD/Prompt:\n", motd.strip())

                    # Переход в enable/config
                    writer.write('enable\n')
                    _ = await reader.readuntil(b'#')
                    writer.write('config\n')
                    _ = await reader.readuntil(b'(config)#')

                    print("[TELNET] AUTHORIZED!")

                    # Теперь искать ONT
                    writer.write(f'display ont info by-sn {serial}\n')
                    writer.write('q\n')
                    time.sleep(2)
                    ont_out = await reader.readuntil(b') ----')
                    # time.sleep(2)
                    out_str = ont_out.decode('utf-8', errors='replace').strip()
                    # print('[TELNET] Output:\n', ont_out)
                
                    pattern = r'F/S/P\s*:\s*(\d+)/(\d+)/(\d+)\s+ONT-ID\s*:\s*(\d+)'
                    match = re.search(pattern, out_str.replace('\r', ''))

                    if not match:
                        res_data['output'] = 'ONT не найден'
                        print('[TELNET] ONT не найден')
                        writer.close()
                        await writer.wait_closed()
                        return

                    frame, slot, port, ont = match.group(1), match.group(2), match.group(3), match.group(4)
                    res_data['serialInfo'] = f'{frame}/{slot}/{port}/{ont}'
                    print(f"{res_data['serialInfo']}")

                    writer.write(f'interface gpon {frame}/{slot}\nont remote-ping {port} {ont} ip-address {host}\nq\n')
                    time.sleep(5)
                    
                    ping_out = await remote_ping_wait(reader)

                    res_data['ok'] = ('Transmit packets' in str(ping_out))
                    res_data['output'] = ping_out

                    print('[TELNET] PING output:\n', res_data)
                    
                    writer.close()
                    await writer.wait_closed()
                    print('[TELNET] Connection closed.')

            except Exception as e:
                print(f'[TELNET][ERROR] {str(e)}')
                res_data['output'] = f'Ошибка telnet: {e}'

            
        loop.run_until_complete(run_telnet())
    t = threading.Thread(target=telnet_code)
    t.start()
    t.join(timeout=15)
    return res_data

@app.post('/api/ping')
def api_ping():
    req = request.get_json(silent=True) or {}
    host = req.get('host', '').strip()
    serial = req.get('serial', '').strip()
    olt_ip = req.get('olt_ip', '').strip()
    # if not (host and serial and olt_ip):
    #     return {'error': 'Необходимо заполнить все поля'}, 400
    print(f'Получен olt_ip: "{olt_ip}"')    # <-- Debug!
    res = query_station(host, serial, olt_ip)
    return res, 200

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
        contentmenu=level1menu, HUAWEI_OLT = HUAWEI_OLT
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
