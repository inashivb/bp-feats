#!/bin/bash
# Get the directory where script is
SCRIPTDIR="$(dirname "$0")"

conflicts=false

# Check if there is an old log file already
if [ -f bp_error.log ]; then
    rm bp_error.log
fi

while IFS= read -r line; do
    # cherry-pick each commit
    out=$(git cherry-pick -x $line 2>&1 1>/dev/null)
    retval=$?
    if [ $retval -eq 128 ]; then
        # Case where commit was not found in the git tree
        conflicts=true
        echo $out >> bp_error.log
    elif [ $retval -eq 1 ]; then
        # Case of errors while trying to apply the commit
        if [[ $out =~ "allow-empty" ]]; then
            # Don't log/report error if it was an empty commit
            # Skip the commit and continue
            git cherry-pick --skip
            continue
        fi
        # Abort the cherry pick in case there was a conflict
        git cherry-pick --abort
        conflicts=true
        echo $out >> bp_error.log
    elif [ $retval -eq 0 ]; then
        # Case where cherry pick was clean and successful
        # Then, test if the commit passes the build
        mkout=$(make -j8 2>&1 1>/dev/null)
        ret=$?
        if [ $ret -ne 0 ]; then
            # Reset to previous commit stage in case build failed and log it
            git reset --hard HEAD~ 1>/dev/null
            echo "Build failed for $line" >> bp_error.log
        fi
        testout=$(ASAN_OPTIONS="detect_leaks=0" ./src/suricata -u 2>&1 1>/dev/null)
        ret=$?
        if [ $ret -ne 0 ]; then
            # Reset to previous commit stage in case unittests failed and log it
            git reset --hard HEAD~ 1>/dev/null
            echo "Unittests failed for $line" >> bp_error.log
        fi
    fi
done < "${SCRIPTDIR}/$1"

if [ "$conflicts" = true ]; then
    echo "Some commits were not cleanly backported. Please check the error report."
fi
