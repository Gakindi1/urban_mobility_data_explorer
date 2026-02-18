-- CreateTable
CREATE TABLE "zones" (
    "location_id" INTEGER NOT NULL,
    "borough" VARCHAR(50) NOT NULL,
    "zone" VARCHAR(100) NOT NULL,
    "service_zone" VARCHAR(50) NOT NULL,
    "geometry" TEXT,

    CONSTRAINT "zones_pkey" PRIMARY KEY ("location_id")
);

-- CreateTable
CREATE TABLE "trips" (
    "trip_id" SERIAL NOT NULL,
    "vendor_id" INTEGER NOT NULL,
    "pickup_datetime" TIMESTAMP(3) NOT NULL,
    "dropoff_datetime" TIMESTAMP(3) NOT NULL,
    "passenger_count" INTEGER,
    "trip_distance" DECIMAL(10,2) NOT NULL,
    "rate_code_id" INTEGER NOT NULL,
    "store_and_fwd_flag" CHAR(1) NOT NULL,
    "pu_location_id" INTEGER NOT NULL,
    "do_location_id" INTEGER NOT NULL,
    "payment_type" INTEGER NOT NULL,
    "fare_amount" DECIMAL(10,2) NOT NULL,
    "extra" DECIMAL(10,2) NOT NULL,
    "mta_tax" DECIMAL(10,2) NOT NULL,
    "tip_amount" DECIMAL(10,2) NOT NULL,
    "tolls_amount" DECIMAL(10,2) NOT NULL,
    "improvement_surcharge" DECIMAL(10,2) NOT NULL,
    "total_amount" DECIMAL(10,2) NOT NULL,
    "congestion_surcharge" DECIMAL(10,2),
    "trip_duration_minutes" INTEGER,
    "speed_mph" DECIMAL(10,2),
    "tip_percentage" DECIMAL(5,2),
    "hour_of_day" INTEGER NOT NULL,
    "day_of_week" INTEGER NOT NULL,
    "is_weekend" BOOLEAN NOT NULL,
    "fare_per_mile" DECIMAL(10,2),

    CONSTRAINT "trips_pkey" PRIMARY KEY ("trip_id")
);

-- CreateTable
CREATE TABLE "data_quality_log" (
    "log_id" SERIAL NOT NULL,
    "record_data" TEXT NOT NULL,
    "exclusion_reason" VARCHAR(200) NOT NULL,
    "logged_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "data_quality_log_pkey" PRIMARY KEY ("log_id")
);

-- CreateIndex
CREATE INDEX "trips_pickup_datetime_idx" ON "trips"("pickup_datetime");

-- CreateIndex
CREATE INDEX "trips_pu_location_id_idx" ON "trips"("pu_location_id");

-- CreateIndex
CREATE INDEX "trips_do_location_id_idx" ON "trips"("do_location_id");

-- CreateIndex
CREATE INDEX "trips_hour_of_day_idx" ON "trips"("hour_of_day");

-- AddForeignKey
ALTER TABLE "trips" ADD CONSTRAINT "trips_pu_location_id_fkey" FOREIGN KEY ("pu_location_id") REFERENCES "zones"("location_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "trips" ADD CONSTRAINT "trips_do_location_id_fkey" FOREIGN KEY ("do_location_id") REFERENCES "zones"("location_id") ON DELETE RESTRICT ON UPDATE CASCADE;
