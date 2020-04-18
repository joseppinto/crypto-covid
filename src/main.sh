update=false
while getopts u option
do
  case "${option}"
  in
  u) update=true;;
  *) ;;
  esac
done

if ${update}
then
  echo -n "Updating dataset..."
  cd ../data
  python join_datasets.py
  echo "Done"

  echo -n "Preprocessing data..."
  cd ../src/learning/
  python data-preprocessing.py
  echo "Done"

  echo "Training models..."
  rm ../../data/predictions.txt
  for coin in bitcoin ethereum litecoin ripple
  do
    rm -rf logs/*
    echo -n "Training ${coin} model..."
    python train.py ${coin}
    echo "Done"

    echo -n "Making ${coin} prediction..."
    cd models/${coin}
    file=$(ls -1tr | tail -n -1)
    find . -maxdepth 1 -mindepth 1 ! -name "${file}" -exec rm -rf {} +
    cd ../../
    python predict.py ${coin} >> ../../data/predictions.txt
    echo "Done"
  done
  cd ../
fi

echo -n "Initializing front-end..."
cd front_end/
python front_end.py
echo "Bye bye"




