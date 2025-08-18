n=$1
ef="${@:2}"
out_dir=$3

for tc in tcOneNode tcTwoNodes tcThreeNodes tcFiveNodes tcTenNodes
do
    if ((${#ef} == 0))
    then
        echo "Run $tc with $n schedules for all events"
        p check -tc $tc -s $n --pinfer -tf $out_dir/$(($n*5))
    else
        echo "Run $tc with $n schedules with events $ef"
        p check -tc $tc -s $n -ef $ef --pinfer -tf $out_dir/$(($n*5))
    fi
done
echo "Finished"