#!/bin/sh

# files all tag,  -f files, -d dirctory  -v verbose

OUTFILE='cscope.files'
C_FILES=('*.h' '*.c' '*.m' '*.mm')
CPP_FILES=('*.cpp' '*.h' '*.cc' '*.hxx' '*.hpp' '*.h')

declare -a others
declare -a dirs
declare -a paths

paths=(`pwd`)

while  getopts "f:d:v" opt
do
    case "$opt" in
        f)
            others+=($OPTARG);;
        d)
            dirs+=($OPTARG);;
        v)
            verbose=1;;
        \? | *)
            echo "Usage: args [-f file] [-d directory] [-v]"
            echo "-f addon file"
            echo "-d addon directory"
            echo "-v verbose"
            exit 1;;
    esac
done

allfiles=(${C_FILES[@]} ${CPP_FILES[@]} ${others[@]})

if [[ ${#dirs[@]} -ne 0 ]]; then
    # used default (pwd)
    paths=(${dirs[@]})
fi

command="find ${paths[@]} "
command+='\( '
for (( i = 0; i < ${#allfiles[@]}; i++ )); do
    command+="-name \"${allfiles[$i]}\" "

    if [[ i -ne ${#allfiles[@]}-1 ]]; then
        command+='-o '
    fi
done
command+="\) -print > ${OUTFILE}"

if [[ verbose -eq 1 ]]; then
    echo  "$command"
fi

#i don't know why this command can't run correctly,
# another way to walk around it
echo ${command} > dump.sh
bash dump.sh
rm dump.sh



