from openai import OpenAI

client = OpenAI(api_key="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")
import sys

#! 2つのGPTを使用
#! ２つ目のGPTでは，１つ目のGPTのプロンプトを作成する
#! ITの知識を使用して会話する


# openai.api_key = "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"
#openai.api_key = "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"
default_messages = [{"role": "system",
                     "content": "exam"},  # プロンプトを入力
                    ]

next_messages = default_messages





# chatGPTに音声認識結果を入力し，返答を得る
#! 引数：(string,prompt)
#! string:inputする会話
#! prompt:最初のプロンプトor作成したプロンプト 型:string
def chat1(prompt):
    #TODO 会話文を生成
    #TODO 入力：プロンプト
    #TODO 出力：会話文


    next_messages.append({"role": "user","content": prompt })

    res = client.chat.completions.create(model="gpt-4",
    messages=next_messages)
    #api_key=api_key


    # next_messages.append({"role": "assistant",
    #                       "content": res["choices"][0]["message"]["content"]})

    # GPTの返答
    return res["choices"][0]["message"]["content"]

def chat2(prompt):
    #TODO 会話文を生成
    #TODO 入力：プロンプト
    #TODO 出力：会話文
    #TODO 新しい話題に遷移するgpt

    next_messages.append({"role": "user","content": prompt })
    res = client.chat.completions.create(model="gpt-4",
    messages=next_messages)
    #api_key=api_key
    # next_messages.append({"role": "assistant",
    #                       "content": res["choices"][0]["message"]["content"]})
    # GPTの返答
    return res["choices"][0]["message"]["content"]

def chat_match(prompt):
    #TODO 会話文を生成
    #TODO 入力：プロンプト
    #TODO 出力：会話文
    #TODO 新しい話題に遷移するgpt

    next_messages.append({"role": "user","content": prompt })
    res = client.chat.completions.create(model="gpt-4",
    messages=next_messages)
    #api_key=api_key
    # next_messages.append({"role": "assistant",
    #                       "content": res["choices"][0]["message"]["content"]})
    # GPTの返答
    return res["choices"][0]["message"]["content"]

def chat_question(prompt):
    #TODO 会話文を生成
    #TODO 入力：プロンプト
    #TODO 出力：会話文
    #TODO 新しい話題に遷移するgpt

    next_messages.append({"role": "user","content": prompt })
    res = client.chat.completions.create(model="gpt-4",
    messages=next_messages)
    #api_key=api_key
    # next_messages.append({"role": "assistant",
    #                       "content": res["choices"][0]["message"]["content"]})
    # GPTの返答
    return res["choices"][0]["message"]["content"]

def chat2_1(prompt):
    #TODO 会話文を生成
    #TODO 入力：プロンプト
    #TODO 出力：会話文
    #TODO 新しい話題に遷移するgpt

    next_messages.append({"role": "user","content": prompt })
    res = client.chat.completions.create(model="gpt-4",
    messages=next_messages)
    #api_key=api_key
    # next_messages.append({"role": "assistant",
                        #   "content": res["choices"][0]["message"]["content"]})
    # GPTの返答
    return res["choices"][0]["message"]["content"]

def chat2_2(prompt):
    #TODO 会話文を生成
    #TODO 入力：プロンプト
    #TODO 出力：会話文
    #TODO 新しい話題に遷移するgpt

    next_messages.append({"role": "user","content": prompt })
    res = client.chat.completions.create(model="gpt-4",
    messages=next_messages)
    #api_key=api_key
    next_messages.append({"role": "assistant",
                          "content": res["choices"][0]["message"]["content"]})
    # GPTの返答
    return res["choices"][0]["message"]["content"]

def chat2_3(prompt):
    #TODO 会話文を生成
    #TODO 入力：プロンプト
    #TODO 出力：会話文
    #TODO 新しい話題に遷移するgpt

    next_messages.append({"role": "user","content": prompt })
    res = client.chat.completions.create(model="gpt-4",
    messages=next_messages)
    #api_key=api_key
    # next_messages.append({"role": "assistant",
    #                       "content": res["choices"][0]["message"]["content"]})
    # GPTの返答
    return res["choices"][0]["message"]["content"]

def chat3(question):
    # if input_text == "さようなら":
    #     sys.exit()
    #TODO 前の回答がどの質問項目に対応するのかを決定する
    #TODO 入力：会話文の最後の奇数行の文＋リスト
    #TODO 出力：「該当なし」or　該当する質問項目
    print("chat3の入力：" + str(question))
    next_messages.append({"role": "user",
                          "content": "質問項目を下に示します．以下の例に従って，質問が当てはまる項目の数字を答えてください．\nただし，該当する項目がなければ「該当なし」を回答してください．\n[質問項目]\n1. どのOSを使用してるか\\n\n 2. コンピュータで何をしているか\\n\n3. 1日に何時間くらいコンピュータを使用しているか\nQ：あなたはどのようなOSを使用していますか？\nA：1\n\nQ：現在、どのオペレーティングシステム（OS）を使用していますか？\nA：1\n\nQ：使用しているOSはなんですか？\nA：1\n\nQ：コンピュータでどのようなことをしていますか？\nA：2\n\nQ：1日にどのくらいコンピュータを使用しているのですか？\n A：3\n\nQ：使用しているパソコンのメーカーや型番、スペックについて教えてください．\nA：1\n\nQ：" + str(question) + "\nA："
    })
    res = client.chat.completions.create(model="gpt-4",
    messages=next_messages)
    #api_key=api_key
    # next_messages.append({"role": "assistant",
    #                       "content": res["choices"][0]["message"]["content"]})

    # GPTの返答
    return res["choices"][0]["message"]["content"]