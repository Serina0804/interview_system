### 使用言語
<img src="https://img.shields.io/badge/-Flask-00000.svg?logo=flask&style=plastic">
<img src="https://img.shields.io/badge/-Python-3776AB.svg?logo=python&style=plastic">
<img src="https://img.shields.io/badge/-Javascript-F7DF1E.svg?logo=javascript&style=plastic">

## 目次

1. [プロジェクトについて](#プロジェクトについて)
2. [セットアップ](#セットアップ)
3. [環境](#環境)
4. [使い方](#使い方)
5. [注意点](#注意点)

## プロジェクトについて

大規模言語モデルを使用して、事前に用意した質問項目からインタビューを展開するシステム。</p>
質問項目から指定したトピックについての質問文を生成。</p>
質問項目分類モジュール、質問文生成モジュール、質問再判定モジュールの３つの機能で構成</p>

## ロボット

**ロボットを動かすコード：robot_gesture.py**

### 動かし方

**- ターミナルで　ssh root@SOTAのIPアドレス**
    **- パスワード：edison00**
**- binディレクトリで　./run.sh sotajsonconverter/SotaJsonConverter　を実行**
**- 新しいターミナルでパイソンファイルを実行（例：robot_gesture.py）**

### 概要

### 質問項目分類モジュール

質問項目リストに格納してある20の質問項目を、入力したトピックに関連するかどうかで分類する。

### 質問項目選択モジュール

質問文を生成するための質問項目を選択する。

### 質問文生成モジュール

質問項目選択モジュールで選択した質問項目について、入力したトピックに関連するように質問文を生成する。

## セットアップ
以下のPythonライブラリが必須．必要なPythonバージョンなどは調べること

openai
flask
flask_socketio

## 環境

<!-- 言語、フレームワーク、ミドルウェア、インフラの一覧とバージョンを記載 -->

Python、Flask、chatGPT

<p align="right">(<a href="#top">トップへ</a>)</p>

## 使い方

1.OPENAIのAPIkeyをtest_system.pyに入力 </br>
2.test_system.pyを実行 </br>
3.ターミナルにインタビュートピックを入力</br>
4.ターミナルに表示される質問項目について、トピックと関係あれば1、関係なければ2を入力する。</br>
5.Enterを押すとインタビューが始まるため、音声の質問に答える。</br>

## 注意点

ロボットSOTAと連動しているため、プログラムの入ったSOTAと接続しなければ実際に動かない。</br>
ロボットなしで実行する場合は、スレッドのコードをコメントアウトする。
