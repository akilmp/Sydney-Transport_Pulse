DATE ?= $(shell date +%Y%m%d)

.PHONY: fetch_gtfs_static
# Download daily GTFS static schedule and push to MinIO s3://stp/gtfs_static/
fetch_gtfs_static:
	poetry run python scripts/fetch_gtfs_static.py $(DATE)

