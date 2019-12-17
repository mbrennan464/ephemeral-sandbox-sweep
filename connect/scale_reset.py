#!/usr/local/bin/python

from __future__ import print_function
from os import path
import yaml

import json
import requests
import time
import kubernetes.client
from kubernetes.client.rest import ApiException
from pprint import pprint
from kubernetes import client, config, watch
from datetime import date

today = date.today()
config.load_kube_config()
batch_v1 = client.BatchV1Api()

webhook_url='https://hooks.slack.com/services/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'
slack_data= {'text':'Ephemeral Sandbox reset starting now....'}
response = requests.post(webhook_url, json=slack_data, headers={'Content-Type':'application/json'})

if response.status_code != 200:
   raise ValueError(
        'Request to slack returned an error %s, the response is:\n%s'
        % (response.status_code, response.text)
    )

corev1api = client.CoreV1Api()
appsv1beta1api = client.AppsV1beta1Api()
# Scale down Deployment to 0 replicas
body = {'spec': {'replicas': 0}}
try:
    appsv1beta1api.patch_namespaced_deployment(
        'connect-api', 'connect', body)
except client.rest.ApiException as e:
    if e.status == 404:
        # Deployment does not exist, nothing to scale
        msg = 'can not delete nonexistent Deployment/{} from ns/{}'
        # logging.debug(msg.format(name, namespace))
        print(msg)
    else:
        # Unexpected exception, stop reaping
        # logging.exception(e)
        print("Unknown exception")

try:
    appsv1beta1api.patch_namespaced_deployment(
        'harmony-anchor-writer', 'connect', body)
except client.rest.ApiException as e:
    if e.status == 404:
        # Deployment does not exist, nothing to scale
        msg = 'can not delete nonexistent Deployment/{} from ns/{}'
        # logging.debug(msg.format(name, namespace))
        print(msg)
    else:
        # Unexpected exception, stop reaping
        # logging.exception(e)
        print("Unknown exception")

try:
    appsv1beta1api.patch_namespaced_deployment(
        'harmony-identity', 'connect', body)
except client.rest.ApiException as e:
    if e.status == 404:
        # Deployment does not exist, nothing to scale
        msg = 'can not delete nonexistent Deployment/{} from ns/{}'
        # logging.debug(msg.format(name, namespace))
        print(msg)
    else:
        # Unexpected exception, stop reaping
        # logging.exception(e)
        print("Unknown exception")
try:                                                                                               
    appsv1beta1api.patch_namespaced_deployment(                                                    
        'anchors-receipts-api', 'connect', body)                                                       
except client.rest.ApiException as e:                                                              
    if e.status == 404:                                                                            
        # Deployment does not exist, nothing to scale                                  
        msg = 'can not delete nonexistent Deployment/{} from ns/{}'                                
        # logging.debug(msg.format(name, namespace))                                               
        print(msg)                                                   
    else:                                                            
        # Unexpected exception, stop reaping                         
        # logging.exception(e)                                       
        print("Unknown exception")   


nmspace="connect"
file_name="reset-job.yaml"

with open("reset.yaml", "rt") as fin:
    with open("reset-job.yaml", "wt") as fout:
        for line in fin:
            fout.write(line.replace('reset-connect-db', 'reset-connect-db-{}'.format(today)))

with open(path.join(path.dirname(__file__), file_name)) as f:
    dep = yaml.safe_load(f)
    try: 
        api_response = batch_v1.create_namespaced_job(
        body=dep,
        namespace=nmspace)
        print("Job created. status='%s'" % str(api_response.status))
    except ApiException as e:
        print("Exception when calling BatchV1Api->create_namespaced_job: %s\n" % e)

with open("dataflow-wipe.yaml", "rt") as fin:
    with open("dataflow-wipe-job.yaml", "wt") as fout:
        for line in fin:
            fout.write(line.replace('datastore-delete', 'datastore-delete-{}'.format(today)))

file_name="dataflow-wipe-job.yaml"


with open(path.join(path.dirname(__file__), file_name)) as f:      
    dep = yaml.safe_load(f)                                        
    try:                                                           
        api_response = batch_v1.create_namespaced_job(             
        body=dep,                                                  
        namespace=nmspace)                                         
        print("Job created. status='%s'" % str(api_response.status))
    except ApiException as e:                                       
        print("Exception when calling BatchV1Api->create_namespaced_job: %s\n" % e)

incomplete=True                                                                       

while incomplete:
    ret = batch_v1.list_namespaced_job(namespace='connect', watch=False)
    for i in ret.items:
        if i.metadata.name == 'reset-connect-db-{}'.format(today):
            if i.status.succeeded == 1:
                incomplete = False
                print(i.metadata.name)
                print("Connect database reset complete!")


incomplete=True

while incomplete:
    ret = batch_v1.list_namespaced_job(namespace='connect', watch=False)                 
    for i in ret.items:                                                            
        if i.metadata.name == 'datastore-delete-{}'.format(today):                                  
            if i.status.succeeded == 1:                                            
                incomplete = False                                                 
                print(i.metadata.name)                                             
                print("Datastore reset complete!")  

                                             
                                                                                   

body = {'spec': {'replicas': 1}}                                                                                                                                                                            
try:                                                                                                                                                                                                        
    appsv1beta1api.patch_namespaced_deployment(                                                                                                                                                             
        'connect-api', 'connect', body)                                                                                                                                                                     
except client.rest.ApiException as e:                                                                                                                                                                       
    if e.status == 404:                                                                                                                                                                                     
        # Deployment does not exist, nothing to scale                                                                                                                                           
        msg = 'can not scale-up nonexistent Deployment/{} from ns/{}'                                                                                                                                         
        # logging.debug(msg.format(name, namespace))                                                                                                                                                        
        print(msg)                                                                                                                                                                                          
    else:                                                                                                                                                                                                   
        # Unexpected exception, stop reaping                                                                                                                                                                
        # logging.exception(e)                                                                                                                                                                              
        print("Unknown exception")                                                                                                                                                                           
                                                                                   
try:                                                                               
    appsv1beta1api.patch_namespaced_deployment(                                    
        'harmony-anchor-writer', 'connect', body)                                  
except client.rest.ApiException as e:                                              
    if e.status == 404:                                                            
        # Deployment does not exist, nothing to scale                  
        msg = 'can not scale-up nonexistent Deployment/{} from ns/{}'                
        # logging.debug(msg.format(name, namespace))                               
        print(msg)                                                                 
    else:                                                                          
        # Unexpected exception, stop reaping                                       
        # logging.exception(e)                                                     
        print("Unknown exception")                                                  
                                                                                   
try:                                                                               
    appsv1beta1api.patch_namespaced_deployment(                                    
        'harmony-identity', 'connect', body)                                       
except client.rest.ApiException as e:                                              
    if e.status == 404:                                                            
        # Deployment does not exist, nothing to scale                  
        msg = 'can not scale-up nonexistent Deployment/{} from ns/{}'                
        # logging.debug(msg.format(name, namespace))                               
        print(msg)                                                                 
    else:                                                                          
        # Unexpected exception, stop reaping                                       
        # logging.exception(e)                                                     
        print("Unknown exception")    

try:                                                                                               
    appsv1beta1api.patch_namespaced_deployment(                                                    
        'anchors-receipts-api', 'connect', body)                                                   
except client.rest.ApiException as e:                                                              
    if e.status == 404:                                                                            
        # Deployment does not exist, nothing to scale                                  
        msg = 'can not delete nonexistent Deployment/{} from ns/{}'  
        # logging.debug(msg.format(name, namespace))                 
        print(msg)                                                   
    else:                                                            
        # Unexpected exception, stop reaping                       
        # logging.exception(e)                                     
        print("Unknown exception")  


slack_data= {'text':'Ephemeral Sandbox reset complete!'}                    
response = requests.post(webhook_url, json=slack_data, headers={'Content-Type':'application/json'})
                                                                                   
if response.status_code != 200:                                                    
   raise ValueError(                                                               
        'Request to slack returned an error %s, the response is:\n%s'              
        % (response.status_code, response.text)                                    
    )  