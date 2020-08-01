import os
import pandas as pd
import numpy as np
import re

# 参考
# https://qiita.com/tomotaka_ito/items/594ee1396cf982ba9887

# csvから学生番号と氏名（空白削除して）読み込み
df = pd.read_csv('./cpu2020.csv', encoding='cp932')
name_rd = []  # 名前からスペースを削除したもの

for row in df.itertuples():
    # print(row)
    name_space_reduced = ''.join(row[2].split())
    print(name_space_reduced)
    name_rd.append(name_space_reduced)

df['name_rd'] = name_rd  # spaceを削除した名前の列を追加

# imgファイル読み込み
# imgファイル末尾と同じ氏名を学生番号と氏名のリストから探す
# 見つけたら学生番号と氏名のリストのあとにファイル名を追加する
dir_path = "./exama"
output_path = "./exama/output"
try:
    os.mkdir(output_path)
except FileExistsError:
    print("output dir already exists")
    pass

images_ = []
for item in os.listdir(dir_path):
    path_ = os.path.join(dir_path, item)
    if os.path.isfile(path_):
        ext_ = os.path.splitext(path_)[-1].lower()
        if ext_ in [".jpg", ".jpeg", ".png", ".pdf"]:
            # pathだと./exama\\hoge_藤原 健人.jpegのようになる
            images_.append(item)
# print(images_)

for img in images_:
    img_rpd = re.sub('[0-9]+', '', img.replace(' ', ''))  # 半角スペースと数字を削除
    under = img_rpd.rfind('_') + 1  # 末尾からみた_の次の文字のindex
    period = img_rpd.rfind('.')  # 末尾から見た拡張子まで
    ext = img_rpd[period:len(img_rpd)]

    print("name_from_file:"+img_rpd[under:period])
    # ファイル名末尾の名前からスペースを削除した名前に一致する行だけTrueになったpandas.Series
    # https://note.nkmk.me/python-pandas-str-contains-match/
    name_mask = df['name_rd'] == img_rpd[under:period]
    num = 1
    # 該当する名前が名簿にない場合はSkip
    if (len(df[name_mask].index) == 0):
        print(img_rpd[under:period]+" has skipped!")
        continue
    # print(df[name_mask])
    while True:
        # print(num)
        try:
            # print(type(df.loc[name_mask, 'file' + str(num)]))
            # print(df.loc[name_mask, 'file' + str(num)])
            if (df.loc[name_mask, 'file' + str(num)].isnull().any()):
                pass
            else:
                num = num + 1
                continue
        except KeyError as ke:
            print(ke)
        except TypeError as te:
            print(te)
        # ファイル名を学生番号_通し番号のファイル名に変更
        df.loc[name_mask, 'file' + str(num)] = img
        ren_img = df.loc[name_mask, 'sid'] + '_' + f'{num:02}' + ext
        df.loc[name_mask, 'ren_file' + str(num)] = ren_img
        ren_img_str = df.loc[name_mask, 'ren_file' + str(num)].iat[0]
        print()

        img_path = os.path.join(dir_path, img)
        ren_img_path = os.path.join(output_path, ren_img_str)
        try:
            os.rename(img_path, ren_img_path)
        except FileExistsError as fee:
            print(fee)
        print(img_path)
        print(ren_img_path)

        break
    print(df[name_mask])

# ファイル名のRename

# print(df)
df.to_csv("cpu2020_file.csv", encoding='cp932')

# if __name__ == "__main__":
