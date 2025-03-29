from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django.http import Http404, StreamingHttpResponse, HttpResponse

import requests as req, json
import cv2

import json, os

os.environ["NO_PROXY"] = "api.live.bilibili.com,bilibili.com,*.bilibili.com"

def index(request):
    return render(request, "live/index.html", {})


bilibili_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
}


def getm5u8url(m5u8id):
    try:
        res = req.get(
            f"https://api.live.bilibili.com/xlive/web-room/v2/index/getRoomPlayInfo?room_id={m5u8id}&no_playurl=0&mask=0&qn=0&platform=0&protocol=0,1&format=0,2&codec=0,1",
            headers=bilibili_headers, verify=False)
        if res.status_code != 200:
            return -1
        info = res.json()
        for stream in info['data']['playurl_info']['playurl']['stream']:
            if stream['protocol_name'] == 'http_hls':
                return stream['format'][0]['codec'][0]['url_info'][0]['host'] + stream['format'][0]['codec'][0][
                    'base_url']
        return -1
    except BaseException as e:
        # raise e
        return -1


print(os.getcwd())
file = open("./static/error.png", 'rb')
result = file.read()
file.close()


@csrf_exempt
@xframe_options_exempt
def live(request, m5u8id):
    m5u8url = getm5u8url(m5u8id)
    if m5u8url == -1:
        return HttpResponse(result, content_type='image/png')
    video = cv2.VideoCapture(m5u8url)

    def generate():
        while True:
            ret, frame = video.read()
            if not ret:
                video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = video.read()

            if not ret:
                break

                # 将图片转换为字节流
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')

