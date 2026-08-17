'use strict';

/**
 * Base application error carrying an HTTP status code so the error-handling
 * middleware can format a proper response.
 */
class AppError extends Error {
  /**
   * @param {string} message
   * @param {number} statusCode
   * @param {object} [details] Optional structured details (e.g. validation errors)
   */
  constructor(message, statusCode = 500, details = undefined) {
    super(message);
    this.name = this.constructor.name;
    this.statusCode = statusCode;
    this.details = details;
    // Distinguishes trusted operational errors from unexpected bugs.
    this.isOperational = true;
    Error.captureStackTrace(this, this.constructor);
  }
}

/** 400 - the client sent invalid data. */
class ValidationError extends AppError {
  constructor(message = 'Validation failed', details = undefined) {
    super(message, 400, details);
  }
}

/** 404 - the requested resource does not exist. */
class NotFoundError extends AppError {
  constructor(message = 'Resource not found') {
    super(message, 404);
  }
}

module.exports = { AppError, ValidationError, NotFoundError };
