#!/bin/bash

exist() {
    command -v $1 >/dev/null 2>&1 || { echo >&2 "$1 may be not installed. abort"; exit 1; }
}

exist vim
exist git

VIM_DIR=$HOME/.vim

if [[ ! -d $VIM_DIR ]]; then
    mkdir $VIM_DIR
fi

git clone https://github.com/gmarik/Vundle.vim $VIM_DIR/bundle/Vundle.vim

cp ./vimrc $HOME/.vimrc
cp ./vimrc.plugins $HOME/.vimrc.plugins

vim +PluginInstall +qall



