dr=${0%/*} # ファイルのディレクトリを取得
cd "$dr"

python3 main.py 'IMGPATH1' 'IMGPATH2' 'IMGPATH3' -u 'YOUR_USERNAME' -p 'YOUR_PASSWORD' -c 'YOUR_CAPTION'