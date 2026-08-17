'use strict';

const { AppError } = require('../errors/AppError');

/**
 * 404 handler for unmatched routes. Placed after all routes.
 */
function notFoundHandler(req, res, next) {
  res.status(404).json({
    error: {
      message: `Route not found: ${req.method} ${req.originalUrl}`,
      status: 404,
    },
  });
}

/**
 * Centralised error-handling middleware. Express identifies it by its four
 * arguments. Formats a consistent JSON error response and hides internal
 * details for unexpected (non-operational) errors.
 */
// eslint-disable-next-line no-unused-vars
function errorHandler(err, req, res, next) {
  const isKnown = err instanceof AppError;
  const statusCode = isKnown ? err.statusCode : 500;

  // Log server-side for observability. Operational 4xx errors log at a lower
  // signal than unexpected 5xx errors.
  if (statusCode >= 500) {
    console.error('[TaskHero] Unhandled error:', err);
  }

  const body = {
    error: {
      message: isKnown ? err.message : 'Internal server error',
      status: statusCode,
    },
  };

  if (isKnown && err.details) {
    body.error.details = err.details;
  }

  res.status(statusCode).json(body);
}

module.exports = { notFoundHandler, errorHandler };
