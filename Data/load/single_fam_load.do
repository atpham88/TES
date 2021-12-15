use "C:\Users\atpha\Documents\Postdocs\Projects\Thermal Storage\Data\load\single_fam_load.dta", clear
keep timestamp units_represented outelectricitywater_systemsenerg
gen water_sys_load = outelectricitywater_systemsenerg/units_represented
keep timestamp water_sys_load


gen month = substr(timestamp,1,2)
replace month=subinstr(month,"/","",.)
destring(month), replace

gen date = substr(timestamp,3,3)
replace date = reverse(substr(reverse(date),strpos(reverse(date), "/"), . )) if substr(date,1,1)!= "/"
replace date=subinstr(date,"/","",.)
destring(date), replace

gen hour = substr(timestamp,-5,2)
destring(hour), replace

drop timestamp


bysort month date hour: egen tot_w_load = sum(water_sys_load)
duplicates drop month date hour, force

drop water_sys_load
