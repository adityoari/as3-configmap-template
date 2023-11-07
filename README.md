# as3-configmap-template

## Overview

Simple python script for rendering a pre-built jinja2 template into an AS3 ConfigMap YAML which can be deployed into a k8s cluster with CIS installed.

## Requirements

* Python3
* Jinja2

## Usage

Usage:  
`python cm-template-parser.py <template-directory>/<template-file> <data-csv-file>`  

Example:  
`python cm-template-parser.py templates/serviceNclient.yaml sample-data.yaml`  

## Input files

### Data CSV

Data CSV files would consist of lines with the following format:  
`Key-category_Key-name,Value1,Value2,...`

With `Key-category` is one of the following:  
* CM : ConfigMap-level setting parameter
* AS3: AS3/BIG-IP-level setting parameter
* APP: App-specific setting parameter

### Jinja2 template

Currently  `cm-template-parser.py` script is specifically written for `serviceNclient.yaml` template, and vice versa.  

