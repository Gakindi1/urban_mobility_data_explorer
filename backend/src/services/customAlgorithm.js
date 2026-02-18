/**
 * CUSTOM ALGORITHM IMPLEMENTATION (Manual - No Built-in Libraries)
 * 
 * Algorithm: Percentile-Based Outlier Detection using Manual QuickSort
 * Purpose: Identify and filter outliers in trip data (fare, distance, duration)
 * 
 * Time Complexity: O(n log n) - QuickSort
 * Space Complexity: O(n) - for values array
 */

export class OutlierDetector {
  /**
   * Manual QuickSort Implementation
   * @param {Array} arr - Array to sort
   * @param {number} low - Starting index
   * @param {number} high - Ending index
   */
  quickSort(arr, low, high) {
    if (low < high) {
      const pi = this.partition(arr, low, high);
      this.quickSort(arr, low, pi - 1);
      this.quickSort(arr, pi + 1, high);
    }
  }

  /**
   * Partition function for QuickSort
   */
  partition(arr, low, high) {
    const pivot = arr[high];
    let i = low - 1;
    
    for (let j = low; j < high; j++) {
      if (arr[j] < pivot) {
        i++;
        // Manual swap
        const temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
      }
    }
    
    // Final swap
    const temp = arr[i + 1];
    arr[i + 1] = arr[high];
    arr[high] = temp;
    
    return i + 1;
  }

  /**
   * Detect outliers using IQR method (Interquartile Range)
   * @param {Array} data - Array of objects
   * @param {string} field - Field name to analyze
   * @returns {Object} - { clean: [], outliers: [], stats: {} }
   */
  detectOutliers(data, field) {
    // Extract values manually
    const values = [];
    for (let i = 0; i < data.length; i++) {
      const value = parseFloat(data[i][field]);
      if (!isNaN(value) && value !== null && value !== undefined) {
        values.push(value);
      }
    }

    if (values.length === 0) {
      return { clean: [], outliers: [], stats: {} };
    }

    // Sort using manual QuickSort
    this.quickSort(values, 0, values.length - 1);

    // Calculate quartiles manually
    const q1Index = Math.floor(values.length * 0.25);
    const q3Index = Math.floor(values.length * 0.75);
    const medianIndex = Math.floor(values.length * 0.5);
    
    const q1 = values[q1Index];
    const q3 = values[q3Index];
    const median = values[medianIndex];
    const iqr = q3 - q1;


    // Calculate bounds
    const lowerBound = q1 - 1.5 * iqr;
    const upperBound = q3 + 1.5 * iqr;

    // Separate clean data from outliers
    const clean = [];
    const outliers = [];

    for (let i = 0; i < data.length; i++) {
      const value = parseFloat(data[i][field]);
      if (isNaN(value) || value === null || value === undefined) {
        outliers.push(data[i]);
      } else if (value >= lowerBound && value <= upperBound) {
        clean.push(data[i]);
      } else {
        outliers.push(data[i]);
      }
    }

    return {
      clean,
      outliers,
      stats: {
        total: data.length,
        cleanCount: clean.length,
        outlierCount: outliers.length,
        q1,
        q3,
        median,
        iqr,
        lowerBound,
        upperBound,
        min: values[0],
        max: values[values.length - 1]
      }
    };
  }

  /**
   * Multi-field outlier detection
   * Removes records that are outliers in ANY of the specified fields
   */
  detectMultiFieldOutliers(data, fields) {
    let cleanData = data;
    const allOutliers = [];
    const fieldStats = {};

    for (const field of fields) {
      const result = this.detectOutliers(cleanData, field);
      cleanData = result.clean;
      allOutliers.push(...result.outliers);
      fieldStats[field] = result.stats;
    }

    return {
      clean: cleanData,
      outliers: allOutliers,
      fieldStats
    };
  }
}
