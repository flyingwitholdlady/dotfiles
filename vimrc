
"////////////////////////global///////////////////////////////

set nocompatible " be iMproved, required
silent exec 'language en_US'
set encoding=utf-8
set termencoding=utf-8
scriptencoding utf-8

" vundle#begin
filetype off " required

set rtp+=~/.vim/bundle/Vundle.vim/
call vundle#rc('~/.vim/bundle/')
" load .vimrc.plugins & .vimrc.plugins.local
let vimrc_plugins_path = '~/.vimrc.plugins'
if filereadable(expand(vimrc_plugins_path))
    exec 'source ' . fnameescape(vimrc_plugins_path)
endif
" vundle#end
filetype plugin indent on " required
syntax on " required

" Default colorscheme setup

set background=dark
colorscheme solarized
"let g:molokai_original = 1
"colorscheme molokai
highlight WhitespaceEOL ctermbg=red guibg=red
match WhitespaceEOL /\s\+$/

"/////////////////////////////////////////////////////////////////////////////
" General
"/////////////////////////////////////////////////////////////////////////////

" Redefine the shell redirection operator to receive both the stderr messages and stdout messages
set shellredir=>%s\ 2>&1
set history=30 " keep 30 lines of command line history
set autoread " auto read same-file change ( better for vc/vim change )
behave xterm  " set mouse behavior as xterm
set matchtime=0 " 0 second to show the matching paren ( much faster )
set nu " show line number
set relativenumber " show line number
" only supoort in 7.3 or higher
if v:version >= 703
    set noacd " no autochchdir
endif
set viewoptions=folds,options,cursor,unix,slash
set wildmenu " turn on wild menu, try typing :h and press <Tab>
set whichwrap=b,s,h,l,<,>,[,]
set list
set listchars=tab:>-,trail:•
set showcmd " display incomplete commands
set ruler " show the cursor position all the time
set hidden " allow to change buffer without saving
set shortmess=aoOtTI " shortens messages to avoid 'press a key' prompt
set lazyredraw " do not redraw while executing macros (much faster)
set display+=lastline " for easy browse last line with wrap text
set laststatus=2 " always have status-line
set titlestring=%F\ (%{expand(\"%:p:.:h\")}/)
set showfulltag " show tag with function protype.
set statusline=%F\ %y%r%m\ %{&ff}%=[Hex:0x%B][Dec:%b]\ %4l/%L\ %02p%%
set cc=81
set diffopt+=vertical
set cursorline
set cursorcolumn
set autoindent " autoindent
set smartindent " smartindent
set backspace=indent,eol,start " allow backspacing over everything in insert mode
" indent options
" see help cinoptions-values for more details
set	cinoptions=>s,e0,n0,f0,{0,}0,^0,:0,=s,l0,b0,g0,hs,ps,ts,is,+s,c3,C0,0,(0,us,U0,w0,W0,m0,j0,)20,*30
" default '0{,0},0),:,0#,!^F,o,O,e' disable 0# for not ident preprocess
" set cinkeys=0{,0},0),:,!^F,o,O,e
set cindent shiftwidth=4 " set cindent on to autoinent when editing c/c++ file, with 4 shift width
set tabstop=4 " set tabstop to 4 characters
set expandtab " set expandtab on, the tab will be change to space automaticaly
set ve=block " in visual block mode, cursor can be positioned where there is no actual character
set foldmethod=marker foldmarker={,} foldlevel=9999

set showmatch " show matching paren
set incsearch " do incremental searching
set hlsearch " highlight search terms
set ignorecase " set search/replace pattern to ignore case
set smartcase " set smartcase mode on, If there is upper case character in the search patern, the 'ignorecase' option will be override.
set nojoinspaces
" set this to use id-utils for global search
set grepprg=lid\ -Rgrep\ -s
set grepformat=%f:%l:%m
set fileencodings=utf-8,GB18030,ucs-bom,default,latin1
set clipboard=unnamed



if has('autocmd')
    augroup ex
        au!
        " when editing a file, always jump to the last known cursor position.
        " don't do it when the position is invalid or when inside an event handler
        " (happens when dropping a file on gvim).
        au BufReadPost *
                    \ if line("'\"") > 0 && line("'\"") <= line("$") |
                    \   exe "normal g`\"" |
                    \ endif
        au FileType text setlocal textwidth=78 " for all text files set 'textwidth' to 78 characters.
        au FileType vim set comments=sO:\"\ -,mO:\"\ \ ,eO:\"\",f:\"
        au FileType c,cpp,java,javascript set comments=sO:*\ -,mO:*\ \ ,exO:*/,s1:/*,mb:*,ex:*/,f://
    augroup END
endif


" copy - paste
noremap <Leader>p "+p
vmap <C-c> "+y

nmap <Leader>q :q<CR>
nmap <Leader>w :w<CR>

noremap <C-h> <C-W>h
noremap <C-j> <C-W>j
noremap <C-k> <C-W>k
noremap <C-l> <C-W>l

noremap H ^
noremap L g_

noremap k gk
noremap j gj
nnoremap [t gT
nnoremap ]t gt
nnoremap [c :cp <CR>
nnoremap ]c :cn <CR>

map <leader>tn :tabnew<cr>
map <leader>to :tabonly<cr>
map <leader>tc :tabclose<cr>
map <leader>tm :tabmove

inoremap ( ()<ESC>i
inoremap [ []<ESC>i
inoremap { {}<ESC>i
inoremap < <><ESC>i

