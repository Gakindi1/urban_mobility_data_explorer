import Fastify from 'fastify';
import cors from '@fastify/cors';
import { PrismaClient } from '@prisma/client';
import dotenv from 'dotenv';
import apiRoutes from './routes/api.js';

dotenv.config();

const prisma = new PrismaClient();
const fastify = Fastify({
  logger: true
});

// Register CORS
await fastify.register(cors, {
  origin: true
});

// Add Prisma to fastify instance
fastify.decorate('prisma', prisma);

// Register routes
fastify.register(apiRoutes, { prefix: '/api' });

// Health check
fastify.get('/health', async (request, reply) => {
  return { status: 'ok', timestamp: new Date().toISOString() };
});

// Start server
const start = async () => {
  try {
    const port = process.env.PORT || 3000;
    await fastify.listen({ port, host: '0.0.0.0' });
    console.log(`🚀 Server running on http://localhost:${port}`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();
