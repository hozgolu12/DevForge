import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';
import { logger } from './logger';
import healthRouter from './health';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Security and utility middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Request logger middleware
app.use((req, res, next) => {
  logger.info(`${req.method} ${req.url}`, {
    ip: req.ip,
    userAgent: req.headers['user-agent'],
  });
  next();
});

// Health check endpoint
app.use('/health', healthRouter);

// Sample api endpoint
app.get('/api/info', (req, res) => {
  res.json({
    message: 'Welcome to DevForge Express Platform',
    status: 'operational',
    databasesAvailable: ['PostgreSQL', 'MongoDB', 'Redis', 'Neo4j'],
  });
});

// Error handling middleware
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  logger.error('Unhandled request exception', err);
  res.status(500).json({
    error: 'Internal Server Error',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong',
  });
});

app.listen(PORT, () => {
  logger.info(`Express server running on http://localhost:${PORT} in ${process.env.NODE_ENV || 'development'} mode`);
  logger.info(`Debug inspector available (if run with inspect) on port 9229`);
});
