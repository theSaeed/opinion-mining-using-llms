cp -r database.mpqa.2.0 database.mpqa.2.0.backup
patch -d database.mpqa.2.0 -p1 -u <utils/modifications.patch
mv database.mpqa.2.0 database.mpqa.2.0.cleaned
mv database.mpqa.2.0.backup database.mpqa.2.0
dir=$(pwd)
cd utils
os="$(uname)"
if [ "$os" == "Windows_NT" ]; then
    sep="\\\\"
else
    sep="/"
fi
python csds_cleaner.py "$dir$sep"
mv MPQA2.0_cleaned.json ../MPQA2.0_cleaned.json
cd ..