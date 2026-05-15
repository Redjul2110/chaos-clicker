import tkinter as tk
from tkinter import messagebox
import random
import subprocess
import tempfile
import os

# -----------------------------
# Chaos Task Clicker
# Harmlos:
# - keine echten Fehler
# - keine Dateien werden beschädigt
# - öffnet am Ende nur Notepad mit einem Text
# -----------------------------

clicks = 0
coins = 0

click_power = 1
click_power_cost = 15
time_cost = 20

task_number = 1
task_type = "clicks"
task_goal = 30
task_progress = 0
time_left = 45

game_running = False
game_started = False
game_paused = False

extra_windows = []
button_parent = None
click_btn = None
manual_close = True

start_words_clicked = {
    "Klicke": False,
    "Clicker": False,
    "klickende": False,
    "Clicker2": False
}


# -----------------------------
# Startscreen
# -----------------------------

def show_start_screen():
    hide_game_ui()
    pause_frame.pack_forget()
    dev_frame.pack_forget()
    start_frame.pack(fill="both", expand=True)

    start_status_label.config(
        text="Drücke alle Click/Klick-Wörter, um das Spiel zu starten."
    )


def start_word_pressed(word_key, button):
    start_words_clicked[word_key] = True
    button.config(state="disabled", text=button.cget("text") + " ✓")

    if all(start_words_clicked.values()):
        start_status_label.config(text="Alle Klick-Wörter gedrückt. Spiel startet...")
        root.after(700, start_game)


def start_game():
    global game_running, game_started, game_paused

    game_running = True
    game_started = True
    game_paused = False

    start_frame.pack_forget()
    pause_frame.pack_forget()
    dev_frame.pack_forget()

    show_game_ui()
    create_click_button(root, 200, 330)
    update_labels()
    timer_tick()


# -----------------------------
# Dev Tool
# -----------------------------

def show_dev_tools():
    start_frame.pack_forget()
    pause_frame.pack_forget()
    hide_game_ui()
    dev_frame.pack(fill="both", expand=True)


def dev_start_level(level):
    global task_number, game_running, game_started, game_paused
    global clicks, coins, click_power, click_power_cost, time_cost

    clicks = 0
    coins = 999
    click_power = 5
    click_power_cost = 15
    time_cost = 20

    task_number = level - 1

    game_running = True
    game_started = True
    game_paused = False

    dev_frame.pack_forget()
    start_frame.pack_forget()
    show_game_ui()

    new_task(force_number=level)
    create_click_button(root, 200, 330)
    update_labels()
    timer_tick()


def dev_add_money():
    global coins
    coins += 500
    update_labels()
    messagebox.showinfo("Dev Tool", "+500 Münzen gegeben.")


def dev_add_time():
    global time_left
    time_left += 60
    update_labels()
    messagebox.showinfo("Dev Tool", "+60 Sekunden gegeben.")


def dev_spawn_window():
    create_funny_window()
    messagebox.showinfo("Dev Tool", "Popup-Fenster erstellt.")


def dev_fake_errors():
    show_fake_errors()


def dev_force_task_complete():
    global task_progress
    task_progress = task_goal
    update_labels()
    messagebox.showinfo("Dev Tool", "Aktuelle Aufgabe wurde auf geschafft gesetzt.")


def dev_cheater_ending():
    cheater_ending()


# -----------------------------
# Pause
# -----------------------------

def toggle_pause(event=None):
    if not game_started or not game_running:
        return

    if game_paused:
        resume_game()
    else:
        pause_game()


def pause_game():
    global game_paused

    if not game_running:
        return

    game_paused = True

    hide_game_ui()
    hide_extra_windows()
    pause_frame.pack(fill="both", expand=True)


def resume_game():
    global game_paused

    game_paused = False

    pause_frame.pack_forget()
    show_game_ui()
    show_extra_windows()
    create_click_button(root, 200, 330)
    update_labels()


def hide_extra_windows():
    for win in extra_windows:
        try:
            if win.winfo_exists():
                win.withdraw()
        except:
            pass


def show_extra_windows():
    for win in extra_windows:
        try:
            if win.winfo_exists():
                win.deiconify()
        except:
            pass


# -----------------------------
# UI anzeigen / verstecken
# -----------------------------

def hide_game_ui():
    title_label.pack_forget()
    info_label.pack_forget()
    task_label.pack_forget()
    stats_frame.pack_forget()
    power_label.pack_forget()
    power_btn.pack_forget()
    time_btn.pack_forget()
    pause_btn.pack_forget()

    try:
        if click_btn is not None and click_btn.winfo_exists():
            click_btn.destroy()
    except:
        pass


def show_game_ui():
    title_label.pack(pady=10)
    info_label.pack()
    task_label.pack(pady=8)
    stats_frame.pack(pady=6)
    power_label.pack(pady=5)
    power_btn.pack(pady=4)
    time_btn.pack(pady=4)
    pause_btn.pack(pady=6)


# -----------------------------
# Game Logik
# -----------------------------

def update_labels():
    title_label.config(text=f"Chaos Clicker - Aufgabe {task_number}")
    task_label.config(text=get_task_text())

    clicks_label.config(text=f"Klicks: {clicks}")
    coins_label.config(text=f"Münzen: {coins}")
    time_label.config(text=f"Zeit: {time_left}s")
    power_label.config(text=f"Klick-Power: {click_power}x")

    power_btn.config(text=f"+1 Klick-Power kaufen ({click_power_cost} Münzen)")
    time_btn.config(text=f"+15 Sekunden kaufen ({time_cost} Münzen)")


def get_task_text():
    if task_number == 10:
        return (
            f"Aufgabe 10: Mir sind die Ideen ausgegangen.\n"
            f"Klicke {task_goal} mal in fast keiner Zeit. "
            f"Fortschritt: {task_progress}/{task_goal}"
        )

    if task_type == "clicks":
        return f"Aufgabe: Erreiche {task_goal} Klicks. Fortschritt: {task_progress}/{task_goal}"

    if task_type == "upgrades":
        return f"Aufgabe: Kaufe {task_goal} Upgrades. Fortschritt: {task_progress}/{task_goal}"

    if task_type == "coins":
        return f"Aufgabe: Sammle {task_goal} Münzen. Fortschritt: {task_progress}/{task_goal}"

    if task_type == "button_clicks":
        return f"Aufgabe: Klicke den Chaos-Button {task_goal} mal. Fortschritt: {task_progress}/{task_goal}"

    return "Aufgabe: Überlebe."


def check_task_progress():
    global task_progress

    if task_type == "clicks":
        task_progress = clicks

    elif task_type == "coins":
        task_progress = coins

    update_labels()


def task_completed():
    return task_progress >= task_goal


def new_task(force_number=None):
    global task_number, task_type, task_goal, task_progress
    global time_left, clicks

    if force_number is None:
        task_number += 1
    else:
        task_number = force_number

    task_progress = 0

    # Aufgabe 10: fast unmöglich
    if task_number == 10:
        task_type = "button_clicks"
        task_goal = 250
        time_left = 20
        clicks = 0

        messagebox.showwarning(
            "Aufgabe 10",
            "Mir sind die Ideen ausgegangen.\n\n"
            "Ab jetzt wird es fast unmöglich."
        )

        spam_funny_windows()
        update_labels()
        return

    task_type = random.choice([
        "clicks",
        "upgrades",
        "coins",
        "button_clicks"
    ])

    if task_type == "clicks":
        task_goal = 25 + task_number * 12
        time_left = 45 + task_number * 4
        clicks = 0

    elif task_type == "upgrades":
        task_goal = min(2 + task_number // 2, 6)
        time_left = 55 + task_number * 4

    elif task_type == "coins":
        task_goal = 35 + task_number * 20
        time_left = 50 + task_number * 4

    elif task_type == "button_clicks":
        task_goal = 12 + task_number * 3
        time_left = 45 + task_number * 4

    messagebox.showinfo(
        "Neue Aufgabe!",
        f"Aufgabe {task_number} startet jetzt!\n\n{get_task_text()}"
    )

    update_labels()


def get_alive_windows():
    windows = [root]

    for win in extra_windows:
        try:
            if win.winfo_exists():
                windows.append(win)
        except:
            pass

    return windows


def create_click_button(parent, x=None, y=None):
    global click_btn, button_parent

    try:
        if click_btn is not None and click_btn.winfo_exists():
            click_btn.destroy()
    except:
        pass

    click_btn = tk.Button(
        parent,
        text=random.choice(["KLICK!", "CLICK!", "KLICK MICH!", "NICHT HIER!"]),
        font=("Arial", 15, "bold"),
        command=click_button
    )

    if x is None:
        x = random.randint(30, 220)

    if y is None:
        y = random.randint(50, 140)

    click_btn.place(x=x, y=y)
    button_parent = parent


def move_button_to_random_place():
    windows = get_alive_windows()
    new_parent = random.choice(windows)

    x = random.randint(20, 230)
    y = random.randint(40, 150)

    create_click_button(new_parent, x, y)


def move_button_inside_current_window():
    parent = button_parent

    try:
        if parent is None or not parent.winfo_exists():
            parent = root
    except:
        parent = root

    x = random.randint(20, 230)
    y = random.randint(40, 150)

    create_click_button(parent, x, y)


def create_funny_window():
    if len(extra_windows) >= 8:
        return

    win = tk.Toplevel(root)
    win.title(random.choice([
        "Klick-Kontrolle",
        "Maus-Prüfung",
        "Windows Klickamt",
        "Button eventuell hier",
        "Nicht panisch werden",
        "Klick-Labor",
        "Maus-Behörde",
        "Klick-Steuerbehörde"
    ]))

    win.geometry("330x220")
    win.resizable(False, False)

    texts = [
        "Dieses Fenster wurde von deinem Klickstress erstellt.",
        "Der Button könnte hier sein. Oder gleich weg sein.",
        "Bitte ruhig bleiben. Die Maus beobachtet dich.",
        "Windows fragt sich, warum du so klickst.",
        "Dieses Fenster sieht wichtiger aus als es ist.",
        "Achtung: Der Button kann gleich hier auftauchen.",
        "Klick-Inspektion läuft. Bitte nicht atmen.",
        "Ich bin nur hier, um dich zu verwirren."
    ]

    label = tk.Label(
        win,
        text=random.choice(texts),
        font=("Arial", 11),
        wraplength=290
    )
    label.pack(pady=35)

    extra_windows.append(win)

    def on_close_extra():
        global button_parent

        if win in extra_windows:
            extra_windows.remove(win)

        try:
            if button_parent == win:
                create_click_button(root, 200, 330)
        except:
            pass

        try:
            win.destroy()
        except:
            pass

    win.protocol("WM_DELETE_WINDOW", on_close_extra)

    if random.randint(1, 2) == 1:
        create_click_button(win)


def spam_funny_windows():
    for _ in range(5):
        create_funny_window()


def click_button():
    global clicks, coins, task_progress

    if not game_running or game_paused:
        return

    clicks += click_power
    coins += click_power

    if task_type == "button_clicks":
        task_progress += 1

    check_task_progress()

    # Aufgabe 10: extra Chaos
    if task_number == 10:
        if random.randint(1, 2) == 1:
            create_funny_window()

        move_button_to_random_place()
        return

    if random.randint(1, 8) == 1:
        create_funny_window()

    if random.randint(1, 3) == 1:
        move_button_to_random_place()
    else:
        move_button_inside_current_window()


def buy_click_power():
    global coins, click_power, click_power_cost
    global task_progress

    if not game_running or game_paused:
        return

    if coins >= click_power_cost:
        coins -= click_power_cost
        click_power += 1
        click_power_cost += 15

        if task_type == "upgrades":
            task_progress += 1

        check_task_progress()
    else:
        messagebox.showwarning(
            "Zu wenig Münzen",
            "Du brauchst mehr Münzen für stärkere Finger."
        )


def buy_time():
    global coins, time_left, time_cost
    global task_progress

    if not game_running or game_paused:
        return

    if coins >= time_cost:
        coins -= time_cost
        time_left += 15
        time_cost += 20

        if task_type == "upgrades":
            task_progress += 1

        check_task_progress()
    else:
        messagebox.showwarning(
            "Zu wenig Münzen",
            "Zeit ist Geld. Und du hast gerade zu wenig Münzen."
        )


def timer_tick():
    global time_left

    if not game_running:
        return

    if game_paused:
        root.after(1000, timer_tick)
        return

    check_task_progress()

    if time_left <= 0:
        if task_completed():
            if task_number == 10:
                cheater_ending()
                return
            else:
                new_task()
        else:
            lose_game()
            return

    time_left -= 1
    update_labels()
    root.after(1000, timer_tick)


def cheater_ending():
    global game_running, manual_close

    game_running = False
    manual_close = False

    messagebox.showerror(
        "Du cheatest",
        "Du hast Aufgabe 10 geschafft?\n\n"
        "Nein. Das glaube ich dir nicht.\n"
        "Du cheatest."
    )

    close_all_windows()
    open_angry_notepad()


def open_angry_notepad():
    try:
        temp_path = os.path.join(tempfile.gettempdir(), "clicker_game_angry.txt")

        with open(temp_path, "w", encoding="utf-8") as file:
            file.write(
                "DU CHEATEST.\n\n"
                "Das klickende Clicker Spiel hat alles gesehen.\n"
                "Du dachtest wirklich, ich merke das nicht?\n\n"
                ">:)\n"
            )

        subprocess.Popen(["notepad.exe", temp_path])
    except:
        pass


def lose_game():
    global game_running, manual_close
    game_running = False
    manual_close = False

    show_fake_errors()
    close_all_windows()


def show_fake_errors():
    errors = [
        (
            "Click.exe funktioniert nicht mehr",
            "Dein Klickfinger hat versucht zu kündigen."
        ),
        (
            "Aufgabe fehlgeschlagen",
            "Du hattest eine Aufgabe.\nDu hattest Zeit.\nDu hattest Hoffnung."
        ),
        (
            "Windows Klickprüfung",
            "Ergebnis: zu wenig Klick, zu viel Panik."
        ),
        (
            "Upgrade Shop Error",
            "Der Shop sagt: Mehr Upgrades wären schlau gewesen."
        ),
        (
            "Skill Issue erkannt",
            "Fehlercode: 404\nReaktionszeit nicht gefunden."
        ),
        (
            "Maus emotional beschädigt",
            "Deine Maus braucht jetzt erstmal Urlaub."
        ),
        (
            "Fake Blue Screen",
            ":(\nDein PC ist okay.\nDein Run eher nicht."
        ),
        (
            "Nur Spaß",
            "Alle Meldungen sind fake.\nDein PC wurde nicht verändert."
        )
    ]

    for title, text in errors:
        messagebox.showerror(title, text)


def on_main_close():
    global manual_close

    if manual_close:
        messagebox.showinfo(
            "Clicker Game ist traurig",
            "Clicker Game ist traurig, weil du einfach gegangen bist 😢"
        )

    close_all_windows()


def close_all_windows():
    for win in extra_windows:
        try:
            if win.winfo_exists():
                win.destroy()
        except:
            pass

    try:
        root.destroy()
    except:
        pass


# -----------------------------
# Hauptfenster
# -----------------------------

root = tk.Tk()
root.title("Chaos Task Clicker")
root.geometry("520x460")
root.resizable(False, False)

root.protocol("WM_DELETE_WINDOW", on_main_close)
root.bind("<Escape>", toggle_pause)


# -----------------------------
# Startscreen UI
# -----------------------------

start_frame = tk.Frame(root)

start_title = tk.Label(
    start_frame,
    text="Chaos Clicker Startscreen",
    font=("Arial", 22, "bold")
)
start_title.pack(pady=18)

start_info = tk.Label(
    start_frame,
    text="Drücke alle Click/Klick-Wörter:",
    font=("Arial", 12)
)
start_info.pack(pady=5)

sentence_frame = tk.Frame(start_frame)
sentence_frame.pack(pady=12)

btn_klicke = tk.Button(
    sentence_frame,
    text="Klicke",
    font=("Arial", 11, "bold"),
    command=lambda: start_word_pressed("Klicke", btn_klicke)
)
btn_klicke.grid(row=0, column=0, padx=3)

tk.Label(sentence_frame, text="den", font=("Arial", 11)).grid(row=0, column=1, padx=3)

btn_clicker1 = tk.Button(
    sentence_frame,
    text="Clicker",
    font=("Arial", 11, "bold"),
    command=lambda: start_word_pressed("Clicker", btn_clicker1)
)
btn_clicker1.grid(row=0, column=2, padx=3)

tk.Label(sentence_frame, text="Knopf um das", font=("Arial", 11)).grid(row=0, column=3, padx=3)

btn_klickende = tk.Button(
    sentence_frame,
    text="klickende",
    font=("Arial", 11, "bold"),
    command=lambda: start_word_pressed("klickende", btn_klickende)
)
btn_klickende.grid(row=1, column=0, padx=3, pady=8)

btn_clicker2 = tk.Button(
    sentence_frame,
    text="Clicker",
    font=("Arial", 11, "bold"),
    command=lambda: start_word_pressed("Clicker2", btn_clicker2)
)
btn_clicker2.grid(row=1, column=1, padx=3, pady=8)

tk.Label(sentence_frame, text="Spiel zu starten", font=("Arial", 11)).grid(row=1, column=2, columnspan=2, padx=3)

start_status_label = tk.Label(
    start_frame,
    text="",
    font=("Arial", 11),
    wraplength=440
)
start_status_label.pack(pady=10)

dev_open_btn = tk.Button(
    start_frame,
    text="Dev Tool öffnen",
    font=("Arial", 11, "bold"),
    command=show_dev_tools,
    width=25
)
dev_open_btn.pack(pady=10)


# -----------------------------
# Dev Tool UI
# -----------------------------

dev_frame = tk.Frame(root)

dev_title = tk.Label(
    dev_frame,
    text="Dev Tool",
    font=("Arial", 24, "bold")
)
dev_title.pack(pady=15)

dev_info = tk.Label(
    dev_frame,
    text="Teste Level und Funktionen.",
    font=("Arial", 11)
)
dev_info.pack(pady=5)

level_frame = tk.Frame(dev_frame)
level_frame.pack(pady=8)

for i in range(1, 11):
    btn = tk.Button(
        level_frame,
        text=f"Level {i}",
        width=8,
        command=lambda lvl=i: dev_start_level(lvl)
    )
    btn.grid(row=(i - 1) // 5, column=(i - 1) % 5, padx=4, pady=4)

dev_button_frame = tk.Frame(dev_frame)
dev_button_frame.pack(pady=12)

tk.Button(
    dev_button_frame,
    text="+500 Münzen",
    command=dev_add_money,
    width=18
).grid(row=0, column=0, padx=5, pady=4)

tk.Button(
    dev_button_frame,
    text="+60 Sekunden",
    command=dev_add_time,
    width=18
).grid(row=0, column=1, padx=5, pady=4)

tk.Button(
    dev_button_frame,
    text="Popup testen",
    command=dev_spawn_window,
    width=18
).grid(row=1, column=0, padx=5, pady=4)

tk.Button(
    dev_button_frame,
    text="Fake Errors testen",
    command=dev_fake_errors,
    width=18
).grid(row=1, column=1, padx=5, pady=4)

tk.Button(
    dev_button_frame,
    text="Aufgabe schaffen",
    command=dev_force_task_complete,
    width=18
).grid(row=2, column=0, padx=5, pady=4)

tk.Button(
    dev_button_frame,
    text="Cheater Ende testen",
    command=dev_cheater_ending,
    width=18
).grid(row=2, column=1, padx=5, pady=4)

tk.Button(
    dev_button_frame,
    text="Zurück",
    command=show_start_screen,
    width=18
).grid(row=3, column=0, columnspan=2, padx=5, pady=4)


# -----------------------------
# Pause UI
# -----------------------------

pause_frame = tk.Frame(root)

pause_title = tk.Label(
    pause_frame,
    text="PAUSE",
    font=("Arial", 30, "bold")
)
pause_title.pack(pady=45)

pause_text = tk.Label(
    pause_frame,
    text="Das klickende Clicker Spiel klickt gerade nicht.",
    font=("Arial", 12)
)
pause_text.pack(pady=10)

resume_btn = tk.Button(
    pause_frame,
    text="Weiter klicken",
    font=("Arial", 14, "bold"),
    command=resume_game,
    width=20
)
resume_btn.pack(pady=20)

pause_hint = tk.Label(
    pause_frame,
    text="Tipp: ESC pausiert und setzt fort.",
    font=("Arial", 10)
)
pause_hint.pack(pady=5)


# -----------------------------
# Game UI
# -----------------------------

title_label = tk.Label(
    root,
    text="Chaos Clicker",
    font=("Arial", 21, "bold")
)

info_label = tk.Label(
    root,
    text="Erfülle Aufgaben, kaufe Upgrades und finde den Button wieder!",
    font=("Arial", 11)
)

task_label = tk.Label(
    root,
    text="",
    font=("Arial", 11, "bold"),
    wraplength=480
)

stats_frame = tk.Frame(root)

clicks_label = tk.Label(stats_frame, text="", font=("Arial", 12))
clicks_label.grid(row=0, column=0, padx=8)

coins_label = tk.Label(stats_frame, text="", font=("Arial", 12))
coins_label.grid(row=0, column=1, padx=8)

time_label = tk.Label(stats_frame, text="", font=("Arial", 12))
time_label.grid(row=0, column=2, padx=8)

power_label = tk.Label(root, text="", font=("Arial", 12, "bold"))

power_btn = tk.Button(
    root,
    text="",
    command=buy_click_power,
    width=40
)

time_btn = tk.Button(
    root,
    text="",
    command=buy_time,
    width=40
)

pause_btn = tk.Button(
    root,
    text="Pause",
    command=pause_game,
    width=20
)


show_start_screen()
root.mainloop()