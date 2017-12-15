# Diabetes Management

While there are a variety of technologies out there today that make managing diabetes easier, they are generally single-purpose and integration of information between multiple devices can mean double or triple entry of information.  The goal is this project is to  extract information from various monitoring and management devices to allow for insights that are not possible when using them on their own.

## Background

Though not all of this is yet included, here is some useful background information related to the data sources.
- a1c: The measure of glycolated hemoglobin in the blood.  This is generally-speaking a 3-month average of blood sugar.  A good target range is < 7.0.
- Bolus insulin: an amount of insulin taken at once
- Basal insulin: a rate of insulin released into the body over time throughout the day.  Different parts of the day will have different basal insulin rates
- BG or bg: a common abbreviation for blood sugar (blood glucose)
- CGM: Continuous Glucose Monitor.  Dexcom is an example of a CGM.  A CGM takes samples of blood sugar from interstitial fluid rather than directly from the blood.  As a result, CGM blood sugar values are generally considered to be 10-15 minutes behind the actual blood sugar.


## Getting Started

Currently, this project supports two types of (.csv or .xlsx) files:
- Omnipod log files: FreeStyle CoPilot Health Management System
	- There is no export option, but you can easily copy and paste all of this data as-is into an excel or csv file.
- Dexcom: Export from your Dexcom Clarity account - Maximum download is 90 days.
	- https://clarity.dexcom.com
	- Reports > Export
	
To use this package, it is best to store your Omnipod and Dexcom data in a folder along with the .py file.

Once all files are located in their place, you will just need to use the file paths/folder within the Jupyter notebook to get started.  

#### Omnipod
```
- Meal Bolus: Insulin taken for food eaten
- Bolus Insulin: A bolus taken for ANY reason where the reason is not specified in the device.
- Correction Bolus: Insulin taken if blood glucose levels are above target.  A correction bolus is broken out separately from a Meal bolus when bg is above the target.
- IOB: Insulin On Board - Fast-acting insulin is used in Insulin Pumps (Omnipod, Medtronic, etc.).  When calculating how much insulin to take, either the person or the device must understand how much insulin is already in the body to calculate a correct dose.  If insulin is not used within ~20 minutes after it entered the body, it will be be excreted with no effect on blood sugar.  
- Extended Meal Bolus: Bolus insulin delivered over a time period.  In the omnipod data, this is seen as a fraction, 0.4 = 40% of the Meal Bolus, for example, will be delivered after a designated time period.  Since some foods take longer for the body to digest into sugars that can be processed by the insulin, extended meal boluses allow for a programmatic way to handle complex foods (i.e. pizza).
- Blood Sugar (bg) Target: A numeric value that the device uses to calculate the "ideal" blood sugar and uses to calculate the amount of insulin to deliver.
```

#### Dexcom
```
- Calibration: A Dexcom (G5) is generally celibrated 2x per day.  Each calibration takes 2 back-to-back blood sugar readings.  
- Lifecycle: The life of a single device is about 7 days.  After 7 days, the site is switched and there is a two-hour warm-up phase required to activate the new site.

Note: For a variety of reasons, the Dexcom calibration may not be accurate.  Some of these reasons include blood sugar volatility during the warm-up phase of the device (occurs weekly), a faulty insertion (blood affecting the measurement), or over-calibration.
```

### Prerequisites

- FreeStyle CoPilot Health Management System
	- For instructions: https://www.myomnipod.com/learning-center/download-software/download-abbott
- Python 
- Jupyter Notebook

## Contributing

As this project is further developed, I will open it up for contribution.  If you are interested in seeing any particular data sources added, please contact me: [chelsea.lapeikis@gmail.com]

## Versioning

Version 0.1 - 12/15/2017

## Authors

* **Chelsea Lapeikis** - *Initial work* - [chelseamlap](https://github.com/chelseamlap)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

My husband for expanding my understanding of the complex world of diabetes management and for explaining the many variables that exist within each of the systems.

