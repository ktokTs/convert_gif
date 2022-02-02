from itertools import count
import math

import cv2
from PIL import Image
from pathlib import Path

START = 0
END = 1

RED = '\033[31m'
GREEN = '\033[32m'
RESET = '\033[0m'

# 動画のfpsとフレーム数を返す
def get_fps_n_count(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return (None, None, None)

    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = round(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    cap.release()
    cv2.destroyAllWindows()
    return (fps, count, width)

# アスペクト比を返す
def aspect_ratio(width, height):
    gcd = math.gcd(width, height)
    ratio_w = width // gcd
    ratio_h = height // gcd
    return (ratio_w, ratio_h)

# アスペクト比を元にリサイズ後のwidth, heightを求める
def resize_based_on_aspect_ratio(aspect_ratio, base_width, max_width):
    if base_width < max_width:
        return None

    base = max_width / aspect_ratio[0]
    new_w = int(base * aspect_ratio[0])
    new_h = int(base * aspect_ratio[1])
    return (new_w, new_h)

# プログレスバーを表示
def print_progress(end, now, step):
    n = 20
    i = int(n * now / end)
    bar = '*' * i + " " * (n-i-1)
    print(f"\r\033[K[{bar}]", end="")
    if (now + step >= end):
        print()
    return

# 指定された範囲の画像をPillowのimage objectのリストにする
def get_frame_range(video_path, start_frame, stop_frame, step_frame, max_width):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    asp = aspect_ratio(width, height)

    width_height = resize_based_on_aspect_ratio(asp, width, max_width)

    im_list = []
    for n in range(start_frame, stop_frame, step_frame):
        print_progress(stop_frame, n, step_frame)
        cap.set(cv2.CAP_PROP_POS_FRAMES, n)
        ret, frame = cap.read()
        if ret:
            if width_height is not None:
                frame = cv2.resize(frame, dsize=width_height)
            img_array = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            im = Image.fromarray(img_array)
            im_list.append(im)

    cap.release()
    cv2.destroyAllWindows()
    return im_list

# gifを作る
def make_gif(filename, im_list, duration_time):
    im_list[0].save(filename, duration=duration_time, save_all=True, append_images=im_list[1:], loop=0, optimize=True)

# 入力を促して、変換前のファイル名取得
def get_filename():
    print(f"{GREEN}ファイル名を指定{RESET}")
    video_file = input()
    filename = Path(video_file).stem
    return video_file, filename

# 入力を促して、どこからどこまでをgifにするかを決める
def get_start_or_end_frame(fps, default, start_or_end):
    if (start_or_end == START):
        print(f"{GREEN}gif化する最初の秒数(空で最初から)：{RESET}")
    elif(start_or_end == END):
        print(f"{GREEN}gif化する最後の秒数(空で最後まで)：{RESET}")
    frame = 0
    sec_str = input()
    if (sec_str == ""):
        frame = default
    else:
        sec = int(sec_str)
        frame = int(sec * fps)
    return frame

# 入力を促して、gifのfpsを決める
def get_gif_frame(fps):
    print(f"{GREEN}gif化する際、何フレームごとに保存するか(空で3fps)：{RESET}")
    step_frame = 0
    step_frame_str = input()
    if (step_frame_str == ""):
        step_frame = int(fps / 3)
        if (step_frame <= 0):
            print(f"{RED}フレーム数が0になります{RESET}")
            return
    else:
        step_frame = int(step_frame_str)
    return step_frame

# 入力を促して、gifのサイズを決める
def get_resize(width):
    print(f"{GREEN}現在の横幅：", width,f"px{RESET}")
    print(f"{GREEN}どの程度縮小するか、px指定(空で960)：{RESET}")
    max_width_str = input()
    max_width = width
    if (max_width_str == ""):
        max_width = 960
    else:
        max_width = int(max_width_str)
    return max_width

# メイン処理
def main():
    video_file, filename = get_filename()

    fps, count, width= get_fps_n_count(video_file)
    if fps is None:
        print(f"{RED}動画ファイルを開けませんでした{RESET}")
        return

    max_width = get_resize(width)

    video_len = count / fps
    print(f"{GREEN}ビデオの長さ：", video_len, "s{RESET}")
    if (video_len >= 30):
        print(f"{RED}ビデオの長さが30秒以上のため、中断{RESET}")
        return

    # gifにしたい範囲を指定
    start_frame = get_start_or_end_frame(fps, 0, START)
    stop_frame = get_start_or_end_frame(fps, count, END)

    step_frame = get_gif_frame(fps)

    print(f"{GREEN}gif化開始{RESET}")
    im_list = get_frame_range(video_file, start_frame, stop_frame, step_frame, max_width)
    if im_list is None:
        print(f"{RED}動画ファイルを開けませんでした{RESET}")
        return

    make_gif(filename + '.gif', im_list, 1000 * step_frame / fps)
    print(f"{GREEN}終了{RESET}")


if __name__ == "__main__":
    main()