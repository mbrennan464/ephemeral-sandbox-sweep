# Sandbox Reset

The cronjob for sandbox reset is `connect-wipe` and it calls the container `gcr.io/connect-sandbox-224121/connect-wipe` to kickoff the process.
This container runs  `scale_reset.py` - which stops the pods that are running the connect API and need to be stopped for the restart.  Then it initiates the `reset-connect-db` job, which clears the local database that connect uses.   

Next it starts the `dataflow-wipe` - this job starts a separate container which contains the necessary service account to authenticate and run `restart.sh` against the FactomD cluster for the ephemeral sandbox. It deletes the persistent volume, claim, and pod for the node that is running the blockchain.  It then waits for the pod to start correctly, and will scale down and back up to make sure the pod starts.  Then it will run the funding job, so that the node is funded.  This script deletes the info in the datastores for the sandbox as well.

Finally, the `connect-wipe` job, when it detects the `dataflow-wipe` job is finished, will re-scale the pods for the Connect API, back up.  Then it posts a finish notifcation to slack, and is completed.