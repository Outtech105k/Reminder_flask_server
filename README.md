# Overview

AizuHack 2023 IoT部門作品のプロジェクトファイルです。
Python venv環境で、リマインダに必要なFlaskサーバを起動します。

# 使用方法
1. Python/pipのセットアップ
1. リポジトリのフォーク
1. カレントディレクトリ(flask_test)に移動
1. SQLite3データベースを準備(実行: `mv remind.db.sample remind.db`)
1. 仮想環境の作成 (参考リンク: https://fuji-pocketbook.net/python-venv/ )
1. 仮想環境モード(プロンプト先頭に(virtual)と表記されている状態)で実行: `python3 server.py` or `python server.py`
1. サーバ起動完了( 実行中にCtrl+Cで終了 ) ※開発モードに設定されているため、実行中もソースコードの変更に対応(不要なら変更推奨)

### エンドポイントの解説ファイル
https://docs.google.com/document/d/1CF46dFiHTKiAjP3NdTxM9gloXW1hBildQpgXdXkgbL8/edit?usp=sharing

### 参考リンク
https://elsammit-beginnerblg.hatenablog.com/entry/2021/06/03/230222

### LICENSE
[MIT LICENSE](LICENSE)を適用します。
