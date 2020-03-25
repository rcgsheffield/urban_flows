# DEFRA Sensor Observation Services Harvestor

This is a code source repository for a harvestor module for DEFRA Sensor Observation Services data source for Urban Flow project (The University of Sheffield) .

https://uk-air.defra.gov.uk/data/about_sos

This module is designed to ingest air pollution measurements from Defra’s UK-AIR Sensor Observation Service (SOS). 

The module is run with the following parameters:

-d/--date 			(required) ISO UTC date  
-od/--output_data 	(required) Output CSV file path  
-k/--distance		Radius distance (km)  
-um/--update_meta	True if update the metadata  
-om/--output_meta	Output folder path for metadata files  
-v/--verbose		Debug logging mode  
-ad/--assets-dir	Assets directory  

The parameters should be define in CONFIG file. The module run by calling pipeline.sh script.

The following example call the module with parameters spedified by inline arguments:  
`python pipeline.py -d 2020-01-01 -od defra_sos.csv -k 25 -um True -om meta`

Please follow the tests suits to see how the module works. You can also find comments in the code describing the logic. 
	
 - tests/tests_utils.py
 - tests/tests_download.py
 - tests/tests_metadata.py

