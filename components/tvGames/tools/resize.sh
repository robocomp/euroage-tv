mkdir newfiles
for f in $(find . -maxdepth 1 -iname '*.mp4'); 
do 
	ffmpeg -i "$f" "newfiles/$f";
done
mogrify -resize 1920x1080 -quality 80 -path newfiles *.jpg
