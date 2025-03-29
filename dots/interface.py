from __future__ import annotations

from tkinter import END, VERTICAL, WORD, Label, Scrollbar, Text, Tk, ttk
from tkinter.ttk import Treeview


def create_leaderboard(root: Tk) -> Treeview:
    """
    Создает таблицу лидеров в GUI, отображающую рейтинг игроков.
    """
    _columns: tuple[str, str, str] = ("Место", "Имя", "Счет")

    _header_label: Label = Label(
        root,
        text="Таблица лидеров",
        font=("Arial", 12, "bold"),
        bg="white",
        highlightthickness=0,
    )
    _header_label.place(relx=1.0, rely=0.0, x=-65, y=20, anchor="ne")

    _tree: Treeview = ttk.Treeview(root, columns=_columns, show="headings")
    for col in _columns:
        _tree.heading(col, text=col)
        _tree.column(col, width=80, anchor="center")

    _style: ttk.Style = ttk.Style()
    _style.configure("Treeview", rowheight=40, font=("Arial", 10))
    _style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="lightblue")

    _num_rows: int = 3
    _row_height: int = 45
    _header_height: int = 30
    _total_height: int = _num_rows * _row_height + _header_height

    _tree.place(relx=1.0, rely=0.0, x=-20, y=50, anchor="ne", height=_total_height)

    return _tree


def create_scoreboard(root: Tk) -> Treeview:
    """
    Создает таблицу счета в GUI, отображающую текущие очки обоих игроков.
    """
    _columns: tuple[str, str] = ("Игрок1 (Синий)", "Игрок2 (Красный)")

    _header_label: Label = Label(root, text="Счет", font=("Arial", 12, "bold"), bg="white", highlightthickness=0)
    _header_label.place(relx=1.0, rely=0.0, x=-400, y=110, anchor="ne")

    _tree: Treeview = ttk.Treeview(root, columns=_columns, show="headings")
    for col in _columns:
        _tree.heading(col, text=col)
        _tree.column(col, width=120, anchor="center")

    _tree.insert("", END, values=("Синий: 0", "Красный: 0"), tags=("blue", "red"))

    _tree.tag_configure("blue", foreground="darkblue")
    _tree.tag_configure("red", foreground="darkred")

    _num_rows: int = 1
    _row_height: int = 45
    _header_height: int = 30
    _total_height: int = _num_rows * _row_height + _header_height

    _tree.place(relx=1.0, rely=0.0, x=-300, y=140, anchor="ne", height=_total_height)

    return _tree


def create_rules(root: Tk) -> None:
    """
    Создает и отображает раздел с правилами игры в GUI.
    """
    _header_label: Label = Label(
        root,
        text="Правила игры",
        font=("Arial", 12, "bold"),
        bg="white",
        highlightthickness=0,
    )
    _header_label.place(relx=1.0, rely=0.0, x=-210, y=520, anchor="ne")

    _text_block: Text = Text(root, wrap=WORD, width=70, height=10, font=("Arial", 10))
    _text_block.insert(
        END,
        "Ход: игроки ходят поочерёдно, за один ход можно поставить только одну точку. Разрешено "
        "рисовать точки только на пересечении линий, где нет других знаков — в свободном поле.\n"
        "Цель: окружить точки соперника. Окружение — это создание на определённом участке игрового поля "
        "области, замкнутой внутри непрерывной непересекающейся цепи точек одного цвета, отстоящих друг "
        "от друга не более, чем на одну клетку по горизонтали, вертикали или диагонали.\n"
        "Захваченные точки: если в области, окружённой точками одного цвета, есть точки другого цвета, "
        "то точки соперника внутри неё выключаются из дальнейшей игры, считаясь захваченными, и идут в "
        "зачёт окружившему.\n"
        "Домик: если замыкается область, внутри которой нет точек соперника, она называется «домиком» и "
        "не является окружением. Такая область не закрашивается, а в пустые пункты внутри неё можно ставить "
        "точки.\n"
        "Подсчёт очков: по окончании игры производится подсчёт окружённых точек. Победителем считается "
        "игрок, захвативший хотя бы на одну точку больше, чем соперник. При равенстве по этому показателю "
        "объявляется ничья.",
    )
    _text_block.configure(state="disabled")
    _text_block.place(relx=0.0, rely=0.0, x=670, y=550, anchor="nw")

    _scrollbar: Scrollbar = Scrollbar(root, orient=VERTICAL, command=_text_block.yview)
    _scrollbar.place(relx=0.0, rely=0.0, x=1160, y=550, anchor="nw", height=160)
    _text_block.config(yscrollcommand=_scrollbar.set)
