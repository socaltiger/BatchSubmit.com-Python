%macro nobs(dsn=);
    %let DSNID=%sysfunc(OPEN(&dsn.,IN));
    %let NOBS=%sysfunc(ATTRN(&DSNID,NOBS));
    %let RC=%sysfunc(CLOSE(&DSNID));
    &NOBS
%mend;