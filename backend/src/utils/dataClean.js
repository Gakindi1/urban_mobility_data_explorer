/**
 * Data Cleaning and Feature Engineering Utilities
 */

export class DataCleaner {
  /**
   * Clean and validate trip record
   */
  cleanTripRecord(record) {
    const issues = [];

    // Parse dates
    const pickupDate = new Date(record.tpep_pickup_datetime);
    const dropoffDate = new Date(record.tpep_dropoff_datetime);

    // Validation checks
    if (isNaN(pickupDate.getTime())) {
      issues.push('Invalid pickup datetime');
    }
    if (isNaN(dropoffDate.getTime())) {
      issues.push('Invalid dropoff datetime');
    }

    // Check for temporal anomalies (should be January 2019)
    if (pickupDate.getFullYear() !== 2019 || pickupDate.getMonth() !== 0) {
      issues.push(`Temporal anomaly: ${record.tpep_pickup_datetime}`);
    }

    // Check for logical errors
    if (dropoffDate <= pickupDate) {
      issues.push('Dropoff before pickup');
    }

    // Check for missing or invalid values
    const tripDistance = parseFloat(record.trip_distance);
    if (isNaN(tripDistance) || tripDistance < 0) {
      issues.push('Invalid trip distance');
    }

    const fareAmount = parseFloat(record.fare_amount);
    if (isNaN(fareAmount) || fareAmount < 0) {
      issues.push('Invalid fare amount');
    }

    // Check for suspicious zero-distance trips with fare
    if (tripDistance === 0 && fareAmount > 0) {
      issues.push('Zero distance with fare charged');
    }

    return {
      isValid: issues.length === 0,
      issues,
      record
    };
  }


  /**
   * Engineer derived features from trip record
   */
  engineerFeatures(record) {
    const pickupDate = new Date(record.tpep_pickup_datetime);
    const dropoffDate = new Date(record.tpep_dropoff_datetime);

    // Feature 1: Trip Duration (minutes)
    const tripDurationMinutes = Math.round(
      (dropoffDate - pickupDate) / (1000 * 60)
    );

    // Feature 2: Speed (mph)
    const tripDistance = parseFloat(record.trip_distance);
    const speedMph = tripDurationMinutes > 0
      ? (tripDistance / tripDurationMinutes) * 60
      : 0;

    // Feature 3: Tip Percentage
    const fareAmount = parseFloat(record.fare_amount);
    const tipAmount = parseFloat(record.tip_amount);
    const tipPercentage = fareAmount > 0
      ? (tipAmount / fareAmount) * 100
      : 0;

    // Feature 4: Hour of Day
    const hourOfDay = pickupDate.getHours();

    // Feature 5: Day of Week (0 = Sunday, 6 = Saturday)
    const dayOfWeek = pickupDate.getDay();

    // Feature 6: Is Weekend
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;

    // Feature 7: Fare per Mile
    const farePerMile = tripDistance > 0
      ? parseFloat(record.total_amount) / tripDistance
      : 0;

    return {
      tripDurationMinutes,
      speedMph: Math.round(speedMph * 100) / 100,
      tipPercentage: Math.round(tipPercentage * 100) / 100,
      hourOfDay,
      dayOfWeek,
      isWeekend,
      farePerMile: Math.round(farePerMile * 100) / 100
    };
  }

  /**
   * Check for duplicate records
   */
  isDuplicate(record, seenRecords) {
    const key = `${record.tpep_pickup_datetime}_${record.PULocationID}_${record.DOLocationID}_${record.fare_amount}`;
    if (seenRecords.has(key)) {
      return true;
    }
    seenRecords.add(key);
    return false;
  }
}
