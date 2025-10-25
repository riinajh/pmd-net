#!/bin/bash
# Usage: ./01_query.sh "term1" "term2" ...

RUNTIME=`date "+%Y%m%d%H%M"`

# Exit immediately on errors
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $SCRIPT_DIR

# Directory to store results
OUTDIR="../data/pubmed_results"
mkdir -p $OUTDIR

# Log file
LOGFILE="$OUTDIR/log01_${RUNTIME}.txt"
touch $LOGFILE

# Output file
OUTFILE="${OUTDIR}/prefilter_${RUNTIME}.xml"
touch $OUTFILE

# Loop over all provided MeSH terms
SEARCH_STRING=""
for TERM in "$@"; do
    if [ -z $SEARCH_STRING ]; then
    	SEARCH_STRING="$TERM [MESH]"
    else
        SEARCH_STRING="${SEARCH_STRING} OR $TERM [MESH]"
    fi
done

echo "[$(date)] Fetching results for MeSH term(s): $SEARCH_STRING" | tee -a $LOGFILE

# Perform search with EDirect and create prefilter.xml.gz
echo works > $OUTFILE
xsearch -query $SEARCH_STRING >> $OUTFILE
	
echo "[$(date)] Saved ${OUTFILE}" | tee -a $LOGFILE

