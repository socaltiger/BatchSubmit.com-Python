/*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}
Macro procedure GetVarList creates a list of all the character or numeric variables 
in the specified dataset.  The macro parameters are:

    datain  = Dataset to use.
    type    = Variable type (Num or Char).
    varlist = Macro variable returned containing the list of numeric or character variables.

Example:  
*%GetVarList(dataset,type,varlist);
%GetVarList(work.a,Num,varlist);

*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*}{*/

*Returns a list of Numeric(Num) or Character(Char) variables from the dataset;
%Macro GetVarList(dataset,type,mvarlist);
  %If %Checkdata(&dataset,Y) %Then %Do;
    %If %CheckStr(&type,Num Char,Choice,Y) %Then %Do;
      %Global &mvarlist;
      Ods Listing Select None;
      Ods Output Variables(Match_all Persist=Proc)=work._mmvars;
      Proc Contents Data=&dataset; Run;
      Ods Output Clear;
      Ods Listing Select All;
      Data work._mmakvars;
        Retain _mn 0;
        Set work._mmvars;
        If Upcase(type)=Upcase("&type") Then Do;
          _mn=_mn+1;
          Call Symput(Compress('var'||_mn),variable);
	End;
        Call Symput('mmax',Compress(_mn));
      Run;
      %Let mt=&mmax;
      %Let &mvarlist=;
      %Do _i=1 %To &mmax;
        %Let &mvarlist=&&&mvarlist &&&var&_i;
      %End;
      Proc Datasets Library=work Memtype=data NoDetails NoList;
        Delete _mmvars _mmakvars;
      Run;
    %End;
  %End;
%Mend GetVarList;

%Macro CheckData(dataset,Message);
  %Let dsid=%Sysfunc(Open(&dataset,Is));
  %If &dsid=0 %Then %Do;
    %Let checkdata=0;
    %If &Message=Y %then %Put ERROR: Dataset &dataset is not available.;
  %End; %Else %Do;
    %Let checkdata=1;
    %Let done=%Sysfunc(Close(&dsid));
  %End;
  &checkdata
%Mend CheckData;

%Macro CheckStr(value,choices,param,Message);
  %Let value=%Lowcase(&value);
  %Let choices=%Lowcase(&choices);
  %Let checkstr=0;
  %Let choice=%NextWord(choices);
  %Do %While (%Length(&choice)>0);
    %If "&value"="&choice" %Then %Let checkstr=1;
    %Let choice=%NextWord(choices);
  %End;
  %If &checkstr=0 %Then %Do;
    %If &Message=Y %then %put ERROR: Invalid option for &param in parameter list.;
  %End;
  &checkstr
%Mend checkStr;

%Macro NextWord(string);
  %Let space=%Index(&&&string,%Str( ));
  %Let size=%Length(&&&string);
  %If %Eval(&space)>0 %Then %Do; 
    %Let NextWord=%Substr(&&&string,1,&space); 
    %Let &string=%Substr(&&&string,&space+1,&size-&space); 
  %End; %Else %Do; %Let NextWord=&&&string; %Let &string= ; %End;
  &NextWord
%Mend NextWord;
