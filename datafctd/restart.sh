#!/bin/bash
echo "Service account json must be mounted on /"
gcloud auth activate-service-account --key-file=/rake-sa.json
gcloud config set project connect-sandbox-224121
gcloud container clusters get-credentials  factomd-sandbox-ephemeral --zone us-central1-a --project  connect-sandbox-224121

echo "Deleting FactomD Database...."
for i in $(kubectl -n $NAMESPACE get pods | grep boot | awk {'print $1'}); do 
    kubectl -n $NAMESPACE exec $i -it -- rm -rf /root/.factom/m2/custom-database/*
    kubectl -n $NAMESPACE delete pod $i
    echo "Deleted pod $i"
done;


for i in $(kubectl -n $NAMESPACE get pods | grep -v NAME | grep -v seed | grep -v boot | awk {'print $1'}); do
    kubectl -n $NAMESPACE delete pvc database-$i &
    PV=$(kubectl -n $NAMESPACE get pv | grep database-$i | awk {'print $1'})
    kubectl -n $NAMESPACE delete pv $PV &
    kubectl -n $NAMESPACE delete pod $i &
    echo "Deleted $i"
done;

echo "Making backup of datastore...."
gcloud datastore export --namespaces="EPHEMERAL,EPHEMERAL-connect" gs://datastore-backups/

echo "Deleting datastores...."
gcloud dataflow jobs run keys-delete --gcs-location gs://dataflow-templates/latest/Datastore_to_Datastore_Delete --parameters datastoreReadGqlQuery="SELECT * FROM Key",datastoreReadProjectId="connect-sandbox-224121",datastoreDeleteProjectId="connect-sandbox-224121",datastoreReadNamespace="EPHEMERAL"

gcloud dataflow jobs run identity-delete --gcs-location gs://dataflow-templates/latest/Datastore_to_Datastore_Delete --parameters datastoreReadGqlQuery="SELECT * FROM Identity",datastoreReadProjectId="connect-sandbox-224121",datastoreDeleteProjectId="connect-sandbox-224121",datastoreReadNamespace="EPHEMERAL"

gcloud dataflow jobs run dblocks-delete --gcs-location gs://dataflow-templates/latest/Datastore_to_Datastore_Delete --parameters datastoreReadGqlQuery="SELECT * FROM DirectoryBlock",datastoreReadProjectId="connect-sandbox-224121",datastoreDeleteProjectId="connect-sandbox-224121",datastoreReadNamespace="EPHEMERAL-connect"

gcloud dataflow jobs run syncpt-delete --gcs-location gs://dataflow-templates/latest/Datastore_to_Datastore_Delete --parameters datastoreReadGqlQuery="SELECT * FROM SyncCheckpoint",datastoreReadProjectId="connect-sandbox-224121",datastoreDeleteProjectId="connect-sandbox-224121",datastoreReadNamespace="EPHEMERAL-connect"

echo "Scaling factomd pod down to reset data"
kubectl -n $NAMESPACE scale --replicas=0 statefulset factomd-factomd-v6-3-3
sleep 15
kubectl -n $NAMESPACE scale --replicas=1 statefulset factomd-factomd-v6-3-3
sleep 20
let minute=0;
echo " $count pods deleted"
until [[ "$(kubectl -n $NAMESPACE get pods | grep factomd-factomd-v6-3-3-0 | grep Running | wc -l)" -eq "1" ]]; do
   echo "Waiting for Pod to start!"	   
   sleep 5
   let "minute++";
   echo "Minute $minute"
   if [[ "$minute" -eq "5" ]]; then
      echo "Sending failing to start curl ..."
      echo "Deleting pod, reseting minute loop"
      kubectl -n $NAMESPACE delete pod factomd-factomd-v6-3-3-0
      let minute=0
   fi
done;

echo "Pod running!"

echo "$running pods running" ;

echo "Waiting 120 to start funding...."
sleep 120

echo "Starting funding job...."

kubectl -n $NAMESPACE create -f fund.yaml

echo "Data FCTD reset done!"

exit 0

