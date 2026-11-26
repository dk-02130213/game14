
# ステージごとのマップやルールをまとめる
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
        "description": "箱をすべてゴールに運べ！"
    },
    {
        "name": "ステージ2",
        "rooms": {
        "A": [
        "##########",
        "#       $#",
        "#  $     #",
        "#        #",
        "#        #",
        "#      @ D",
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
        "features": ["mirror"],
        "description": "部屋Aをお手本にして、部屋Bの箱を同じ位置に配置しろ！"
    },
    {
        "name": "ステージ3",
        "map": [
        "###########",
        "#         #",
        "#  @  $   #",
        "#IIIIIIIII#",
        "#IIIIIIIII#",
        "#IIIIIIIII#",
        "#IIII.IIII#",
        "###########",
        ],
        "features": ["ice"],
        "description": "床が滑る！！"
    },  
    {
    "name": "ステージ4",
    "rooms": {
        "A": [
            "###########",
            "#        $#",
            "# $       #",
            "#         #",
            "#         #",
            "#       @ D",
            "#    $    #",
            "###########",
        ],
        "B": [
            "###########",
            "#IIIIIIIII#",
            "#I  IIIIII#",
            "#II$IIIIII#",
            "##IIIIII$ #",
            "#IIIII$   D",
            "#III# I   #",
            "###########",
        ]
    },
    "features": ["mirror", "ice"],
    "description": "部屋Bの氷を利用して、部屋Aと箱の配置を一致させよう！"
},

]

# WASDキーごとの移動方向（横、縦）
DIRECTIONS = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}

def parse_map(rows):  # マップ文字列を座標データに変換する
    # 壁・ゴール・箱・扉・氷の座標を集合で保存する
    walls, goals, boxes, doors, ice = set(), set(), set(), set(), set()
    player = None  # プレイヤーの座標

    if not rows:  # 空のマップは解析できない
        raise ValueError("マップが空です")

    width = len(rows[0])  # 1行目からマップの横幅を得る
    # 行の長さがそろっていないマップはエラーにする
    if any(len(row) != width for row in rows):
        raise ValueError("マップの行の長さをそろえてください")

    # 各マスの文字を読み、種類ごとに座標を記録する
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            pos = (x, y)  # マスの座標（横、縦）
            if ch == "#":
                walls.add(pos)
            elif ch == "D":
                doors.add(pos)
            elif ch == "I":
                ice.add(pos)
            elif ch in ".+*":
                goals.add(pos)

            if ch in "$*":
                boxes.add(pos)

            if ch in "@+":
                if player is not None:
                    raise ValueError("プレイヤーは1人にしてください")
                player = pos

    # 解析結果とマップの大きさを辞書にして返す
    return {"walls": walls, "goals": goals, "boxes": boxes, "doors": doors, "ice": ice, "player": player,
            "width": width, "height": len(rows), }

def load_level(level):  # ステージのデータをゲーム用に準備する
    if "mirror" in level["features"]:  # ミラー形式なら両方の部屋を解析する
        room_a = parse_map(level["rooms"]["A"])
        room_b = parse_map(level["rooms"]["B"])

        game = {
            "rooms": {
                "A": room_a,
                "B": room_b
            },
            "current_room": "A",  # 最初に操作する部屋
            "player": room_a["player"],
            "features": level["features"],
            "description": level["description"],
            "moves": 0,  # 移動回数
            "history": []  # undo用の履歴
        }
    else:
        room = parse_map(level["map"])  # 通常形式のマップを解析する

        # 解析結果にステージ情報とゲームの状態を加える
        game = {
            **room,
            "features": level["features"],
            "description": level["description"],
            "moves": 0,
            "history": []
        }

    return game  # 準備したゲームデータを返す

def make_row(room, y, player):  # 部屋の指定した1行を文字列にする
    line = ""

    # 左から右へマスを確認し、表示する文字を追加する
    for x in range(room["width"]):
        pos = (x, y)

        if pos == player:
            line += "+" if pos in room["goals"] else "@"
        elif pos in room["boxes"]:
            line += "*" if pos in room["goals"] else "$"
        elif pos in room["walls"]:
            line += "#"
        elif pos in room["doors"]:
            line += "D"
        elif pos in room["ice"]:
            line += "I"
        elif pos in room["goals"]:
            line += "."
        else:
            line += " "

    return line  # できあがった1行を返す

def draw_game(game):  # ゲーム画面を表示する
    print("\n" * 2 + "=== SOKOBAN ===")
    print("クリア条件:", game["description"])
    print("# 壁   . ゴール   $ 箱   @ プレイヤー   D 出入口　I 氷")

    if "mirror" in game["features"]:
        # ミラー形式ではお手本と操作中の部屋を並べて表示する
        room_a = game["rooms"]["A"]
        room_b = game["rooms"]["B"]

        current = game["current_room"]

        print()
        print("部屋A：お手本          部屋B：操作する部屋")

        # プレイヤーは現在いる部屋にだけ表示する
        if current == "A":
            player_a = game["player"]
            player_b = None
        else:
            player_a = None
            player_b = game["player"]

        for y in range(room_a["height"]):
            line_a = make_row(room_a, y, player_a)
            line_b = make_row(room_b, y, player_b)

            print(line_a + "     " + line_b)

        print(f"\n現在の部屋: {current}")

    else:
        # 通常ステージはマップを1行ずつ表示する
        for y in range(game["height"]):
            print(make_row(game, y, game["player"]))

    print(f"移動回数: {game['moves']} | WASD: 移動 / U: 一手戻す / R: リスタート / Q: 終了")


def inside(game, pos):  # 座標がマップの範囲内か調べる
    return 0 <= pos[0] < game["width"] and 0 <= pos[1] < game["height"]


def move_player(game, key):  # キーに応じてプレイヤーを動かす
    if key not in DIRECTIONS:
        return False
    
    # 操作中の部屋を取り出す（通常ステージではgame自体が部屋）
    if "mirror" in game["features"]:
        room = game["rooms"][game["current_room"]]
    else:
        room = game

    # 移動先の座標を計算する
    dx, dy = DIRECTIONS[key]
    x, y = game["player"]
    target = (x + dx, y + dy)
    # マップ外や壁には移動できない
    if not inside(room, target) or target in room["walls"]:
        return False

    # ミラー形式で扉に入ったら、もう一方の部屋へ切り替える
    if "mirror" in game["features"] and target in room["doors"]:
        game["history"].append((
            game["current_room"],
            game["player"],
            room["boxes"].copy()
        ))

        if game["current_room"] == "A":#現在の部屋がAなら
            next_room = "B"#次をBに
        else:
            next_room = "A"#もしくはAに

        game["current_room"] = next_room#実際に部屋を切り替える
        game["player"] = target#プレイヤーを出入り口に
        game["moves"] += 1
        return True
    
    # 箱を押す場合の移動先を確認する
    pushed_to = None

    if target in room["boxes"]:
        # Mirrorの部屋Aでは箱を押せない
        if "mirror" in game["features"] and game["current_room"] == "A":
            return False

        pushed_to = (target[0] + dx, target[1] + dy)

        # 箱を1マス押せるか確認
        if (not inside(room, pushed_to)
                or pushed_to in room["walls"]
                or pushed_to in room["boxes"]):
            return False

        # Iceでは箱も滑る
        if "ice" in game["features"]:
            while pushed_to in room["ice"]:#箱を押した先が氷なら
                next_pos = (pushed_to[0] + dx, pushed_to[1] + dy)

                if (not inside(room, next_pos)
                        or next_pos in room["walls"]
                        or next_pos in room["boxes"]):
                    break

                pushed_to = next_pos

    # 移動前の状態を保存
    if "mirror" in game["features"]:
        game["history"].append((
            game["current_room"],
            game["player"],
            room["boxes"].copy()
        ))
    else:
        game["history"].append((
            None,
            game["player"],
            room["boxes"].copy()
        ))

    # 箱を移動させる
    if pushed_to is not None:
        room["boxes"].remove(target)
        room["boxes"].add(pushed_to)

    # Iceではプレイヤーも滑る
    if "ice" in game["features"]:
        while target in room["ice"]:
            next_pos = (target[0] + dx, target[1] + dy)

            if (not inside(room, next_pos)
                    or next_pos in room["walls"]
                    or next_pos in room["boxes"]):
                break

            target = next_pos

    # プレイヤーの位置を更新
    game["player"] = target
    game["moves"] += 1
    return True


def undo(game):  # 直前の移動を取り消す
    if not game["history"]:
        return

    # 履歴から一つ前の部屋・プレイヤー・箱の状態を取り出す
    previous_room, previous_player, previous_boxes = game["history"].pop()

    if "mirror" in game["features"]:
        game["current_room"] = previous_room  # 前にいた部屋へ戻す
        game["rooms"][previous_room]["boxes"] = previous_boxes  # 箱の位置を戻す
    else:
        game["boxes"] = previous_boxes

    game["player"] = previous_player  # プレイヤーを前の位置に戻す
    game["moves"] -= 1


def is_cleared(game):  # ステージのクリア条件を満たしたか調べる
    if "mirror" in game["features"]:
        room_a = game["rooms"]["A"]
        room_b = game["rooms"]["B"]

        # ミラー形式は両部屋の箱の位置が同じならクリア
        return room_a["boxes"] == room_b["boxes"]

    # 通常形式はすべての箱がゴール上ならクリア
    return game["boxes"] == game["goals"]


def main():  # ステージ進行とプレイヤー入力を管理する
    level_index = 0
    game = load_level(LEVELS[level_index])
    while True:
        draw_game(game)
        # クリア済みなら次のステージへ進む
        if is_cleared(game):
            print("クリア！ 次のステージへ進みます。")
            level_index += 1
            if level_index == len(LEVELS):
                print("全ステージクリア！")
                break
            input("Enterを押して次へ...")
            game = load_level(LEVELS[level_index])
            continue

        # 入力されたキーに応じて終了・再開・取り消し・移動を行う
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
    main()  # このファイルを直接実行したときにゲームを開始する
