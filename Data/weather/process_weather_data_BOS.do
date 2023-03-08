* Import Detroit temp data:
import delimited using "C:\Users\atpha\Documents\Postdocs\Projects\TES\Data\weather\BOS.csv", clear
rename valid date

gen date_convert = date(date, "YMDhm")
format date_convert %tc
gen year = year(date_convert)
gen month = month(date_convert)
rename date date_orig
gen date = day(date_convert)

gen double time = clock(date_orig, "YMDhm")
format time %tc
gen hour = hh(time)

drop date_convert time

replace hour = hour+1

* Remove duplicated hours:
duplicates drop date_orig, force 

sort year month date hour

* Clean and fill in missing data points:
* Use tab hour if month==1
*** Jan: 
* missing hour 1 of day 7:
expand 2 if (date==6 & month==1 & hour==24), gen(dupindicator)
replace hour = 1 if dupindicator == 1
replace date = 7 if dupindicator == 1
drop dupindicator
* missing hour 3 of day 31:
expand 2 if (date==31 & month==1 & hour==2), gen(dupindicator)
replace hour = 3 if dupindicator == 1
drop dupindicator
* missing hour 7 of day 21:
expand 2 if (date==21 & month==1 & hour==6), gen(dupindicator)
replace hour = 7 if dupindicator == 1
drop dupindicator
* missing hour 9 of day 22:
expand 2 if (date==22 & month==1 & hour==8), gen(dupindicator)
replace hour = 9 if dupindicator == 1
drop dupindicator
* missing hour 13 of day 24:
expand 2 if (date==24 & month==1 & hour==12), gen(dupindicator)
replace hour = 13 if dupindicator == 1
drop dupindicator
* missing hour 22 of day 12:
expand 2 if (date==12 & month==1 & hour==21), gen(dupindicator)
replace hour = 22 if dupindicator == 1
drop dupindicator
* missing hour 24 of day 28:
expand 2 if (date==28 & month==1 & hour==23), gen(dupindicator)
replace hour = 24 if dupindicator == 1
drop dupindicator

sort year month date hour


*** Feb:
* missing hour 8 of day 10:
expand 2 if (date==10 & month==2 & hour==7), gen(dupindicator)
replace hour = 8 if dupindicator == 1
drop dupindicator
* missing hour 8 of day 25:
expand 2 if (date==25 & month==2 & hour==7), gen(dupindicator)
replace hour = 8 if dupindicator == 1
drop dupindicator
* missing hour 14 of day 19:
expand 2 if (date==19 & month==2 & hour==13), gen(dupindicator)
replace hour = 14 if dupindicator == 1
drop dupindicator
* missing hour 19 of day 23:
expand 2 if (date==23 & month==2 & hour==18), gen(dupindicator)
replace hour = 19 if dupindicator == 1
drop dupindicator
* missing hour 24 of day 6:
expand 2 if (date==6 & month==2 & hour==23), gen(dupindicator)
replace hour = 24 if dupindicator == 1
drop dupindicator
sort year month date hour


*** March:
* missing hour 3 in day 3
expand 2 if (date==3 & month==3 & hour==2), gen(dupindicator)
replace hour = 3 if dupindicator == 1
drop dupindicator
* missing hour 3 in day 7
expand 2 if (date==7 & month==3 & hour==2), gen(dupindicator)
replace hour = 3 if dupindicator == 1
drop dupindicator
* missing hour 3 in day 11
expand 2 if (date==11 & month==3 & hour==2), gen(dupindicator)
replace hour = 3 if dupindicator == 1
drop dupindicator
* missing hour 4 in day 26
expand 2 if (date==26 & month==3 & hour==3), gen(dupindicator)
replace hour = 4 if dupindicator == 1
drop dupindicator
* missing hour 5 in day 14
expand 2 if (date==14 & month==3 & hour==4), gen(dupindicator)
replace hour = 5 if dupindicator == 1
drop dupindicator
* missing hour 9 in day 12
expand 2 if (date==12 & month==3 & hour==8), gen(dupindicator)
replace hour = 9 if dupindicator == 1
drop dupindicator
* missing hour 10 in day 4
expand 2 if (date==4 & month==3 & hour==9), gen(dupindicator)
replace hour = 10 if dupindicator == 1
drop dupindicator
* missing hour 15 in day 8
expand 2 if (date==8 & month==3 & hour==14), gen(dupindicator)
replace hour = 15 if dupindicator == 1
drop dupindicator
* missing hour 17 in day 19
expand 2 if (date==19 & month==3 & hour==16), gen(dupindicator)
replace hour = 17 if dupindicator == 1
drop dupindicator
* missing hour 21 in day 5
expand 2 if (date==5 & month==3 & hour==20), gen(dupindicator)
replace hour = 21 if dupindicator == 1
drop dupindicator
* missing hour 23 in day 11
expand 2 if (date==11 & month==3 & hour==22), gen(dupindicator)
replace hour = 23 if dupindicator == 1
drop dupindicator
* missing hour 24 in day 9
expand 2 if (date==9 & month==3 & hour==23), gen(dupindicator)
replace hour = 24 if dupindicator == 1
drop dupindicator
sort year month date hour

*** Apr:
* missing hour 24 of day 10
expand 2 if (date==10 & month==4 & hour==23), gen(dupindicator)
replace hour = 24 if dupindicator == 1
drop dupindicator
* missing hour 1 of day 11
expand 2 if (date==10 & month==4 & hour==24), gen(dupindicator)
replace hour = 1 if dupindicator == 1
replace date = 11 if dupindicator == 1
drop dupindicator
* missing hour 3 of day 18
expand 2 if (date==18 & month==4 & hour==2), gen(dupindicator)
replace hour = 3 if dupindicator == 1
drop dupindicator
* missing hour 13 of day 21
expand 2 if (date==21 & month==4 & hour==12), gen(dupindicator)
replace hour = 13 if dupindicator == 1
drop dupindicator
* missing hour 14 of day 3
expand 2 if (date==3 & month==4 & hour==13), gen(dupindicator)
replace hour = 14 if dupindicator == 1
drop dupindicator
* missing hour 14 of day 18
expand 2 if (date==18 & month==4 & hour==13), gen(dupindicator)
replace hour = 14 if dupindicator == 1
drop dupindicator
* missing hour 15 of day 29
expand 2 if (date==29 & month==4 & hour==14), gen(dupindicator)
replace hour = 15 if dupindicator == 1
drop dupindicator
sort year month date hour

*** May:
* Missing hour 1 of days 9,10,18
expand 2 if (date==8 & month==5 & hour==24), gen(dupindicator)
replace hour = 1 if dupindicator == 1
replace date = 9 if dupindicator == 1
drop dupindicator
expand 2 if (date==9 & month==5 & hour==24), gen(dupindicator)
replace hour = 1 if dupindicator == 1
replace date = 10 if dupindicator == 1
drop dupindicator
expand 2 if (date==17 & month==5 & hour==24), gen(dupindicator)
replace hour = 1 if dupindicator == 1
replace date = 18 if dupindicator == 1
drop dupindicator
* missing hour 2 of days 9,10
expand 2 if (date==9 & month==5 & hour==1), gen(dupindicator)
replace hour = 2 if dupindicator == 1
drop dupindicator
expand 2 if (date==10 & month==5 & hour==1), gen(dupindicator)
replace hour = 2 if dupindicator == 1
drop dupindicator
* missing hour 3 of day 9
expand 2 if (date==9 & month==5 & hour==2), gen(dupindicator)
replace hour = 3 if dupindicator == 1
drop dupindicator
* missing hour 8 of day 16
expand 2 if (date==16 & month==5 & hour==7), gen(dupindicator)
replace hour = 8 if dupindicator == 1
drop dupindicator
* missing hour 10 of day 15
expand 2 if (date==15 & month==5 & hour==9), gen(dupindicator)
replace hour = 10 if dupindicator == 1
drop dupindicator
* missing hour 11 of day 26
expand 2 if (date==26 & month==5 & hour==10), gen(dupindicator)
replace hour = 11 if dupindicator == 1
drop dupindicator
sort year month date hour

*** June:
* missing hour 4 of day 12
expand 2 if (date==12 & month==6 & hour==3), gen(dupindicator)
replace hour = 4 if dupindicator == 1
drop dupindicator
* missing hour 14 of day 22
expand 2 if (date==22 & month==6 & hour==13), gen(dupindicator)
replace hour = 14 if dupindicator == 1
drop dupindicator
* missing hour 15 of day 8
expand 2 if (date==8 & month==6 & hour==14), gen(dupindicator)
replace hour = 15 if dupindicator == 1
drop dupindicator
* missing hour 15 of day 14
expand 2 if (date==14 & month==6 & hour==14), gen(dupindicator)
replace hour = 15 if dupindicator == 1
drop dupindicator
* missing hour 21 of day 18
expand 2 if (date==18 & month==6 & hour==20), gen(dupindicator)
replace hour = 21 if dupindicator == 1
drop dupindicator
* missing hour 24 of day 15
expand 2 if (date==15 & month==6 & hour==23), gen(dupindicator)
replace hour = 24 if dupindicator == 1
drop dupindicator
sort year month date hour

*** Jul:
* missing hour 2 of day 4
expand 2 if (date==4 & month==7 & hour==1), gen(dupindicator)
replace hour = 2 if dupindicator == 1
drop dupindicator
* missing hour 2 of day 17
expand 2 if (date==17 & month==7 & hour==1), gen(dupindicator)
replace hour = 2 if dupindicator == 1
drop dupindicator
* missing hour 4 of day 17
expand 2 if (date==17 & month==7 & hour==3), gen(dupindicator)
replace hour = 4 if dupindicator == 1
drop dupindicator
* missing hour 6 of day 29
expand 2 if (date==29 & month==7 & hour==5), gen(dupindicator)
replace hour = 6 if dupindicator == 1
drop dupindicator
* missing hour 10 of day 14
expand 2 if (date==14 & month==7 & hour==9), gen(dupindicator)
replace hour = 10 if dupindicator == 1
drop dupindicator
* missing hour 14 of day 22
expand 2 if (date==22 & month==7 & hour==13), gen(dupindicator)
replace hour = 14 if dupindicator == 1
drop dupindicator
* missing hour 17 of day 19
expand 2 if (date==10 & month==7 & hour==16), gen(dupindicator)
replace hour = 17 if dupindicator == 1
drop dupindicator
* missing hour 18 of day 12
expand 2 if (date==12 & month==7 & hour==17), gen(dupindicator)
replace hour = 18 if dupindicator == 1
drop dupindicator
* missing hour 21 of day 26
expand 2 if (date==26 & month==7 & hour==20), gen(dupindicator)
replace hour = 21 if dupindicator == 1
drop dupindicator
* missing hour 22 of day 15
expand 2 if (date==15 & month==7 & hour==21), gen(dupindicator)
replace hour = 22 if dupindicator == 1
drop dupindicator
sort year month date hour

*** Aug:
* missing hour 1 of day 28
expand 2 if (date==27 & month==8 & hour==24), gen(dupindicator)
replace hour = 1 if dupindicator == 1
replace date = 28 if dupindicator == 1
drop dupindicator
* missing hour 2 of day 21
expand 2 if (date==21 & month==8 & hour==1), gen(dupindicator)
replace hour = 2 if dupindicator == 1
drop dupindicator
* missing hour 3 of day 11
expand 2 if (date==11 & month==8 & hour==2), gen(dupindicator)
replace hour = 3 if dupindicator == 1
drop dupindicator
* missing hour 8 of day 4
expand 2 if (date==4 & month==8 & hour==7), gen(dupindicator)
replace hour = 8 if dupindicator == 1
drop dupindicator
* missing hour 9 of day 26
expand 2 if (date==26 & month==8 & hour==8), gen(dupindicator)
replace hour = 9 if dupindicator == 1
drop dupindicator
* missing hour 21 of day 29
expand 2 if (date==29 & month==8 & hour==20), gen(dupindicator)
replace hour = 21 if dupindicator == 1
drop dupindicator
* missing hour 22 of day 9
expand 2 if (date==9 & month==8 & hour==21), gen(dupindicator)
replace hour = 22 if dupindicator == 1
drop dupindicator
* missing hour 22 of day 26
expand 2 if (date==26 & month==8 & hour==21), gen(dupindicator)
replace hour = 22 if dupindicator == 1
drop dupindicator
* missing hour 24 of day 13
expand 2 if (date==13 & month==8 & hour==23), gen(dupindicator)
replace hour = 24 if dupindicator == 1
drop dupindicator
sort year month date hour

*** Sep:
* missing hour 3 of day 11
expand 2 if (date==11 & month==9 & hour==2), gen(dupindicator)
replace hour = 3 if dupindicator == 1
drop dupindicator
* missing hour 12 of day 25
expand 2 if (date==25 & month==9 & hour==11), gen(dupindicator)
replace hour = 12 if dupindicator == 1
drop dupindicator
* missing hour 14 of day 29
expand 2 if (date==29 & month==9 & hour==13), gen(dupindicator)
replace hour = 14 if dupindicator == 1
drop dupindicator
* missing hour 16 of day 3
expand 2 if (date==3 & month==9 & hour==15), gen(dupindicator)
replace hour = 16 if dupindicator == 1
drop dupindicator
* missing hour 17 of day 9
expand 2 if (date==9 & month==9 & hour==16), gen(dupindicator)
replace hour = 17 if dupindicator == 1
drop dupindicator
* missing hour 22 of day 27
expand 2 if (date==27 & month==9 & hour==21), gen(dupindicator)
replace hour = 22 if dupindicator == 1
drop dupindicator
sort year month date hour

*** Oct:
* missing hour 1 of day 17
expand 2 if (date==16 & month==10 & hour==24), gen(dupindicator)
replace hour = 1 if dupindicator == 1
replace date = 17 if dupindicator == 1
drop dupindicator
* missing hour 1 of day 22
expand 2 if (date==21 & month==10 & hour==24), gen(dupindicator)
replace hour = 1 if dupindicator == 1
replace date = 22 if dupindicator == 1
drop dupindicator
* missing hour 8 of day 13
expand 2 if (date==13 & month==10 & hour==7), gen(dupindicator)
replace hour = 8 if dupindicator == 1
drop dupindicator
* missing hour 9 of day 21
expand 2 if (date==21 & month==10 & hour==8), gen(dupindicator)
replace hour = 9 if dupindicator == 1
drop dupindicator
* missing hour 10 of day 11
expand 2 if (date==11 & month==10 & hour==9), gen(dupindicator)
replace hour = 10 if dupindicator == 1
drop dupindicator
* missing hour 10 of day 21
expand 2 if (date==21 & month==10 & hour==9), gen(dupindicator)
replace hour = 10 if dupindicator == 1
drop dupindicator
* missing hour 11 of day 19
expand 2 if (date==19 & month==10 & hour==10), gen(dupindicator)
replace hour = 11 if dupindicator == 1
drop dupindicator
* missing hour 11 of day 20
expand 2 if (date==20 & month==10 & hour==10), gen(dupindicator)
replace hour = 11 if dupindicator == 1
drop dupindicator
* missing hour 19 of day 18
expand 2 if (date==18 & month==10 & hour==18), gen(dupindicator)
replace hour = 19 if dupindicator == 1
drop dupindicator
* missing hour 19 of day 23
expand 2 if (date==23 & month==10 & hour==18), gen(dupindicator)
replace hour = 19 if dupindicator == 1
drop dupindicator
* missing hour 20 of day 23
expand 2 if (date==23 & month==10 & hour==19), gen(dupindicator)
replace hour = 20 if dupindicator == 1
drop dupindicator
* missing hour 24 of day 12
expand 2 if (date==12 & month==10 & hour==23), gen(dupindicator)
replace hour = 24 if dupindicator == 1
drop dupindicator
sort year month date hour

*** Nov:
* missing hour 1 of day 17
expand 2 if (date==16 & month==11 & hour==24), gen(dupindicator)
replace hour = 1 if dupindicator == 1
replace date = 17 if dupindicator == 1
drop dupindicator
* missing hour 4 of day 19
expand 2 if (date==19 & month==11 & hour==3), gen(dupindicator)
replace hour = 4 if dupindicator == 1
drop dupindicator
* missing hour 5 of day 4
expand 2 if (date==4 & month==11 & hour==4), gen(dupindicator)
replace hour = 5 if dupindicator == 1
drop dupindicator
* missing hour 9 of day 23
expand 2 if (date==23 & month==11 & hour==8), gen(dupindicator)
replace hour = 9 if dupindicator == 1
drop dupindicator
* missing hour 10 of day 23
expand 2 if (date==23 & month==11 & hour==9), gen(dupindicator)
replace hour = 10 if dupindicator == 1
drop dupindicator
* missing hour 11 of day 23
expand 2 if (date==23 & month==11 & hour==10), gen(dupindicator)
replace hour = 11 if dupindicator == 1
drop dupindicator
* missing hour 12 of day 10
expand 2 if (date==10 & month==11 & hour==11), gen(dupindicator)
replace hour = 12 if dupindicator == 1
drop dupindicator
* missing hour 12 of day 18
expand 2 if (date==18 & month==11 & hour==11), gen(dupindicator)
replace hour = 12 if dupindicator == 1
drop dupindicator
* missing hour 13 of day 27
expand 2 if (date==27 & month==11 & hour==12), gen(dupindicator)
replace hour = 13 if dupindicator == 1
drop dupindicator
* missing hour 13 of day 29
expand 2 if (date==29 & month==11 & hour==12), gen(dupindicator)
replace hour = 13 if dupindicator == 1
drop dupindicator
* missing hour 17 of day 13
expand 2 if (date==13 & month==11 & hour==16), gen(dupindicator)
replace hour = 17 if dupindicator == 1
drop dupindicator
sort year month date hour

*** Dec:
* missing hour 2 of day 3
expand 2 if (date==3 & month==12 & hour==1), gen(dupindicator)
replace hour = 2 if dupindicator == 1
drop dupindicator
* missing hour 2 of day 11
expand 2 if (date==11 & month==12 & hour==1), gen(dupindicator)
replace hour = 2 if dupindicator == 1
drop dupindicator
* missing hour 4 of day 3
expand 2 if (date==3 & month==12 & hour==3), gen(dupindicator)
replace hour = 4 if dupindicator == 1
drop dupindicator
* missing hour 7 of day 15
expand 2 if (date==15 & month==12 & hour==6), gen(dupindicator)
replace hour = 7 if dupindicator == 1
drop dupindicator
* missing hour 7 of day 16
expand 2 if (date==16 & month==12 & hour==6), gen(dupindicator)
replace hour = 7 if dupindicator == 1
drop dupindicator
* missing hour 8 of day 15
expand 2 if (date==15 & month==12 & hour==7), gen(dupindicator)
replace hour = 8 if dupindicator == 1
drop dupindicator
* missing hour 8 of day 16
expand 2 if (date==16 & month==12 & hour==7), gen(dupindicator)
replace hour = 8 if dupindicator == 1
drop dupindicator
* missing hour 9 of day 9
expand 2 if (date==9 & month==12 & hour==8), gen(dupindicator)
replace hour = 9 if dupindicator == 1
drop dupindicator
* missing hour 11 of day 15
expand 2 if (date==15 & month==12 & hour==10), gen(dupindicator)
replace hour = 11 if dupindicator == 1
drop dupindicator
* missing hour 12 of day 9
expand 2 if (date==9 & month==12 & hour==11), gen(dupindicator)
replace hour = 12 if dupindicator == 1
drop dupindicator
* missing hour 12 of day 26
expand 2 if (date==26 & month==12 & hour==11), gen(dupindicator)
replace hour = 12 if dupindicator == 1
drop dupindicator
* missing hour 13 of day 15
expand 2 if (date==15 & month==12 & hour==12), gen(dupindicator)
replace hour = 13 if dupindicator == 1
drop dupindicator
* missing hour 16 of day 28
expand 2 if (date==28 & month==12 & hour==15), gen(dupindicator)
replace hour = 16 if dupindicator == 1
drop dupindicator
sort year month date hour

gen index = _n

rename tmpc temp 

keep temp lon lat

export delimited using "C:\Users\atpha\Documents\Postdocs\Projects\TES\Data\weather\ext_temp_Boston.csv", replace

