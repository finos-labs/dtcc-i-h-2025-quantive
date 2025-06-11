import webbrowser, os
import json
import boto3
import re
from collections import Counter
import botocore

"""
Obtain the Comprehend output and read it
"""
# initialize an S3 environment
session = boto3.Session(profile_name='hackathon-participant-730356633374')
s3 = session.client('s3')

# get user input for bucket name and filepath to the Comprehend data
bucket = input("Enter the name of your S3 bucket: ")
while(bucket == ""):
    bucket = input("Bucket name cannot be blank. Enter the name of your S3 bucket: ")
filepath = input("Enter the full filepath to your Comprehend output file: ")
while(filepath == ""):
    filepath = input("Filepath cannot be blank. Enter the full filepath to your Comprehend output file: ")
# get user input for metadata folder for storing Kendra-friendly files
meta_folder = input("Enter the full filepath to your metadata directory: ")
while((meta_folder == "") or (meta_folder[-1] != "/")):
    if meta_folder == "":
        meta_folder = input("Filepath cannot be blank. Enter the full filepath to your metadata directory: ")
    elif (meta_folder[-1] != "/"):
        meta_folder = input("Filepath must end with a /. Enter the full filepath to your metadata directory: ")
# get the output file
comprehend_output = s3.get_object(Bucket=bucket, Key=filepath)
# store the entire text as a string in variable "body"
body = comprehend_output['Body'].read().decode("utf-8")
# notify user of starting the process
print("Converting...")

"""
Split the Comprehend file and store it in an array
"""
# create int array containing start indices of each JSON object
split_locations = [word.start() for word in re.finditer('{"Entities"', body)]
# initialize array to hold the split sections
split_array = []
# loop to split Comprehend text at desired indices
for i in range(len(split_locations)):
    if i != len(split_locations) - 1:
        entry = body[split_locations[i]:split_locations[i+1]].strip("\n")
        split_array.append(entry)
    else:
        split_array.append(body[split_locations[i]:len(body)].strip("\n"))

"""
Convert array elementwise into Kendra metadata and output
"""
# initialize array
kendra_array = []
# loop over split elements to reformat individually
for i in range(len(split_array)):
    # load each split element as JSON
    item = split_array[i]
    try:
        entity_json = json.loads(item)
    except Exception as e:
        pass
    # initialize dictionary
    current_dictionary = dict()
    # store 'File' attribute to be used for renaming
    file_name = entity_json["File"]
    # loop to determine entity types present with high confidence score
    for entry in entity_json["Entities"]:
        if float(entry["Score"]) >= 0.9:
            current_dictionary[entry["Type"]] = []
    # loop to populate string lists of present entities for entry in entity_json["Entities"]:
        if float(entry["Score"]) >= 0.9:
            current_dictionary[entry["Type"]].append(entry["Text"])
    # pruning lists to keep 10 most common entities per category
    for key in current_dictionary:
        frequency_set = Counter(current_dictionary[key])
        max_10_frequencies = list(frequency_set.most_common(10))
        current_dictionary[key] = [x[0] for x in max_10_frequencies]
        
    # Retrieve filename for required output format
    output_key = meta_folder + file_name + ".metadata.json"

    # New entity metadata to merge
    new_attributes = current_dictionary

    # Try fetching existing metadata file
    try:
        existing_obj = s3.get_object(Bucket=bucket, Key=output_key)
        existing_content = existing_obj['Body'].read().decode('utf-8')
        existing_metadata = json.loads(existing_content)
        existing_attributes = existing_metadata.get("Attributes", {})
    except botocore.exceptions.ClientError as e:
        # If the file doesn't exist, start fresh
        if e.response['Error']['Code'] == "NoSuchKey":
            existing_metadata = {
                "DocumentId": f"s3://{bucket}/{filepath}",
                "Attributes": {},
                "Title": file_name,
                "ContentType": "text/plain"
            }
            existing_attributes = {}
        else:
            raise e

    # Merge logic: combine existing and new attributes, limit to top 10 per key
    for key, values in new_attributes.items():
        if key not in existing_attributes:
            existing_attributes[key] = []
        combined = existing_attributes[key] + values
        freq = Counter(combined)
        existing_attributes[key] = [item for item, _ in freq.most_common(10)]

    # Update only the Attributes section
    existing_metadata["Attributes"] = existing_attributes

    # Save merged metadata
    merged_file_content = json.dumps(existing_metadata)
    s3.put_object(Bucket=bucket, Key=output_key, Body=merged_file_content)

# notify user of completing the process
print("Completed.")
print("Your output JSON file(s) can be viewed at s3://" + bucket + "/" + meta_folder)