
* Import data:
import delimited using "C:\Users\atpha\Documents\Postdocs\Projects\TES\Data\fan heating load\heating_load.csv", clear
rename v1 hour

gen fan_ratio = fanheatingload/heatingload
replace fan_ratio = 0 if fan_ratio ==.

bysort hour: egen mean_fan_heating = mean(fanheatingload)
bysort hour: egen mean_tot_heating = mean(heatingload)

gen mean_fan_ratio = mean_fan_heating/mean_tot_heating
replace mean_fan_ratio = 0 if mean_fan_ratio ==.
replace mean_tot_heating = 0  if mean_tot_heating ==.

sort building_id hour

duplicates drop hour mean_fan_ratio mean_tot_heating, force
keep hour mean_fan_ratio mean_tot_heating

* Specify months:
replace hour = hour+1
gen month = "jan" if (hour>=1 & hour<=744)
replace month = "feb" if (hour>744 & hour<=1416)
replace month = "mar" if (hour>1416 & hour<=2160)
replace month = "apr" if (hour>2160 & hour<=2880)
replace month = "may" if (hour>2880 & hour<=3624)
replace month = "jun" if (hour>3624 & hour<=4344)
replace month = "jul" if (hour>4344 & hour<=5088)
replace month = "aug" if (hour>5088 & hour<=5832)
replace month = "sep" if (hour>5832 & hour<=6552)
replace month = "oct" if (hour>6552 & hour<=7296)
replace month = "nov" if (hour>7296 & hour<=8016)
replace month = "dec" if (hour>8016 & hour<=8760)

drop if mean_tot_heating <0.5

scatter mean_fan_ratio mean_tot_heating
twoway fpfit mean_fan_ratio mean_tot_heating, xtitle("Average Total Heating Load") ytitle("Fan Heating Load to Total Heating Load Ratio")

export delimited using "C:\Users\atpha\Documents\Postdocs\Projects\TES\Data\heating_load_cleaned.csv"
