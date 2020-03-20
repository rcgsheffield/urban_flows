# sheffield_environment_agency
The "harvestor" project for Environment Agency data source for Urban Flow project (The University of Sheffield) .

https://environment.data.gov.uk/flood-monitoring/doc/reference

This model is designed to ingest flood monitoring data from Environment Agency. 

The module is run with the following parameters:

-d/--date 			(required) ISO UTC date
-od/--output_data 	(required) Output CSV file path
-k/--distance		Radius distance (km)
-um/--update_meta	True if update the metadata
-om/--output_meta	Output folder path for metadata files

For example python env_agency_flood.py -d 2020-01-01 -od flood.csv -k 25 -um True -om meta

Please follow the tests below to see how it works. You can also find comments in the code describing the logic. 
	
Test 1: 








