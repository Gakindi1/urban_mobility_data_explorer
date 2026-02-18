/**
 * API Routes for Urban Mobility Data Explorer
 */

export default async function apiRoutes(fastify, options) {
  const prisma = fastify.prisma;

  // GET /api/trips - Get trips with filters
  fastify.get('/trips', async (request, reply) => {
    const {
      borough,
      startDate,
      endDate,
      minFare,
      maxFare,
      paymentType,
      limit = 100,
      offset = 0
    } = request.query;

    const where = {};

    // Filter by borough (pickup location)
    if (borough) {
      where.pickupZone = {
        borough: borough
      };
    }

    // Filter by date range
    if (startDate || endDate) {
      where.pickupDatetime = {};
      if (startDate) where.pickupDatetime.gte = new Date(startDate);
      if (endDate) where.pickupDatetime.lte = new Date(endDate);
    }

    // Filter by fare range
    if (minFare || maxFare) {
      where.fareAmount = {};
      if (minFare) where.fareAmount.gte = parseFloat(minFare);
      if (maxFare) where.fareAmount.lte = parseFloat(maxFare);
    }

    // Filter by payment type
    if (paymentType) {
      where.paymentType = parseInt(paymentType);
    }

    const trips = await prisma.trip.findMany({
      where,
      include: {
        pickupZone: true,
        dropoffZone: true
      },
      take: parseInt(limit),
      skip: parseInt(offset),
      orderBy: {
        pickupDatetime: 'desc'
      }
    });

    const total = await prisma.trip.count({ where });

    return {
      trips,
      pagination: {
        total,
        limit: parseInt(limit),
        offset: parseInt(offset),
        hasMore: total > parseInt(offset) + parseInt(limit)
      }
    };
  });


  // GET /api/zones - Get all taxi zones
  fastify.get('/zones', async (request, reply) => {
    const zones = await prisma.zone.findMany({
      orderBy: {
        borough: 'asc'
      }
    });

    return { zones };
  });

  // GET /api/insights/hourly-demand - Hourly trip demand pattern
  fastify.get('/insights/hourly-demand', async (request, reply) => {
    const hourlyData = await prisma.$queryRaw`
      SELECT 
        hour_of_day,
        COUNT(*) as trip_count,
        AVG(fare_amount) as avg_fare,
        AVG(trip_distance) as avg_distance,
        AVG(trip_duration_minutes) as avg_duration
      FROM trips
      GROUP BY hour_of_day
      ORDER BY hour_of_day
    `;

    return { hourlyDemand: hourlyData };
  });

  // GET /api/insights/borough-stats - Statistics by borough
  fastify.get('/insights/borough-stats', async (request, reply) => {
    const boroughStats = await prisma.$queryRaw`
      SELECT 
        z.borough,
        COUNT(t.trip_id) as trip_count,
        AVG(t.fare_amount) as avg_fare,
        AVG(t.trip_distance) as avg_distance,
        AVG(t.tip_percentage) as avg_tip_percentage,
        SUM(t.total_amount) as total_revenue
      FROM trips t
      JOIN zones z ON t.pu_location_id = z.location_id
      GROUP BY z.borough
      ORDER BY trip_count DESC
    `;

    return { boroughStats };
  });

  // GET /api/insights/payment-distribution - Payment type distribution
  fastify.get('/insights/payment-distribution', async (request, reply) => {
    const paymentDist = await prisma.$queryRaw`
      SELECT 
        payment_type,
        COUNT(*) as count,
        AVG(tip_percentage) as avg_tip_percentage
      FROM trips
      GROUP BY payment_type
      ORDER BY count DESC
    `;

    const paymentTypes = {
      1: 'Credit Card',
      2: 'Cash',
      3: 'No Charge',
      4: 'Dispute',
      5: 'Unknown',
      6: 'Voided Trip'
    };

    const formatted = paymentDist.map(p => ({
      paymentType: paymentTypes[p.payment_type] || 'Unknown',
      count: Number(p.count),
      avgTipPercentage: Number(p.avg_tip_percentage)
    }));

    return { paymentDistribution: formatted };
  });


  // GET /api/insights/weekend-vs-weekday - Weekend vs Weekday comparison
  fastify.get('/insights/weekend-vs-weekday', async (request, reply) => {
    const comparison = await prisma.$queryRaw`
      SELECT 
        is_weekend,
        COUNT(*) as trip_count,
        AVG(fare_amount) as avg_fare,
        AVG(trip_distance) as avg_distance,
        AVG(speed_mph) as avg_speed
      FROM trips
      GROUP BY is_weekend
    `;

    return { weekendVsWeekday: comparison };
  });

  // GET /api/insights/speed-by-hour - Average speed by hour (congestion analysis)
  fastify.get('/insights/speed-by-hour', async (request, reply) => {
    const speedData = await prisma.$queryRaw`
      SELECT 
        hour_of_day,
        AVG(speed_mph) as avg_speed,
        COUNT(*) as trip_count
      FROM trips
      WHERE speed_mph > 0 AND speed_mph < 100
      GROUP BY hour_of_day
      ORDER BY hour_of_day
    `;

    return { speedByHour: speedData };
  });

  // GET /api/insights/top-routes - Most popular routes
  fastify.get('/insights/top-routes', async (request, reply) => {
    const { limit = 10 } = request.query;

    const topRoutes = await prisma.$queryRaw`
      SELECT 
        pz.zone as pickup_zone,
        pz.borough as pickup_borough,
        dz.zone as dropoff_zone,
        dz.borough as dropoff_borough,
        COUNT(*) as trip_count,
        AVG(t.fare_amount) as avg_fare,
        AVG(t.trip_distance) as avg_distance
      FROM trips t
      JOIN zones pz ON t.pu_location_id = pz.location_id
      JOIN zones dz ON t.do_location_id = dz.location_id
      GROUP BY pz.zone, pz.borough, dz.zone, dz.borough
      ORDER BY trip_count DESC
      LIMIT ${parseInt(limit)}
    `;

    return { topRoutes };
  });

  // GET /api/insights/summary - Overall summary statistics
  fastify.get('/insights/summary', async (request, reply) => {
    const summary = await prisma.$queryRaw`
      SELECT 
        COUNT(*) as total_trips,
        SUM(total_amount) as total_revenue,
        AVG(fare_amount) as avg_fare,
        AVG(trip_distance) as avg_distance,
        AVG(trip_duration_minutes) as avg_duration,
        AVG(tip_percentage) as avg_tip_percentage,
        MAX(fare_amount) as max_fare,
        MIN(fare_amount) as min_fare
      FROM trips
    `;

    const zoneCount = await prisma.zone.count();
    const qualityLogCount = await prisma.dataQualityLog.count();

    // Convert BigInt values to Numbers for JSON serialization
    const summaryData = summary[0];
    const formattedSummary = {
      totalTrips: Number(summaryData.total_trips),
      totalRevenue: Number(summaryData.total_revenue),
      avgFare: Number(summaryData.avg_fare),
      avgDistance: Number(summaryData.avg_distance),
      avgDuration: Number(summaryData.avg_duration),
      avgTipPercentage: Number(summaryData.avg_tip_percentage),
      maxFare: Number(summaryData.max_fare),
      minFare: Number(summaryData.min_fare)
    };

    return {
      summary: formattedSummary,
      totalZones: zoneCount,
      excludedRecords: qualityLogCount
    };
  });
}
