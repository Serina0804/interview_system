import socket
import json
import time
import argparse

M_SIZE = 1024

parser = argparse.ArgumentParser()
parser.add_argument('ip', help='IP address')
args = parser.parse_args()

serv_address = (args.ip, 9980)

# 送る姿勢データのサンプル
sample_msg_1 = {
    "info": "this is test message",
    "elapsedtime": 20,
    "timestamp": 20,
    "Waist_Y": 10,
    "RShoulder_P": 1000,
    "RElbow_P": 30,
    "LShoulder_P": -100,
    "LElbow_P": 50,
    "Head_Y": 0,
    "Head_P": 0,
    "Head_R": 0
}

def send_gesture():
    print("Send message")
    # サンプル：右肩・肘、頭を動かす
    for i in range(10):
        sample_msg_1["RShoulder_P"] = -90 + i * 40
        sample_msg_1["RElbow_P"] = 90 - i * 40
        sample_msg_1["Head_Y"] = -10 + i * 50
        msg_json = json.dumps(sample_msg_1).encode('utf-8')
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(msg_json, serv_address)
            print(f"Sent message: {msg_json}")
        time.sleep(0.05)  # ちょっと待つとロボット側も追従しやすい

if __name__ == '__main__':
    send_gesture()
