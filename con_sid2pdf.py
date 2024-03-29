# -*- coding: utf-8 -*-
import os
import img2pdf
from traceback import print_exc
from PIL import Image
import imdirect
import re
import struct
import sys
#import comtypes.client

# 参考
# https://kapibara-sos.net/archives/866

#created_pdf_num = 0
MAX_PDF_NUM = 50  # 一度に多くのPDFをconvertするとPDFが破壊されるっぽいので上限を決めておく

# PDFをpdfフォルダに作成して，変換元のイメージをcompleteに移動する


def save_pdf(path_, item, ext_, dir_path_complete):
    #global created_pdf_num, MAX_PDF_NUM
    # if (created_pdf_num > MAX_PDF_NUM):
    #    print("一度に作成可能なPDFの数を超えました")
    #    return
    #created_pdf_num = created_pdf_num+1

    rep = re.compile(ext_, re.IGNORECASE)  # キャピタライズを無視して
    a4inpt = (img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297))
    layout_fun = img2pdf.get_layout_fun(a4inpt)
    img_pdf_bytes = img2pdf.convert(path_, layout_fun=layout_fun)
    save_pdf_file = re.sub(rep, '.pdf', item)
    # print("save_pdf_file:"+item+":ext_:"+ext_+":"+save_pdf_file)
    file = open(dir_path + "/pdf/" +
                save_pdf_file, "wb")
    file.write(img_pdf_bytes)
    file.close()
    path_complete = os.path.join(dir_path_complete, item)
    # print("move(save_pdf):"+path_+":"+"path_complete")
    move_to_complete(path_, path_complete)


def convert_png_jpg(path_, item, ext_, dir_path_complete):
    # pngをjpgに変換する
    rep = re.compile(ext_, re.IGNORECASE)  # キャピタライズを無視して
    input_image = Image.open(path_)
    rgb_image = input_image.convert('RGB')
    rgb_image_path = re.sub(rep, '.jpg', path_)
    # print("convert:"+rgb_image_path)
    rgb_image.save(rgb_image_path, quality=80)
    input_image.close()
    path_complete = os.path.join(dir_path_complete, item)
    # print("move(convert):"+path_+":"+"path_complete"+path_complete)
    move_to_complete(path_, path_complete)
    # item名の拡張子をjpgに変換（元のままだとpngのため，save_pdfでバグる）
    rgb_image_item = re.sub(rep, '.jpg', item)
    rgb_image_ext = re.sub(rep, '.jpg', ext_)

    save_pdf(rgb_image_path, rgb_image_item, rgb_image_ext, dir_path_complete)


def move_to_complete(orig, dest):
    # ファイルを指定した場所に移動する
    try:
        os.rename(orig, dest)
    except FileExistsError as fee:
        print(fee)
        print("orig:"+orig)
        print("dest:"+dest)


def convert_dir(dir_path, dir_path_pdf, dir_path_complete):
    # 指定したディレクトリ内の画像ファイルをPDFに変換してpdfフォルダに移動する
    # check input argument
    if os.path.isdir(dir_path):
        pdf_file_path = "{}.pdf".format(os.path.basename(dir_path))
        pdf_file_path = os.path.join(os.path.dirname(dir_path), pdf_file_path)
    else:
        raise Exception("invalid path")

    # convertできなかったイメージファイルのpathを入れるリスト
    images_ = []
    print("scanning directory: {}".format(dir_path))
    for item in os.listdir(dir_path):
        path_ = os.path.join(dir_path, item)
        if os.path.isfile(path_):
            ext_ = os.path.splitext(path_)[-1].lower()
            # print(ext_)
            try:
                if ext_ in [".jpg", ".jpeg"]:  # pngを取り除く（アルファチャンネルがどうとかでだめらしい
                    print("img_pdf:" + path_)
                    save_pdf(path_, item, ext_, dir_path_complete)
                elif ext_ in [".png"]:  # png to jpg
                    convert_png_jpg(path_, item, ext_, dir_path_complete)
                elif ext_ in [".pdf"]:  # pdf into complete dir
                    path_pdf = os.path.join(dir_path+'/pdf/', item)
                    move_to_complete(path_, path_pdf)
                elif ext_ in [".docx"]:
                    #convert_word_pdf(path_, dir_path_pdf, item, ext_, dir_path_complete)
                    pass
                else:
                    # skip non-image file
                    continue
            except img2pdf.ExifOrientationError as eoe:
              # これが原因でファイルが破壊されることがあるようなのでやめておく
                # print(eoe)
                # img_eoe = Image.open(path_)
                # print("{0}, Orientation: {1}".format(
                #     img_eoe, img_eoe._getexif().get(274)))
                # imdirect.monkey_patch()
                # img_eoe_rotated = Image.open(path_)
                # print("{0}, Orientation: {1}".format(
                #     img_eoe_rotated, img_eoe_rotated._getexif().get(274)))
                # img_eoe.close()
                # img_eoe_rotated.close()
                # print("eoe:img_pdf:" + path_)
                # save_pdf(path_, item, ext_, dir_path_complete)
                print("ExifOrientationError:" + str(eoe))
                images_.append(path_)

            except TypeError as te:
                print("TypeError:" + str(te))
                images_.append(path_)
            except ValueError as ve:
                print("ValueError:" + str(ve))
                images_.append(path_)
            except struct.error as se:
                print("struct.error:"+str(se))
                images_.append(path_)
            except SyntaxError as sye:
                print("SyntaxError:"+str(sye))
                images_.append(path_)

        else:
            # skip sub directory
            continue

    return images_
    # if len(images_) == 0:
    #     raise Exception("no image files")
    # else:
    #     images_.sort()

    # layout_ = img2pdf.get_layout_fun(params_.pagesize_)
    # print("copying skipped files: ...")


if __name__ == "__main__":
    args = sys.argv
    if (len(args) != 2):
        print("引数の数が間違っています")
        print("`python con_sid2pdf.py 画像フォルダ名` と入力してください")
        print("例: python con_sid2pdf.py cpuexama")
        sys.exit()

    try:
        dir_base = sys.argv[1]
        dir_path = dir_base + "/output"
        dir_path_pdf = dir_base + "/output/pdf"
        dir_path_complete = dir_base + "/output/complete"
        try:
            os.mkdir(dir_path_pdf)
        except FileExistsError:
            print(dir_path_pdf + " already exists")
        except FileNotFoundError as ffe:
            print(sys.argv[1] + "が見つかりません")
            sys.exit()

        try:
            os.mkdir(dir_path_complete)
        except FileExistsError:
            print(dir_path_complete+" already exists")

        images_ = convert_dir(dir_path, dir_path_pdf, dir_path_complete)
        if len(images_) == 0:
            print("All image files are converted to pdf")
        else:
            print(str(len(images_))+" image files are not converted")
            print("Please re-convert again")
            # プログラム中でコマンド再実行しても駄目だが，プログラム自体を再実行するとだいたいいける

    except BaseException:
        print_exc()
