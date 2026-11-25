
LEVELS = [
    {
            "name": "ステージ1",
            "map": [
        "#########",
        "#       #",
        "#  .    #",
        "#  $    #",
        "#  @    #",
        "#       #",
        "#########",
        ],
        "features": [],
    },
    {
        "name": "ステージ2",
        "rooms": {
        "A": [
        "##########",
        "#       $#",
        "#  $     #",
        "#        #",
        "#   @    #",
        "#        D",
        "##########",
        ],
        "B": [
        "##########",
        "#        #",
        "#        #",
        "#  $$    #",
        "#        #",
        "#        D",
        "##########",
        ]
        },
        "features": ["mirror"]
    },
    {
        "name": "ステージ3",
        "map": [
        "###########",
        "#         #",
        "#         #",
        "#    #    #",
        "#    #    #",
        "#  . # $  #",
        "#      @  #",
        "###########",
        ],
        "features": []
    },  

]

DIRECTIONS = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}

def parse_map(rows):#一つのマップを解析
    walls, goals, boxes, doors = set(), set(), set(), set()
    player = None

    if not rows:
        raise ValueError("マップが空です")

    width = len(rows[0])

    if any(len(row) != width for row in rows):
        raise ValueError("マップの行の長さをそろえてください")

    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            pos = (x, y)
            if ch == "#":
                walls.add(pos)
            elif ch == "D":
                doors.add(pos)
            elif ch in ".+*":
                goals.add(pos)

            if ch in "$*":
                boxes.add(pos)
            
            if ch in "@+":
                if player is not None:
                    raise ValueError("プレイヤーは1人にしてください")
                player = pos

    return {"walls": walls, "goals": goals, "boxes": boxes, "doors": doors, "player": player,
            "width": width, "height": len(rows), }

def load_level(level):#解析したマップを使って、ステージ全体を準備している
    if "mirror" in level["features"]: #ミラーが含まれているかどうか確認
        room_a = parse_map(level["rooms"]["A"])
        room_b = parse_map(level["rooms"]["B"])

        game = {
            "rooms": {
                "A": room_a,
                "B": room_b
            },
            "current_room": "A",
            "player": room_a["player"],
            "features": level["features"],
            "moves": 0,
            "history": []
        }
    else:
        room = parse_map(level["map"])

        game = {
            **room,
            "features": level["features"],
            "moves": 0,
            "history": []
        }

    return game


def draw_game(game):
    if "mirror" in game["features"]:
        room = game["rooms"][game["current_room"]]
    else:
        room = game

    print("\n" * 2 + "=== SOKOBAN ===")
    print("# 壁   . ゴール   $ 箱   @ プレイヤー   * ゴール上の箱")
    for y in range(room["height"]):
        line = ""
        for x in range(room["width"]):
            pos = (x, y)
            if pos == game["player"]:
                line += "+" if pos in room["goals"] else "@"
            elif pos in room["boxes"]:
                line += "*" if pos in room["goals"] else "$"
            elif pos in room["walls"]:
                line += "#"
            elif pos in room["doors"]:
                line += "D"
            elif pos in room["goals"]:
                line += "."
            else:
                line += " "
        print(line)
    if "mirror" in game["features"]:
        print(f"現在の部屋: {game['current_room']}")
    print(f"移動回数: {game['moves']} | WASD: 移動 / U: 一手戻す / R: リスタート / Q: 終了")


def inside(game, pos):
    return 0 <= pos[0] < game["width"] and 0 <= pos[1] < game["height"]


def move_player(game, key):
    if key not in DIRECTIONS:
        return False
    
    if "mirror" in game["features"]:
        room = game["rooms"][game["current_room"]]
    else:
        room = game

    dx, dy = DIRECTIONS[key]
    x, y = game["player"]
    target = (x + dx, y + dy)
    if not inside(game, target) or target in room["walls"]:
        return False
    
    pushed_to = None

    if target in room["boxes"]:
        if "mirror" in game["features"] and game["current_room"] == "A":
            return False
        pushed_to = (target[0] + dx, target[1] + dy)
        if (not inside(game, pushed_to) or pushed_to in room["walls"]
                or pushed_to in room["boxes"]):
            return False
    game["history"].append((game["player"], room["boxes"].copy()))
    if pushed_to is not None:
        room["boxes"].remove(target)
        room["boxes"].add(pushed_to)
    game["player"] = target
    game["moves"] += 1
    return True


def undo(game):
    if game["history"]:
        game["player"], game["boxes"] = game["history"].pop()
        game["moves"] -= 1


def is_cleared(game):
    if "mirror" in game["features"]:
        room_a = game["rooms"]["A"]
        room_b = game["rooms"]["B"]

        return room_a["boxes"] == room_b["boxes"]

    return game["boxes"] == game["goals"]


def main():
    level_index = 0
    game = load_level(LEVELS[level_index])
    while True:
        draw_game(game)
        if is_cleared(game):
            print("クリア！ 次のステージへ進みます。")
            level_index += 1
            if level_index == len(LEVELS):
                print("全ステージクリア！")
                break
            input("Enterを押して次へ...")
            game = load_level(LEVELS[level_index])
            continue
        key = input("操作 > ").strip().lower()[:1]
        if key == "q":
            break
        if key == "r":
            game = load_level(LEVELS[level_index])
        elif key == "u":
            undo(game)
        else:
            move_player(game, key)


if __name__ == "__main__":
    main()
