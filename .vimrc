"originally moodle's dev environment specs file for vim
" put this in your hoem directory as .vimrc/vimrc to let vim use it.

" insert space characters whenever the tab key is presse
set expandtab

" insert 4 spaces characters when tab key is pressed
set tabstop=4

" insert 4 spaces wen autoindent indents
set shiftwidth=4

" automatically indent files
set autoindent

" Do smart indentation depending on code syntax (e.g. change after { }, keywords etc)
set smartindent

" set syntax highlighting on
syntax on

" show a ruler with line number, % through file on status line
set ruler
" show line number
set nu
" PHP syntax check
set makeprg=php\ -l\ %
set errorformat=%m\ in\ %f\ on\ line\ %l

set statusline=%<%f\ %h%m%r%=%k[%{(&fenc==\"\")?&enc:&fenc}%{(&bomb?\",BOM\":\"\")}]\ %-14.(%l,%c%V%)\ %P

