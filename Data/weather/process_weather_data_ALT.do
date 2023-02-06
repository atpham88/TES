* Import Detroit temp data:
import delimited using "C:\Users\atpha\Documents\Postdocs\Projects\TES\Data\weather\ATL.csv", clear
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
* missing hour 3 of 31st day:
expand 2 if (date==31 & month==1 & hour==2), gen(dupindicator)
replace hour = 3 if dupindicator == 1
drop dupindicator
sort year month date hour

*** Feb:
* missing hour 11 of day 20:
expand 2 if (date==20 & month==2 & hour==10), gen(dupindicator)
replace hour = 11 if dupindicator == 1
drop dupindicator
sort year month date hour

*** March:
* missing hour 3 in day 11
expand 2 if (date==11 & month==3 & hour==2), gen(dupindicator)
replace hour = 3 if dupindicator == 1
drop dupindicator
* missing hour 4 in day 26
expand 2 if (date==26 & month==3 & hour==3), gen(dupindicator)
replace hour = 4 if dupindicator == 1
drop dupindicator
sort year month date hour

*** Apr:
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
* missing hour 2 of days 9
expand 2 if (date==9 & month==5 & hour==1), gen(dupindicator)
replace hour = 2 if dupindicator == 1
drop dupindicator
* missing hour 20 of day 1
expand 2 if (date==1 & month==5 & hour==19), gen(dupindicator)
replace hour = 20 if dupindicator == 1
drop dupindicator
* missing hour 20 of day 28
expand 2 if (date==28 & month==5 & hour==19), gen(dupindicator)
replace hour = 20 if dupindicator == 1
drop dupindicator
sort year month date hour

*** June:
* missing hour 4 of day 12
expand 2 if (date==12 & month==6 & hour==3), gen(dupindicator)
replace hour = 4 if dupindicator == 1
drop dupindicator
sort year month date hour

*** Jul: no probs

*** Aug:
* missing hour 2 of day 21
expand 2 if (date==21 & month==8 & hour==1), gen(dupindicator)
replace hour = 2 if dupindicator == 1
drop dupindicator
* missing hour 17 of day 18
expand 2 if (date==18 & month==8 & hour==16), gen(dupindicator)
replace hour = 17 if dupindicator == 1
drop dupindicator
sort year month date hour

*** Sep
* missing hour 20 of day 22
expand 2 if (date==22 & month==9 & hour==19), gen(dupindicator)
replace hour = 20 if dupindicator == 1
drop dupindicator
sort year month date hour

*** Oct:
* missing hour 1 of day 17
expand 2 if (date==16 & month==10 & hour==24), gen(dupindicator)
replace hour = 1 if dupindicator == 1
replace date = 17 if dupindicator == 1
drop dupindicator
sort year month date hour

*** Nov:
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

export delimited using "C:\Users\atpha\Documents\Postdocs\Projects\TES\Data\weather\ext_temp_Atlanta.csv"

