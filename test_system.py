# from openai import OpenAI
import sys
import csv
import re
import random
from gtts import gTTS
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from scipy.io.wavfile import write
from scipy.io import wavfile
import pygame
import time
import socket
import argparse
import time
import json
import threading
from pydub import AudioSegment
import simpleaudio
from main2 import audio_recognize

# client = OpenAI(api_key="") #APIkeyを入力

M_SIZE = 1024

parser = argparse.ArgumentParser() 
parser.add_argument('ip', help='IP address')

args = parser.parse_args()

# Sending setting
serv_address = (args.ip, 9980)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Receiving msg setting
sock_recv_msg = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_recv_msg.bind(('', 9982))

# Receiving image setting
sock_recv_img = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_recv_img.bind(('', 9981))

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

#! トピックに関連するのと関連しないのを混ぜながら質問する
#! トピックに関連あり→関連なし
#!　関連なしの質問には再度判定する

default_messages = [{"role": "system",
                     "content": "exam"},  # プロンプトを入力
                    ]

next_messages = default_messages

interview_list_file_1 = "interview_list_system_1.csv"
interview_list_file_2 = "interview_list_system_2.csv"
random_question_1 = "random_question_system_1.csv"
random_question_2 = "random_question_system_2.csv"
interview_file_log = "interview_system_log.csv"
interview_question = "interview_question.csv"

#? 音声
def audio(string):
    language = "ja"
    filename = "gTTS_Text2Speech"
    text_to_speech(string, language, filename)

    mp3_filename = 'gTTS_Text2Speech.mp3'
    
    play_mp3(mp3_filename)
    
    return

def audio_thread_function(interview):
    try:
        print("Initializing pygame mixer...")
        pygame.mixer.init()

        # 以下はaudio関数の中身をそのまま移植
        print("Text to speech...")
        language = "ja"
        filename = "gTTS_Text2Speech"
        text_to_speech(interview, language, filename)

        # ここでsend_gesture()を呼び出す
        print("Sending gesture...")
        send_gesture()
        
        mp3_filename = 'gTTS_Text2Speech.mp3'  # 適切なファイル名に置き換えてください
        print("Loading mp3 file...")
        pygame.mixer.music.load(mp3_filename)

        print("Playing mp3...")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            continue



    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error in audio_thread_function: {e}")

    finally:
        print("Quitting pygame mixer...")
        # ここでpygame.mixer.quit()を呼び出す
        pygame.mixer.quit()
        print("Closing socket...")
        # ここでclose_socket()を呼び出す
        close_socket()





def play_mp3(mp3_filename):
    sound = AudioSegment.from_mp3(mp3_filename)
    playback_obj = simpleaudio.play_buffer(sound.raw_data, num_channels=sound.channels, bytes_per_sample=sound.sample_width, sample_rate=sound.frame_rate)
    playback_obj.wait_done()

def text_to_speech(text, language, filename):
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save(filename + ".mp3")

#? GPT操作
def classify_topic(prompt,question):
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
            "role": "system",
            "content": prompt
            },
            {
            "role": "user",
            "content": question
            },
        ],
        temperature=0,
        max_tokens=3691,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
    return res.choices[0].message.content

def judge_number(string , question):
    res = client.chat.completions.create(
        model="gpt-3.5-turbo-16k-0613",
        messages=[
            {
            "role": "system",
            "content": "assistantに複数の質問を示します．userの質問がこれらのうちどの質問に当てはまるかを判断してください．\nただし，数字のみの形式で回答してください．\n\n例：\nassistant\n1. きっかけは何ですか？\n2. 得意なことは何ですか？\n3. 近い将来やってみたいことはありますか？\n4. 今どこに住んでいますか？\n\nuser：楽しそうですね．今度弾いてみたい曲はありますか？\nA：3\n\nuser：そうなんですね．今どちらにいらっしゃいますか？\nA：4\n\n\n"
            },
            {
            "role": "assistant",
            "content": string
            },
            {
            "role": "user",
            "content": question
            },
        ],
        temperature=0,
        max_tokens=3691,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
    return res.choices[0].message.content

def judge_next_question(interviewer, topic, interview):
    res = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
            "role": "system",
            "content": "あなたは" + interviewer + "に" + topic + "に関してのインタビューをしています．\n今までのインタビュー会話を示します．\n次の質問に，" + topic + "に関係する質問か，関係しない質問のどちらをするのが良いか判定してください．\n関係する方がいい場合は，「1」だけを，関係しない方がいい場合は，「2」だけを答えてください．"
            },
            {
            "role": "user",
            "content": interview
            },
        ],
        temperature=0,
        max_tokens=3691,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
    # 生成されたテキストを取得
    return res.choices[0].message.content

def make_first_question(interviewer, topic , question):
    res = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
            "role": "system",
            "content": "あなたは" + interviewer + "に" + topic + "に関してのインタビューをしています．\nuserは次に質問したい質問項目です．\nuserの質問項目の質問をしてください．\nまた，30字以内に収めてください．"
            },
            {
            "role": "user",
            "content": question
            },
        ],
        temperature=0,
        max_tokens=3691,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
    # 生成されたテキストを取得
    return res.choices[0].message.content

def make_next_question(interviewer, topic,interview,question):
    res = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
            "role": "system",
            "content": "あなたは" + interviewer + "に" + topic + "に関してのインタビューをしています．\nassistantは今までのインタビューの履歴，userは今から質問したい項目です．\nassistantに続く，userの項目についての質問をしてください．ただし，質問文はわかりやすい文章にしてください．また，userの質問に対して回答しないでください，\n\nまた，20字以内に収めてください．"
            },
            {
            "role": "assistant",
            "content": interview
            },
            {
            "role": "user",
            "content": question
            },
        ],
        temperature=0,
        max_tokens=3691,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
    # 生成されたテキストを取得
    return res.choices[0].message.content


def make_next_reaction(interviewer, topic,interview):
    res = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
            "role": "system",
            "content": "あなたは" + interviewer + "に" + topic + "に関してのインタビューをしています．\nassistantは今までのインタビューの履歴です．\nassistantのインタビュー履歴の内容に対するリアクションをしてください．ただし，質問文にはしないでください．また，リアクションは20字以内にしてください．\n"
            },
            {
            "role": "assistant",
            "content": interview
            }
        ],
        temperature=0,
        max_tokens=3691,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
    # 生成されたテキストを取得
    return res.choices[0].message.content



def rejudge(interviewer , question):
    res = client.chat.completions.create(
        model="gpt-3.5-turbo-16k-0613",
        messages=[
            {
            "role": "system",
            "content": "あなたは" + interviewer + "にインタビューを行なっています．\nuserは質問項目です．userの質問項目を" + topic + "や" + interviewer + "についてのトピックに結びつけて質問可能かどうかを判定してください．\n\n可能なら「1」，不可能なら「2」とだけ答えてください．\n\n"
            },
            {
            "role": "user",
            "content": question
            },
        ],
        temperature=0,
        max_tokens=3691,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
    # 生成されたテキストを取得
    return res.choices[0].message.content

def topic_estimate(topic):
    res = client.chat.completions.create(
        model="gpt-3.5-turbo-16k-0613",
        messages=[
            {
            "role": "system",
            "content": topic + "から派生する話題を考えて「、」区切りで10個出力してください．\n\n各話題は「スポーツ」「読書」など具体的な一単語にしてください．\nまた，単語以外は出力しないでください．"
            }
        ],
        temperature=0,
        max_tokens=3691,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
    # 生成されたテキストを取得
    return res.choices[0].message.content

#? ファイル操作
def clear_file_contents(filename):
    # csvファイルを空にする
    with open(filename, 'w', newline='') as csvfile:
        # 空のデータを書き込むことでファイルの中身を削除
        pass

def count_csv_row(filename):
    # 行数を数えるカウンターを初期化
    row_count = 0

    # CSVファイルを開いて行数を数える
    with open(filename, newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            row_count += 1

    # print(f'CSVファイルの行数: {row_count} 行')
    return row_count

def find_and_output_number(input_str):
    # 正規表現を使用して文字列から数字を抽出
    numbers = re.findall(r'\d+', input_str)

    # 数字が見つかった場合、最初の数字を出力
    if numbers:
        # print(numbers[0])
        return int(numbers[0])
    else:
        print("数字は見つかりませんでした")
        return 1000

def get_list_from_csv_to_text(filename, index) :
    # 行を取得
    target_row = get_row(filename, index)
    return target_row

def get_row(csv_file, row_index):
    # 行を取得するための関数
    with open(csv_file, 'r', newline='') as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            if i == row_index:
                return row
    return None

def is_numeric(input_str):
    try:
        # 文字列を整数に変換できるか試みる
        int_value = int(input_str)
        
        # 変換できた場合、半角数字の文字列であるかを判定
        return int_value

    except ValueError:
        # 変換できない場合は半角数字の文字列ではない
        return False

def read_csv_text(filename):
    text_data = []

    with open(filename, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)

        for row in csvreader:
            if len(row) > 0:
                text_data.append(row[0])  # 1列目のデータをテキストとして取得

    return text_data

def write_string_to_csv(filename, input_string):
    # strをcsvファイルに書き込む
    with open(filename, mode="a", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        #csv_writer.writerow(['Text'])
        csv_writer.writerow([input_string])

def send_gesture():
    print("Send message")
    
    # ショルダーとエルボーの動作
    for i in range(10):
        sample_msg_1["RShoulder_P"] = -90 + i * 40
        sample_msg_1["RElbow_P"] = 90 - i * 40
        sample_msg_1["Head_Y"] = -10 + i * 50
        msg_json = json.dumps(sample_msg_1).encode('utf-8')
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(msg_json, serv_address)
            print(f"Sent message: {msg_json}")
    
    for i in range(10):
        sample_msg_1["RShoulder_P"] = 230 - i * 40
        sample_msg_1["RElbow_P"] = -230 + i * 40
        sample_msg_1["Head_Y"] = -10 + i * 50
        msg_json = json.dumps(sample_msg_1).encode('utf-8')
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(msg_json, serv_address)
            print(f"Sent message: {msg_json}")

    for i in range(10):
        sample_msg_1["LShoulder_P"] = -90 + i * 40
        sample_msg_1["LElbow_P"] = 90 - i * 40
        sample_msg_1["Head_Y"] = 10 - i * 50
        msg_json = json.dumps(sample_msg_1).encode('utf-8')
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(msg_json, serv_address)
            print(f"Sent message: {msg_json}")

    for i in range(10):
        sample_msg_1["LShoulder_P"] = 230 - i * 40
        sample_msg_1["LElbow_P"] = -230 + i * 40
        sample_msg_1["Head_Y"] = 10 - i * 50
        msg_json = json.dumps(sample_msg_1).encode('utf-8')
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(msg_json, serv_address)
            print(f"Sent message: {msg_json}")



def close_socket():
    global sock
    try:
        if sock is not None:
            sock.close()
    except Exception as e:
        print(f"Error in close_socket: {e}")


def receive_message():
    print("Receive message 5 packets")
    for i in range(5):
        rx_meesage, addr = sock_recv_msg.recvfrom(M_SIZE)
        print(f"[Server]: {rx_meesage.decode(encoding='utf-8')}")


if __name__ == '__main__':
    clear_file_contents(interview_list_file_1)
    clear_file_contents(interview_list_file_2)
    clear_file_contents(random_question_1)
    clear_file_contents(random_question_2)
    clear_file_contents(interview_file_log)
    send_gesture()
    
    topic = input("please input topic:") #interview topic
    interviewer = input("please input interviewer:")
    count_question = 0
    #! interview_question.csvの質問をトピックに関連するか分類
    file_row = count_csv_row(interview_question)
    print("関係する場合は1，関係しない場合は2を入れてください．")
    judge_1 = input("いつから始めましたか？:")
    judge_2 = input("今日は寒いと思いますか？:")
    judge_3 = input("普段誰と住んでいますか？:")
    judge_4 = input("誰の影響で始めましたか？:")
    prompt = "あなたは" + interviewer + "に" + topic + "に関してのインタビューを行なっています．\nuserは質問項目です．質問項目に対して，" + topic + "のトピックで使用できる質問なのかを判定してください．\n可能なら「1」，不可能なら「2」とだけ答えてください．\n\n例：\nQ：いつから始めましたか？\nA：" + judge_1 + "\n\nQ：今日は寒いと思いますか？\nA：" + judge_2 + "\n\nQ：普段誰と住んでいますか？\nA：" + judge_3 + "\n\nQ：誰の影響で始めましたか？\nA：" + judge_4
    interview_dictionary_1 = {}
    interview_dictionary_2 = {}
    interview_list_1 = []
    interview_list_2 = []
    index = 0
    t = 1
    re_count = 1
    # Eventオブジェクトを作成
    event = threading.Event()
    while True:
        if (index == file_row):
            break
        i = get_list_from_csv_to_text(interview_question, index)
        print("question_list:" , i[0] ,",index:" , index)
        result = classify_topic(prompt , i[0])
        # result = rejudge(interviewer , i[0])
        if (is_numeric(result) != False):
            result = int(result)
            if (result == 1):
                interview_dictionary_1[i[0]] = result
                interview_list_1.append(i[0])
                write_string_to_csv(interview_list_file_1,i[0])
            else :
                interview_dictionary_2[i[0]] = result
                interview_list_2.append(i[0])
                write_string_to_csv(interview_list_file_2,i[0])
            index = index + 1
        else :
            print("rejudge...:" , result)
            index = index + 1
        time.sleep(2)
    print(interview_list_1)
    print(interview_list_2)
    #? interview_list_1,interview_list_2からランダムで4個ずつ質問を抽出し，interview_1 , interview_2に入れる
    # ランダムに5つ選ぶ
    if len(interview_list_1) < 5:
        selected_questions_1 = interview_list_1
    else:
        selected_questions_1 = random.sample(interview_list_1, 5)
    another_list_1 = []
    for question in selected_questions_1:
        another_list_1.append(question)
        write_string_to_csv(random_question_1,question)
    another_list_2 = interview_list_2
    print("another_list_1:" , another_list_1)
    print("another_list_2:" , another_list_2)

    yes_no = input("これからインタビューを始めてもいですか？よければEnterを押してください．")
    #? 挨拶文
    interview = "こんにちは．私はインタビュアーロボットです．"
    print("robot:" , interview)

    # スレッドでaudio関数を実行
    audio_thread = threading.Thread(target=audio_thread_function, args=(interview,))
    audio_thread.start()
    audio_thread.join()  # スレッドの終了を待つ

    # 音声認識
    # answer = input("input something:")
    answer = audio_recognize()

    interview = "これからインタビューを始めます．よろしくお願いします．"
    print("robot:" , interview)

    # スレッドでaudio関数を実行
    audio_thread = threading.Thread(target=audio_thread_function, args=(interview,))
    audio_thread.start()
    audio_thread.join()  # スレッドの終了を待つ
    
    # write_string_to_csv(interview_log,interview)
    #TODO 音声認識
    # answer = input("input something:")
    answer = audio_recognize()
    # write_string_to_csv(interview_log,answer)

    while True:
        if (len(another_list_1) == 0 and len(another_list_2) == 0):
            audio_thread = threading.Thread(target=audio_thread_function, args=("インタビューありがとうございました．",))
            audio_thread.start()
            audio_thread.join()  # スレッドの終了を待つ
            break
        index = index + 1
        #? 関係あるか関係ないか会話ログから判定
        #! 会話ログを読み取る
        interview_log_list = read_csv_text(interview_file_log)
        interview_log = '\n'.join(interview_log_list) #会話履歴全体
        next_question_judge = 0
        if (len(another_list_1) != 0):
            next_question_judge = 1
        elif (len(another_list_1) == 0):
            next_question_judge = 2


        #? 質問を生成
        next_question_list = ""
        if (next_question_judge == 1) :
            next_question_list = random.sample(another_list_1, 1)
            next_question_root = next_question_list[0]
            print("t = " , t , "関連あり，項目：" , next_question_root)
            if (t == 1):
                next_question = make_first_question(interviewer, topic, next_question_root)
            else :
                next_reaction = make_next_reaction(interviewer,topic , interview_log)
                next_question_pre = make_next_question(interviewer,topic , interview_log , next_question_root)
                next_question = next_reaction + next_question_pre
            print("robot:" , next_question)
            count_question = count_question + 1
            # #!テキストを音声に変換
            # audio(next_question)
            
            # スレッドでaudio関数を実行
            audio_thread = threading.Thread(target=audio_thread_function, args=(next_question,))
            audio_thread.start()
            audio_thread.join()  # スレッドの終了を待つ
            
            write_string_to_csv(interview_file_log,next_question)
            #TODO 音声認識
            # answer = input("input something:")
            answer = audio_recognize()
            if (answer == ""): 
                if (t != 1):
                    print("robot:" , next_question_pre)
                    # スレッドでaudio関数を実行
                    audio_thread = threading.Thread(target=audio_thread_function, args=(next_question_pre,))
                    audio_thread.start()
                    audio_thread.join()  # スレッドの終了を待つ
                    #TODO 音声認識
                    # answer = input("input something:")
                    answer = audio_recognize()
                else :
                    print("robot:" , next_question)
                    # スレッドでaudio関数を実行
                    audio_thread = threading.Thread(target=audio_thread_function, args=(next_question,))
                    audio_thread.start()
                    audio_thread.join()  # スレッドの終了を待つ
                    #TODO 音声認識
                    # answer = input("input something:")
                    answer = audio_recognize()
            
            if (answer == "音声が認識できませんでした"):
                if (t != 1):
                    print("robot:" , next_question_pre)
                    # スレッドでaudio関数を実行
                    audio_thread = threading.Thread(target=audio_thread_function, args=(next_question_pre,))
                    audio_thread.start()
                    audio_thread.join()  # スレッドの終了を待つ
                    #TODO 音声認識
                    # answer = input("input something:")
                    answer = audio_recognize()
                else :
                    print("robot:" , next_question)
                    # スレッドでaudio関数を実行
                    audio_thread = threading.Thread(target=audio_thread_function, args=(next_question,))
                    audio_thread.start()
                    audio_thread.join()  # スレッドの終了を待つ
                    #TODO 音声認識
                    # answer = input("input something:")
                    answer = audio_recognize()
  
            if (answer != "音声が認識できませんでした"):
                write_string_to_csv(interview_file_log,answer)
            #TODO
            
            another_list_1.remove(next_question_root)
            print("after_remove_list_1:" , another_list_1)
            count = 0

        elif(next_question_judge == 2):
            next_question_list = random.sample(another_list_2, 1)
            next_question_root = next_question_list[0]
            print("t = " , t , "関連なし，項目：" , next_question_root)
            if (t == 1):
                next_question = make_first_question(interviewer,topic, next_question_root)
            else :
                next_reaction = make_next_reaction(interviewer,topic , interview_log)
                next_question_pre = make_next_question(interviewer,topic , interview_log , next_question_root)
                next_question = next_reaction + next_question_pre

            # print("robot_question:" , next_question)
            # i = rejudge(topic , next_question , formatted_text)
            i = rejudge(interviewer , next_question)
            while True :
                if (is_numeric(i) != False ):
                    i = int(i)
                    break
                else :
                    print("rejudge...:" , question_number)
                    count = count + 1
                    time.sleep(2)
                    if (count >= 2):
                        question_number = find_and_output_number(question_number)
                        if (question_number == 1000):
                            i = 2
                            break
            if (i == 1) :
                print("Yes...robot:" , next_question)
                count_question = count_question + 1
                #!テキストを音声に変換
                # audio(next_question)
                # スレッドでaudio関数を実行
                audio_thread = threading.Thread(target=audio_thread_function, args=(next_question,))
                audio_thread.start()
                audio_thread.join()  # スレッドの終了を待つ
                
                write_string_to_csv(interview_file_log,next_question)
                #TODO 音声認識
                # answer = input("input something:")
                answer = audio_recognize()
                if (answer == ""): 
                    if (t != 1):
                        print("robot:" , next_question_pre)
                        # スレッドでaudio関数を実行
                        audio_thread = threading.Thread(target=audio_thread_function, args=(next_question_pre,))
                        audio_thread.start()
                        audio_thread.join()  # スレッドの終了を待つ
                        #TODO 音声認識
                        # answer = input("input something:")
                        answer = audio_recognize()
                    else :
                        print("robot:" , next_question)
                        # スレッドでaudio関数を実行
                        audio_thread = threading.Thread(target=audio_thread_function, args=(next_question,))
                        audio_thread.start()
                        audio_thread.join()  # スレッドの終了を待つ
                        #TODO 音声認識
                        # answer = input("input something:")
                        answer = audio_recognize()
                
                if (answer == "音声が認識できませんでした"):
                    if (t != 1):
                        print("robot:" , next_question_pre)
                        # スレッドでaudio関数を実行
                        audio_thread = threading.Thread(target=audio_thread_function, args=(next_question_pre,))
                        audio_thread.start()
                        audio_thread.join()  # スレッドの終了を待つ
                        #TODO 音声認識
                        # answer = input("input something:")
                        answer = audio_recognize()
                    else :
                        print("robot:" , next_question)
                        # スレッドでaudio関数を実行
                        audio_thread = threading.Thread(target=audio_thread_function, args=(next_question,))
                        audio_thread.start()
                        audio_thread.join()  # スレッドの終了を待つ
                        #TODO 音声認識
                        # answer = input("input something:")
                        answer = audio_recognize()

                if (answer != "音声が認識できませんでした"):
                    write_string_to_csv(interview_file_log,answer)
            else :
                print("No...:" , next_question)
            another_list_2.remove(next_question_root)
            print("after_remove_list_2:" , another_list_2)
        t = t + 1
    print(count_question)