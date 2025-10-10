#!/usr/bin/env bash
# Usage: ./01_query.sh "term1" "term2" ...

RUNTIME=`date "+%Y%M%d%H%m"`

# Exit immediately on errors
set -euo pipefail

# Directory to store results
OUTDIR="../data/pubmed_results"
mkdir -p "$OUTDIR"

# Log file
LOGFILE="$OUTDIR/log01_${RUNTIME}.txt"
touch "$LOGFILE"

# Output file
OUTFILE="${OUTDIR}/prefilter_${RUNTIME}.xml.gz"

# Loop over all provided MeSH terms
SEARCH_STRING=""
for TERM in "$@"; do
    CLEAN_TERM=$(echo "TERM" | xargs | tr ' ' ' ')
    if [[ -z "$SEARCH_STRING" ]]; then
	SEARCH_STRING="${CLEAN_TERM}[MESH]"
    else
        SEARCH_STRING="${SEARCH_STRING} OR ${CLEAN_TERM}[MESH]"
    fi
done

echo "[$(date)] Fetching results for MeSH term(s): $SEARCH_STRING" | tee -a "$LOGFILE"

# Perform search with EDirect and create prefilter.xml.gz
xsearch -query "SEARCH_STRING" | \
    xfetch | \
    gzip > "$OUTFILE"
	
echo "[$(date)] Saved ${OUTFILE}" | tee -a "$LOGFILE"

