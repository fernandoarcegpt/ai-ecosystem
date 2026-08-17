'use strict';

const express = require('express');
const taskRoutes = require('./routes/taskRoutes');
const { notFoundHandler, errorHandler } = require('./middleware/errorHandler');

/**
 * Build and configure the Express application. Exported as a factory so tests
 * can create isolated instances without binding to a port.
 * @returns {import('express').Express}
 */
function createApp() {
  const app = express();

  // Parse JSON request bodies.
  app.use(express.json());

  // Health check.
  app.get('/health', (req, res) => {
    res.status(200).json({ status: 'ok', service: 'taskhero' });
  });

  // Task resource.
  app.use('/tasks', taskRoutes);

  // 404 for anything unmatched, then the central error handler.
  app.use(notFoundHandler);
  app.use(errorHandler);

  return app;
}

module.exports = createApp;
