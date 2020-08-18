import os
import pandas as pd
import numpy as np
import re
import sys


def name_rdex(df):
    # 参考
    # https://qiita.com/tomotaka_ito/items/594ee1396cf982ba9887

    # csvから学生番号と氏名（空白削除して）読み込み，姓名，名姓の順に保存したデータセットを作成する

    name_rd = []  # 名前からスペースを削除したものを格納するリスト
    name_rdex = []  # 名前からスペースを削除して姓名を反転したものを格納するリスト

    for row in df.itertuples():
        # print(row)
        # print(row[2].split())
        name_space_reduced = ''.join(row[2].split())
        name_space_reduced_exchanged = row[2].split()[1]+row[2].split()[0]
        # print(name_space_reduced)
        name_rd.append(name_space_reduced)
        name_rdex.append(name_space_reduced_exchanged)

    df['name_rd'] = name_rd  # spaceを削除した名前の列を追加
    df['name_rdex'] = name_rdex  # spaceを削除して姓名を入れ替えた列を追加

    # print(df)
    return df


def getImages(dir_path):

    # イメージを順に読み込み，画像ファイルのファイル名だけをimages_に格納して返す関数

    images_ = []
    for item in os.listdir(dir_path):
        path_ = os.path.join(dir_path, item)
        if os.path.isfile(path_):
            ext_ = os.path.splitext(path_)[-1].lower()
            if ext_ in [".jpg", ".jpeg", ".png", ".pdf"]:
                # pathだと./exama\\hoge_藤原 健人.jpegのようになる
                images_.append(item)
    return images_


def getname_fromfile(img_):
    # イメージファイル名に含まれているユーザ名と拡張子を返す関数

    img_rpd = re.sub('[0-9]+|\s|　', '', img_)  # 半角スペース，全角スペースと数字を削除
    under = img_rpd.rfind('_') + 1  # 末尾からみた_の次の文字のindex
    period = img_rpd.rfind('.')  # 末尾から見た拡張子まで
    ext = img_rpd[period:len(img_rpd)]

    print("name_from_file:" + img_rpd[under:period])
    return img_rpd[under:period], ext


def rename_file_sid(images_, dir_path, output_path):
  # ファイル名を学生番号_通し番号.jpgのような形式に変更する
    for img in images_:
        img_info = getname_fromfile(img)
        # print(img_info)
        ext = img_info[1]
        mask1 = df['name_rd'] == img_info[0]  # ファイルに含まれるユーザ名と姓名が一致するデータ
        mask2 = df['name_rdex'] == img_info[0]  # ファイルに含まれるユーザ名と名姓が一致するデータ

        num = 1
        if (len(df[mask1].index) != 0):
            name_mask = mask1
        elif (len(df[mask2].index) != 0):
            name_mask = mask2
        else:
            print(img_info[0] + " has skipped!!!!!!")
            continue
        while True:
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

            img_path = os.path.join(dir_path, img)
            ren_img_path = os.path.join(output_path, ren_img_str)
            print("img_path:" + img_path)
            print("ren_img_path:" + ren_img_path)

            try:
                os.rename(img_path, ren_img_path)
            except FileExistsError as fee:
                print(fee)

            break
    return df


if __name__ == "__main__":
    args = sys.argv
    if (len(args) != 3):
        print("引数の数が間違っています")
        print("`python ren_msfile2sid.py 名簿ファイルのcsv 画像フォルダ名` と入力してください")
        print("例: python ren_msfile2sid.py cpu2020.csv cpuexama")
        sys.exit()

    # sidと学生名が入力された名簿
    try:
        df = pd.read_csv(sys.argv[1], encoding='cp932')
        df = name_rdex(df)
    except FileNotFoundError as ffe:
        print(ffe)
        print(sys.argv[1]+"が見つかりません")
        sys.exit()
    print(df)

    dir_path = sys.argv[2]
    output_path = dir_path + "/output"

    try:
        os.mkdir(output_path)
    except FileExistsError:
        print("output dir already exists")
    except FileNotFoundError:
        print(sys.argv[2] + "が見つかりません")
        sys.exit()

    images = getImages(dir_path)
    df = rename_file_sid(images, dir_path, output_path)
    df.to_csv(sys.argv[2]+".csv", encoding='cp932')
