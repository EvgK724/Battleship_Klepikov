from random import randint


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Выстрел за границы поля боя"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Выстрел в эту область уже был"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'


class Ship:
    def __init__(self, prow, len_, orient):
        self.prow = prow
        self.length = len_
        self.orient = orient
        self.lives = len_

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.prow.x
            cur_y = self.prow.y

            if self.orient == 0:
                cur_x += i
            elif self.orient == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size

        self.count_ships = 0
        self.field = [[" 0"] * size for _ in range(size)]

        self.buzy = []
        self.ships = []

    def __str__(self):
        res = " "
        res += " | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} |" + " |".join(row) + " |"

        if self.hid:
            res = res.replace("▩", "0")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.buzy:
                    if verb:
                        self.field[cur.x][cur.y] = " ."
                    self.buzy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.buzy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = " ▩"
            self.buzy.append(d)
        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()
        if d in self.buzy:
            raise BoardUsedException()

        self.buzy.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = " X"
                if ship.lives == 0:
                    self.count_ships += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль повреждён!")
                    return True
        self.field[d.x][d.y] = " *"
        print("Мимо!")
        return False

    def begin(self):
        self.buzy = []

    def defeat(self):
        return self.count_ships == len(self.ships)


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            coords = input("Ваш ход: ").split()
            if len(coords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = coords

            if not(x.isdigit()) or not(y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.lens = [3, 2, 2, 1, 1, 1, 1]
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        board = Board(size=self.size)
        attempts = 0
        for l in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l,  randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print("-" * 27)
        print("  Морской бой начинается  ")
        print("         Готовы?        ")
        print("-" * 27)
        print("    Формат ввода: x y ")
        print("  x - строкa, y - столбец ")
        print("    Вводите два числa  ")
        print("        от 1 до 6")

    def print_boards(self):
        print("-" * 27)
        print("Ваше поле:")
        print(self.us.board)
        print("-" * 27)
        print("Поле компьютера:")
        print(self.ai.board)
        print("-" * 27)

    def loop(self):
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                repeat = self.us.move()
            else:
                repeat = self.ai.move()

            if repeat:
                num -= 1

            if self.ai.board.defeat():
                self.print_boards()
                print("Вы выиграли!")
                print("-" * 27)
                break

            if self.us.board.defeat():
                self.print_boards()
                print("Компьютер выиграл!")
                print("-" * 27)
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()