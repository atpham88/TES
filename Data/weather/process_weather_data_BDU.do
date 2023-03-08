* Import Boulder temp data:
import delimited using "C:\Users\atpha\Documents\Postdocs\Projects\TES\Data\weather\DEN.csv", clear
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
* missing hour 3 of day 31:
expand 2 if (date==31 & month==1 & hour==2), gen(dupindicator)
replace hour = 3 if dupindicator == 1
drop dupindicator
sort year month date hour

*** Feb: no probs

*** March:
* missing hour 3 in day 11
expand 2 if (date==11 & month==3 & hour==2), gen(dupindicator)
replace hour = 3 if dupindicator == 1
drop dupindicator
* missing hour 4 in day 26
expand 2 if (date==26 & month==3 & hour==3), gen(dupindicator)
replace hour = 4 if dupindicator == 1
drop dupindicator
* missing hour 21 in day 11
expand 2 if (date==11 & month==3 & hour==20), gen(dupindicator)
replace hour = 21 if dupindicator == 1
drop dupindicator
sort year month date hour

*** Apr:
* missing hour 3 of day 18
expand 2 if (date==18 & month==4 & hour==2), gen(dupindicator)
replace hour = 3 if dupindicator == 1
drop dupindicator
* missing hour 13 of day 4
expand 2 if (date==4 & month==4 & hour==12), gen(dupindicator)
replace hour = 13 if dupindicator == 1
drop dupindicator
* missing hour 14 of day 4
expand 2 if (date==4 & month==4 & hour==13), gen(dupindicator)
replace hour = 14 if dupindicator == 1
drop dupindicator
* missing hour 15 of day 4
expand 2 if (date==4 & month==4 & hour==14), gen(dupindicator)
replace hour = 15 if dupindicator == 1
drop dupindicator
* missing hour 16 of day 4
expand 2 if (date==4 & month==4 & hour==15), gen(dupindicator)
replace hour = 16 if dupindicator == 1
drop dupindicator
* missing hour 17 of day 4
expand 2 if (date==4 & month==4 & hour==16), gen(dupindicator)
replace hour = 17 if dupindicator == 1
drop dupindicator
* missing hour 24 of day 10
expand 2 if (date==10 & month==4 & hour==23), gen(dupindicator)
replace hour = 24 if dupindicator == 1
drop dupindicator
sort year month date hour

*** May:
* Missing hour 1 of days 9,10
expand 2 if (date==8 & month==5 & hour==24), gen(dupindicator)
replace hour = 1 if dupindicator == 1
replace date = 9 if dupindicator == 1
drop dupindicator
expand 2 if (date==9 & month==5 & hour==24), gen(dupindicator)
replace hour = 1 if dupindicator == 1
replace date = 10 if dupindicator == 1
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
sort year month date hour

*** June:
* missing hour 4 of day 12
expand 2 if (date==12 & month==6 & hour==3), gen(dupindicator)
replace hour = 4 if dupindicator == 1
drop dupindicator
sort year month date hour

*** Jul:
* missing hour 24 of day 26
expand 2 if (date==26 & month==6 & hour==23), gen(dupindicator)
replace hour = 24 if dupindicator == 1
drop dupindicator
sort year month date hour

*** Aug:
* missing hour 2 of day 21
expand 2 if (date==21 & month==8 & hour==1), gen(dupindicator)
replace hour = 2 if dupindicator == 1
drop dupindicator
* missing hour 17 of day 17
expand 2 if (date==17 & month==8 & hour==16), gen(dupindicator)
replace hour = 17 if dupindicator == 1
drop dupindicator
sort year month date hour

*** Sep: no probs

*** Oct: no probs

*** Nov:
* missing hour 9 of day 23
expand 2 if (date==23 & month==11 & hour==8), gen(dupindicator)
replace hour = 9 if dupindicator == 1
drop dupindicator
* missing hour 10 of day 23
expand 2 if (date==23 & month==11 & hour==9), gen(dupindicator)
replace hour = 10 if dupindicator == 1
drop dupindicator
sort year month date hour

*** Dec:
* missing hour 6 of day 3
expand 2 if (date==3 & month==12 & hour==5), gen(dupindicator)
replace hour = 6 if dupindicator == 1
drop dupindicator
sort year month date hour

gen index = _n

rename tmpc temp 

keep temp lon lat

export delimited using "C:\Users\atpha\Documents\Postdocs\Projects\TES\Data\weather\ext_temp_Boulder.csv", replace

