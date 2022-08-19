#!/bin/bash
##
## Compile sync-settings and install if no errors.
##
TARGET=$1

# Break target down by commas into an array.
TARGET_ADDRESSES=()
while IFS=',' read -ra ADDRESSES; do
    for address in "${ADDRESSES[@]}"; do
        TARGET_ADDRESSES+=($address)
    done
done <<< "$TARGET"

SYNC_FIRST_FILENAME=$(find sync -type f -maxdepth 1 -printf "%f\n" | head -1)

for target_address in "${TARGET_ADDRESSES[@]}"; do
    echo "Copying to $target_address..."
    ssh-copy-id root@$target_address
    target_sync_path=$(ssh root@$target_address "find /usr -name runtests | grep 'site-packages\|dist-packages' | head -1")
    echo "target_sync_path=$target_sync_path"
    rsync -r -a -v bin root@$target_address:/usr
    rsync -r -a -v runtests/* root@$target_address:$target_sync_path
done
