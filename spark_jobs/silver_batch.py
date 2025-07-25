import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, row_number
from pyspark.sql.window import Window

WAREHOUSE = os.getenv("ICEBERG_WAREHOUSE", "s3a://stp/warehouse")

spark = (
    SparkSession.builder.appName("silver_batch")
    .config("spark.sql.catalog.stp", "org.apache.iceberg.spark.SparkCatalog")
    .config("spark.sql.catalog.stp.type", "hadoop")
    .config("spark.sql.catalog.stp.warehouse", WAREHOUSE)
    .getOrCreate()
)

bronze = spark.read.format("iceberg").load("stp.bronze_bus_positions")

# example transformation: deduplicate by kafka offset
w = Window.partitionBy("key").orderBy(col("offset").desc())
clean = (
    bronze.withColumn("rn", row_number().over(w))
    .filter(col("rn") == 1)
    .drop("rn")
)

clean.write.format("iceberg").mode("append").save("stp.silver_bus_positions")
