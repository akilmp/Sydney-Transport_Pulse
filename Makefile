DATE ?= $(shell date +%Y%m%d)

.PHONY: fetch_gtfs_static
fetch_gtfs_static:
	python scripts/fetch_gtfs_static.py $(DATE)

