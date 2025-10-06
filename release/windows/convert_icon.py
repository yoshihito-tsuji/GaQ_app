from PIL import Image

# PNGファイルを読み込み
img = Image.open('src/static/icon.png')

# ICO形式で保存(複数サイズ)
img.save('src/icon.ico', format='ICO', sizes=[
    (256, 256),
    (128, 128),
    (64, 64),
    (32, 32),
    (16, 16)
])

print("icon.ico が作成されました")
