%include "&basedir\Main\Library\SAS\nobs\nobs.sas";

data first;
    INPUT x y z $;
    cards;
1  2.3  A
4  5.6  B
7  8.9  C
;
run;

title3 "nobs = %nobs(dsn=first)";

proc print data=first; run;