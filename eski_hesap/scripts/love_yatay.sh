#!/bin/bash
# usage: SPEED=1 mkL2.sh out.mp4 letters.png "clip:in:out ..." outro_clip outro_in
R=/tmp/claude-0/-home-user-Mun/521f8cfe-2f47-55ee-947c-c97f3b0a55cf/scratchpad/deniz/raw
SP=${SPEED:-1}
OUT=$1; LET=$2; SEGS=($3); OC=$4; OI=$5
inp=(); fc=""; n=0; body=0
for s in "${SEGS[@]}"; do IFS=: read c a b <<< "$s"; inp+=(-ss $a -t $(echo "$b-$a"|bc) -i $R/$c.MP4); fc+="[$n:v]scale=1920:1080,setsar=1,setpts=(PTS-STARTPTS)/$SP,fps=30,eq=contrast=1.05:saturation=1.1[v$n];"; body=$(echo "$body+($b-$a)/$SP"|bc -l); n=$((n+1)); done
inp+=(-ss $OI -t 3.5 -i $R/$OC.MP4); fc+="[$n:v]scale=1920:1080,setsar=1,setpts=(PTS-STARTPTS)/$SP,fps=30,eq=contrast=1.05:saturation=1.1[v$n];"; n=$((n+1))
cat=""; for ((i=0;i<n;i++)); do cat+="[v$i]"; done
T=$(echo "$body+3.0"|bc -l)
fc+="${cat}concat=n=$n:v=1:a=0[cv];[$n:v]format=rgba[let];[cv][let]overlay=0:0[b1];"
fc+="[$((n+1)):v]format=rgba,fade=in:st=$(echo "$body+0.6"|bc -l):d=1.0:alpha=1[card];[b1][card]overlay=0:0,trim=0:$T,setpts=PTS-STARTPTS[vf];"
fc+="[$((n+2)):a]atrim=0:$T,asetpts=PTS-STARTPTS,apad=whole_dur=$T,afade=out:st=$(echo "$T-2.4"|bc -l):d=2.4,loudnorm=I=-14:TP=-1.5[af]"
ffmpeg -v error -y "${inp[@]}" -loop 1 -t $T -i $LET -loop 1 -t $T -i cardL.png -i ref.wav -filter_complex "$fc" -map '[vf]' -map '[af]' -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart $OUT && echo OK $OUT $T
