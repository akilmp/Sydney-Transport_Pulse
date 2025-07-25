import os
from pyspark.sql import SparkSession

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
WAREHOUSE = os.getenv("ICEBERG_WAREHOUSE", "s3a://stp/warehouse")

spark = (
    SparkSession.builder.appName("bronze_stream")
    .config("spark.sql.catalog.stp", "org.apache.iceberg.spark.SparkCatalog")
    .config("spark.sql.catalog.stp.type", "hadoop")
    .config("spark.sql.catalog.stp.warehouse", WAREHOUSE)
    .getOrCreate()
)

stream_df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BROKER)
    .option("subscribe", "bus_positions")
    .load()
)

query = (
    stream_df.writeStream.format("iceberg")
    .outputMode("append")
    .option("checkpointLocation", "/tmp/checkpoints/bronze")
    .toTable("stp.bronze_bus_positions")
    .start()
)

query.awaitTermination()
