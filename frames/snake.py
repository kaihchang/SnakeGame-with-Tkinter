from os import path
import sys  # these 2 are required to find the correct paths for pyinstaller
import tkinter as tk
from random import randint
from PIL import Image, ImageTk

# GLOBAL CONSTANTS
MOVE_INCREMENT = 20


class Snake(tk.Canvas):
    def __init__(self, container, *args, **kwargs):
        super().__init__(
            container, width=600, height=620, background="black", highlightthickness=0, *args, **kwargs
        )  # 'highlightthickness=0' is for getting rid of the default border of canvas

        self.container = container

        # body of the snake image is 20 pixels wide, we'll be placing 3 of them
        self.snake_positions = [(100, 100), (80, 100), (60, 100)]  # 頭 → 尾
        self.food_position = self.set_new_food_position()
        self.direction = "Right"  # initial direction, move_snake() will handle direction control

        # reset score and game speed
        self.score = 0

        self.moves_per_second = 15
        self.game_speed = 1000 // self.moves_per_second  # 66 moves initially

        self.load_assets(container)
        self.create_board()
        self.create_objects()

        self.bind_all("<Key>", self.on_key_press)  # <Key> includes every keypress

        self.pack()

        self.after(self.game_speed, self.perform_actions)

    # load images locally, but won't place it yet
    def load_assets(self, container):
        try:
            # 'path.join' is a cross-platform way of joining paths
            path_to_snake = path.join(container.bundle_dir, 'assets', 'snake.png')

            self.snake_body_image = Image.open(path_to_snake)
            self.snake_body = ImageTk.PhotoImage(self.snake_body_image)

            path_to_food = path.join(container.bundle_dir, 'assets', 'food.png')
            self.food_image = Image.open(path_to_food)
            self.food = ImageTk.PhotoImage(self.food_image)
        except IOError as error:  # if the file doesn't exist
            self.container.destroy()  # close up the whole root window
            raise  # print out the error

    # place the assets (images) into the window
    def create_board(self):
        self.create_text(
            80, 12,
            text=f"Score: {self.score}, Speed: {self.moves_per_second}",
            tag="score", fill="#fff",
            font=('Arial', 15)
        )

    def create_objects(self):
        # create snake body
        for x_position, y_position in self.snake_positions:
            self.create_image(  # built-in method of tk.Canvas
                x_position, y_position, image=self.snake_body, tag="snake"
            )  # tag property will be used to retrieve images from the Canvas

        # create food
        self.create_image(*self.food_position, image=self.food, tag="food")
        # *self.food_position = (self.food_position[0], self.food_position[1])
        self.create_rectangle(7, 27, 593, 613, outline="#525d69")  # create_rectangle(bbox, **options)
        # (7, 27) is the west-north 'start', (593, 613) is the east-south 'end' of the rectangle
        # create boundary for the window

    def check_collisions(self):
        head_x_position, head_y_position = self.snake_positions[0]
        return (
            head_x_position in (0, 600)  # 超出X軸邊界，X值為0或600時
            or head_y_position in (20, 620)  # 超出Y軸邊界，Y值為20或620時
            or (head_x_position, head_y_position) in self.snake_positions[1:]
            # 碰到自己時，頭的座標與身體重複時
        )  # 有以上狀況時，return True

    def on_key_press(self, event):
        # self.bind_all('<Key>') returns:
        # <KeyPress event state=Lock|Mod3|Mod4 keysym=Down keycode=8255233 char='\uf701' x=-5 y=-50>
        new_direction = event.keysym  # 'keysym' stands for key symbol

        all_directions = ("Up", "Down", "Left", "Right")
        opposites = ({"Up", "Down"}, {"Left", "Right"})  # 'sets' doesn't care about order, so {"Down, "Up"} also works

        if (
            new_direction in all_directions  # input needs to be one of the 4 directions
            and {new_direction, self.direction} not in opposites  # prevent opposite input from the snake's direction
        ):  # then we change the direction
            self.direction = new_direction

    def move_snake(self):
        head_x_position, head_y_position = self.snake_positions[0]

        if self.direction == "Left":  # X值減少
            new_head_position = (head_x_position - MOVE_INCREMENT, head_y_position)
        elif self.direction == "Right":  # X值增加
            new_head_position = (head_x_position + MOVE_INCREMENT, head_y_position)
        elif self.direction == "Down":  # Y值增加
            new_head_position = (head_x_position, head_y_position + MOVE_INCREMENT)
        elif self.direction == "Up":  # Y值減少
            new_head_position = (head_x_position, head_y_position - MOVE_INCREMENT)

        self.snake_positions = [new_head_position] + self.snake_positions[:-1]  # 增加一個新的（頭），去掉最後一個舊的（尾）

        # self.find_withtag(): find all the elements with the tag of 'snake', which is all the bodies of the snake
        # "zip" both the image and the position together, making a new tuple
        for segment, position in zip(self.find_withtag("snake"), self.snake_positions):
            # 'Canvas.coords' is a built-in method, it moves things to certain positions, put 1st object to 2nd position
            # more info: https://effbot.org/tkinterbook/canvas.htm
            self.coords(segment, position)

    def perform_actions(self):
        if self.check_collisions():
            self.end_game(self.container, self.score)  # 結束，下面不跑了

        self.check_food_collision()
        self.move_snake()

        self.after(self.game_speed, self.perform_actions)

    def check_food_collision(self):
        if self.snake_positions[0] == self.food_position:
            self.score += 1
            self.snake_positions.append(self.snake_positions[-1])
            # 接著，move_snake(): self.snake_positions = [new_head_position] + self.snake_positions[:-1]
            # append只會增加一個值，這個值在尾，與現存的尾得值相同；再增加一個新的（頭），去掉最後一個舊的（尾），但那個尾有兩個
            # 此程式移動只會根據方向加頭、去尾，因此少去一個尾等於蛇多走了一顆頭

            # increase speed when every 10 scores
            if self.score % 5 == 0:
                self.moves_per_second += 3
                self.game_speed = 1000 // self.moves_per_second

            self.create_image(
                *self.snake_positions[-1], image=self.snake_body, tag="snake"
            )  # 記得給留下的尾巴生成圖像
            self.food_position = self.set_new_food_position()
            self.coords(self.find_withtag("food"), *self.food_position)

            new_score = self.find_withtag("score")
            self.itemconfigure(
                new_score,
                text=f"Score: {self.score}, Speed: {self.moves_per_second}",
                tag="score"
            )

    def set_new_food_position(self):  # food needs to appear somewhere not in the snake's body
        while True:  # repeat endlessly until we break out
            x_position = randint(1, 29) * MOVE_INCREMENT  # 20 to 580 with the step of 20 # remember to import random
            y_position = randint(3, 30) * MOVE_INCREMENT  # 60 to 600 with the step of 20
            food_position = (x_position, y_position)

            if food_position not in self.snake_positions:
                return food_position
            else:
                pass

    def end_game(self, container, score):
        self.delete(tk.ALL)
        container.ask_restart(score)

