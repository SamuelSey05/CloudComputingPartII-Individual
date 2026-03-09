#!/bin/sh

. ./shared-variables.sh

MAIN_CLASS=org.example.JavaWordLetterCount
REMOTE_OUTPUT_PATH=$VOLUME_PATH/CloudComputingCoursework_Group3/
EXECUTION_TIME_FILE="execution_time.txt"

name="$1"
remote_input_data="$2"
executors="$3"

rm -f $EXECUTION_TIME_FILE

/usr/bin/time -o $EXECUTION_TIME_FILE \
    -f "%e" \
    timeout 5m ~/spark-3.5.4-bin-hadoop3/bin/spark-submit \
        --master k8s://https://128.232.80.18:6443 \
        --deploy-mode cluster \
        --name $name \
        --class $MAIN_CLASS \
        --conf spark.executor.instances=$executors \
        --conf spark.kubernetes.namespace=$NAMESPACE \
        --conf spark.kubernetes.authenticate.driver.serviceAccountName=spark-$GROUP \
        --conf spark.kubernetes.container.image=andylamp/spark:v3.5.4-amd64 \
        --conf spark.kubernetes.driver.volumes.persistentVolumeClaim.nfs-$GROUP.mount.path=/test-data \
        --conf spark.kubernetes.driver.volumes.persistentVolumeClaim.nfs-$GROUP.options.claimName=nfs-$GROUP \
        --conf spark.kubernetes.executor.volumes.persistentVolumeClaim.nfs-$GROUP.mount.path=/test-data \
        --conf spark.kubernetes.executor.volumes.persistentVolumeClaim.nfs-$GROUP.options.claimName=nfs-$GROUP \
        $SPARK_JAR_PATH -i $remote_input_data

if [ "$?" -ne 0 ]; then
    # penalty for failure, but not infinity to avoid breaking the maths
    echo "-1" > $EXECUTION_TIME_FILE
fi

kubectl get pods --no-headers=true | awk /$name/'{print $1}' | xargs -r kubectl delete pod
