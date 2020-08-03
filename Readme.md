# MS Forms/Google Formsに提出された画像ファイルを指定したフォーマットに一括変換するスクリプト
### 変更履歴
- 元のファイルで姓名がひっくり返っていた
  - 姓名と名姓の両パターンで検索を実施している
- 同名のファイルを同じ学生が一度にアップロードしている場合があった
  - ファイル名末尾に" 1.jpg"みたいに通し番号がつくっぽいのでファイル名から姓名を取り出すときに数字を正規表現を利用して削除した
- Value errorなどで変換に失敗した画像はそのまま残る．プログラムを再実行すると変換に成功する場合がある．

## ファイル構成
- ren_msfile2sid.py
  - MS Formsに提出されたファイルの名前を学生番号_通し番号.jpgなどに変換する
- ren_gfile2sid.py
  - Google Formsに提出されたファイルの名前を学生番号_通し番号.docxなどに変換する
- con_sid2pdf.py
  - 学生番号_通し番号.jpgや学生番号_通し番号.docxなどのファイルをPDFに変換する

## MS Formsに提出された画像ファイルのPDF変換
### 前提
- MS Formsを通して学生が提出するファイルは以下のようになる．
  - 0FBABF78-CCCB-4958-A17B-61BC43EF27D3_工大 太郎.jpeg
  - 0FBABF78-CCCB-4958-A17B-61BC43EF27D3_工大 太郎 1.jpeg
  - test_工大 花子.png
- これを以下のように学生番号_通し番号.pdfなファイルに変換する
  - X0111_1.pdf
  - X0111_2.pdf
  - X0123_1.pdf


### 準備
- 以下のようなフォーマットのcsvファイルを作成する
- 姓名の間に空白が含まれている必要がある
- ファイルはExcelからcsv出力されたcp932の文字コードであること

|sid	|name|
|----|----|
|B17000	|工大　太郎|
|B18999	|工大　花子|

- MS Formsで学生が提出したファイルをOneDriveからユーザがダウンロードする
- まとめてダウンロードしたファイルをユーザが解凍すると以下のようになっている．
  - ファイル名_学生の姓名.拡張子．という形式になっている．学生によっては名姓になっていることもあるので注意
  - フォームで提出するフォーマットとして画像を指定していれば，jpg,png,pdfなどが存在する．ファイル名部分は学生に依存するので，仮に同名のファイルが提出されていた場合，名前 1.jpegのように通し番号がつくっぽい
    - 0FBABF78-CCCB-4958-A17B-61BC43EF27D3_工大 太郎.jpeg
    - 0FBABF78-CCCB-4958-A17B-61BC43EF27D3_工大 太郎 1.jpeg
    - test_工大 花子.png

- プログラムと同じ箇所にフォルダを作成し，↑で解凍したファイルをすべてコピーする
- csvファイルをプログラムと同じ箇所に配置する

### ファイル名の変更(ren_msfile2sid.py)
- 準備で作成した学生番号と学生氏名が書かれたcsvファイル名，画像ファイルがあるフォルダ名を指定してプログラムを実行する
  - `python ren_msfile2sid.py cpu2020.csv exama`のように実行する
  - 第1引数が学生名簿のcsvファイル名，第2引数が画像等のファイルが格納されたディレクトリ名
- 画像ファイルがあるフォルダにあるファイルが指定したフォルダ/output に移動される
- 画像ファイルがあるフォルダ名.csvファイルに，どの学生がどのファイルを提出し，どうリネームされたかが記述される

## PDFファイルへの変更(con_sid2pdf.py)
- ren_....pyで指定した第2引数（画像フォルダ名）と同じものを第1引数に指定して実行する
  例 `python consid2pdf.py cpuexama`を実行する
- `画像フォルダ名/output`にある学生番号_通し番号.jpgなどの画像データがcompleteに移動され，同時にpdf化されたファイルがpdfフォルダに作成される
- 変換に失敗した画像データがある場合はoutputに残る．その場合，con_sid2pdf.pyを再実行すると正しく変換されることが有る．
