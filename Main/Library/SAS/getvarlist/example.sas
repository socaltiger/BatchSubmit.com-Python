%include "&basedir\Main\Library\SAS\getvarlist\getvarlist.sas";

data first;
    INPUT x y z $;
    cards;
1  2.3  A
4  5.6  B
7  8.9  C
;
run;

%GetVarList(work.first,Num,varlistn);

%GetVarList(work.first,Char,varlistc);

title3 "numeric vars: &varlistn";

title4 "character vars: &varlistc";

proc print data=first;
run;