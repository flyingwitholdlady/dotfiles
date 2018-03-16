#!/bin/bash

exist() {
    command -v $1 >/dev/null 2>&1 || { echo >&2 "$1 may be not installed. abort"; exit 1; }
}

exist vim
exist git
exist curl

VIM_DIR=$HOME/.vim

if [[ ! -d $VIM_DIR ]]; then
    echo "$VIM_DIR isn't exist, create directory"
    mkdir $VIM_DIR
fi


if [[ ! -f "$VIM_DIR/autoload/plug.vim" ]]; then
    curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
        https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
else
    echo 'plug have installed'
fi
VIMRC_DIFF=''

if [[ ! -f "$VIM_DIR/.vimrc" ]]; then
    echo 'ehllo'
    VIMRC_DIFF=`cmp vimrc $HOME/.vimrc`
fi

if [[ -n $VIMRC_DIFF ]]; then
    diff vimrc ~/.vimrc
    read -p 'replace vimrc  >' REPLACE

    if [[ $REPLACE = 'Y' ]]; then
        echo 'replace'
    else
        echo 'ignore'
    fi
fi


if [[ ! -f "$VIM_DIR/.vimrc.plugins" ]]; then
    echo 'ehllo'
    PLUGINS_DIFF=`cmp vimrc.plugins $HOME/.vimrc.plugins`
fi

if [[ -n $PLUGINS_DIFF ]]; then

    diff vimrc.plugins $HOME/.vimrc.plugins
    read -p 'replace vimrc.plugins  >' REPLACE
    if [[ $REPLACE = 'Y' ]]; then
        echo 'replace'
        vim +PlugInstall +qall
    else
        echo 'ignore'
    fi
fi


