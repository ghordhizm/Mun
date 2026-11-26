# usage: chk.sh video out.jpg t1 t2 ...
V=$1; O=$2; shift 2; D=$(mktemp -d); i=0
for t in "$@"; do i=$((i+1)); ffmpeg -v error -y -ss $t -i $V -frames:v 1 -vf "scale=200:-2,drawtext=text='$t':x=4:y=4:fontsize=18:fontcolor=yellow:box=1:boxcolor=black" $D/$(printf %02d $i).jpg; done
ffmpeg -v error -y -i $D/%02d.jpg -filter_complex "tile=${i}x1:padding=3:color=white" $O
ffmpeg -i $V -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1
