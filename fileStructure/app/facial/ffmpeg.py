# ffmpeg を使って動画からフレームを抽出する

import cv2
import numpy as np
import subprocess#ffmpeg を Python から実行するため


def _split_pngs_from_bytes(data: bytes):
#「ここからPNGですよ」の合図
    PNG_SIG = b'\x89PNG\r\n\x1a\n'
    idx = 0

    while True:
        start = data.find(PNG_SIG, idx)
        if start == -1:
            break

        next_start = data.find(PNG_SIG, start + 8)
        if next_start == -1:
            yield data[start:]
            break
        else:
            yield data[start:next_start]
            idx = next_start


def extract_frames_every_n_sec_via_pipe(
    signed_url: str,#動画ファイルのURL
    interval_sec: int = 5#何秒ごとにフレームを抽出するか
):

    if interval_sec <= 0:
        interval_sec = 3

    fps = 1 / interval_sec
    #ffmpegさん、この動画を読んで、〇秒ごとにフレームを取り、PNG形式で、ファイルに保存せず、そのままPythonに流してください
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-i", signed_url,
        "-vf", f"fps={fps}",
        "-f", "image2pipe",
        "-vcodec", "png",
        "-"
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    out, err = proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(
            f"ffmpeg failed: {err.decode(errors='ignore')}"
        )

    frames = []
    time_sec = 0

    for png_bytes in _split_pngs_from_bytes(out):
        img = cv2.imdecode(
            np.frombuffer(png_bytes, np.uint8),
            cv2.IMREAD_COLOR
        )

        if img is not None:
            frames.append({
                "time_sec": time_sec,
                "image": img
            })
            time_sec += interval_sec  # 次のフレームの時刻

    return frames
