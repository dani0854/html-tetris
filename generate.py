import numpy as np
import random
from tqdm import tqdm
import os
import shutil

FIELD_HEIGHT = int(os.getenv("FIELD_HEIGHT", 5))
FIELD_WIDTH = int(os.getenv("FIELD_WIDTH", 4))

blocks = [
    np.atleast_2d((1,1,1,1)), # I
    
    np.atleast_2d(((1,0,0),   # J
                   (1,1,1))),
    
    np.atleast_2d(((0,0,1),   # L
                   (1,1,1))),
    
    np.atleast_2d(((1,1),     # O
                   (1,1))),
    
    np.atleast_2d(((0,1,1),   # S
                   (1,1,0))),
    
    np.atleast_2d(((0,1,0),   # T
                   (1,1,1))),
    
    np.atleast_2d(((1,1,0),   # Z
                   (0,1,1)))
]


class GameState:
    def __init__(self, field = np.zeros((FIELD_HEIGHT, FIELD_WIDTH)), block = None, hpos = 0):
        self.field = field
        self.block = blocks[random.randint(0,6)] if block is None else block
        self.hpos = hpos

    def render(self):
        top = np.zeros((4,FIELD_WIDTH))
        vlen = self.block.shape[0]
        hlen = self.block.shape[1]
        top[4-vlen:4,self.hpos:self.hpos+hlen] = self.block
        return np.concatenate((top, self.field))

    def rotate(self):
        if FIELD_WIDTH-self.hpos < np.rot90(self.block, 3).shape[1]:
            raise Exception("Out of bounds")
        return GameState(field = self.field, block = np.rot90(self.block, 3), hpos = self.hpos)

    def right(self):
        if FIELD_WIDTH-(self.hpos+1) < self.block.shape[1]:
            raise Exception("Out of bounds")
        return GameState(field = self.field, block = self.block, hpos = self.hpos+1)

    def left(self):
        if self.hpos-1 < 0:
            raise Exception("Out of bounds")
        return GameState(field = self.field, block = self.block, hpos = self.hpos-1)

    def down(self):
        vpos = self.__get_lowest_vpos()
        if vpos < 0:
            raise Exception("End of Game")
        vlen = self.block.shape[0]
        hlen = self.block.shape[1]
        new_field = self.field.copy()
        sub_field = new_field[vpos:vpos+vlen,self.hpos:self.hpos+hlen]
        new_field[vpos:vpos+vlen,self.hpos:self.hpos+hlen] = sub_field + self.block
        return GameState(new_field)
        
    def __get_lowest_vpos(self):
        vlen = self.block.shape[0]
        hlen = self.block.shape[1]
        vpos_max = FIELD_HEIGHT-vlen
        for vpos in range(vpos_max+1):
            test_sub_field = self.field[vpos:vpos+vlen,self.hpos:self.hpos+hlen]
            if np.max(test_sub_field + self.block) == 2:
                return vpos-1
        return vpos_max


def generate_html():
    create_dirs()
    first_state = generate_states()
    generate_start(first_state)
    generate_end(first_state)    

def create_dirs():
    if os.path.exists("static"):
        shutil.rmtree("static")
    os.mkdir("static")
    os.mkdir("static/state")

def generate_states():
    known_hashes = []
    new_game = GameState()
    queue = [ new_game ]
    first_state = f"hash" + str(hash(str(new_game.render()))) + ".html"

    pb = tqdm()
    done = 0
    
    while len(queue) > 0:
        state = queue.pop()
        links = {}

        pb.total = len(known_hashes)
        pb.refresh()
        
        for action in ["rotate", "right", "left", "down"]:
            try:
                result = getattr(state, action)()
                h = hash(str(result.render()))
                links[action] = f"hash{str(h)}.html"
                if h not in known_hashes:
                    queue.append(result)
                    known_hashes.append(h)
            except Exception as e:
                if str(e) == "End of Game":
                    links[action] = "../end.html"
                elif str(e) == "Out of bounds":
                    pass
                else:
                    raise e

        rendered = state.render()
        state_name = f"hash" + str(hash(str(rendered))) + ".html"

        table_html = "<table>\n"
        for row in rendered:
            table_html += "\t<tr>\n"
            for i in row:
                color = "black" if i == 1 else "gray"
                table_html += f"\t\t<td bgcolor=\"{color}\"><pre>    </pre></td>\n"
            table_html += "\t</tr>\n"
        table_html += "</table>\n"
        
        html = (
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<body>\n"
            "\n"
            "<h1>Tetris DFA on pure HTML</h1>\n"
            "\n"
            + table_html +
            "\n"
            "<a" + (" href=\"" + links["rotate"] + "\"" if "rotate" in links else "") + ">Rotate</a>\n"
            "<br>\n"
            "<a" + (" href=\"" + links["left"] + "\"" if "left" in links else "") + ">Left</a>\n"
            "<a" + (" href=\"" + links["right"] + "\"" if "right" in links else "") + ">Right</a>\n"
            "<br>\n"
            "<a" + (" href=\"" + links["down"] + "\"" if "down" in links else "") + ">Down</a>\n"
            "<br><br>\n"
            f"<a href=\"{first_state}\">Restart</a>\n"
            "\n"
            "</body>\n"
            "</html>"
        )

        with open("static/state/" + state_name, "w") as file:
            file.write(html)

        pb.update(1)

    return first_state
        

def generate_start(first_state):
    html = (
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<body>\n"
        "\n"
        "<h1>Tetris DFA on pure HTML</h1>\n"
        "\n"
        "<h2>Read more at <a href=\"https://github.com/dani0854/html-tetris\">github</a></h2>\n"
        "\n"
        f"<a href=\"state/{first_state}\">Start</a>\n"
        "\n"
        "</body>\n"
        "</html>"
    )
    with open("static/index.html", "w") as file:
        file.write(html)

def generate_end(first_state):
    html = (
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<body>\n"
        "\n"
        "<h1>Tetris DFA on pure HTML</h1>\n"
        "\n"
        "<h2>End of game</h2>\n"
        "\n"
        f"<a href=\"state/{first_state}\">Restart</a>\n"
        "\n"
        "</body>\n"
        "</html>"
    )
    with open("static/end.html", "w") as file:
        file.write(html)

generate_html()