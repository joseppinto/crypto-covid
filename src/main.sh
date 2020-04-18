update=false
while getopts u option
do
  case "${option}"
  in
  u) update=true;;
  esac
done

if ${update}
then
  cd ../data
  python join_datasets.py

  cd ../src/learning/
  python data-preprocessing.py

  rm ../../data/predictions.txt
  for coin in bitcoin ethereum litecoin ripple
  do
    rm -rf logs/*
    python train.py ${coin}
    cd models/${coin}
    rm -v !($(ls -1tr | tail -n -1))
    cd ../../
    python predict.py ${coin} >> ../../data/predictions.txt
  done
  cd ../
fi

cd front_end/
python front_end.py




