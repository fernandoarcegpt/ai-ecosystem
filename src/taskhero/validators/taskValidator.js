'use strict';

const { ValidationError } = require('../errors/AppError');
const {
  VALID_STATUSES,
  MIN_POWER_LEVEL,
  MAX_POWER_LEVEL,
} = require('../models/task');

/**
 * Validate the payload for creating a task.
 * Enforces required fields and value ranges at the system boundary.
 * @param {object} body Raw request body.
 * @returns {{title: string, description: string, powerLevel: number, status: string}}
 * @throws {ValidationError}
 */
function validateCreate(body) {
  const errors = {};
  const data = body && typeof body === 'object' ? body : {};

  // title: required, non-empty string
  if (typeof data.title !== 'string' || data.title.trim() === '') {
    errors.title = 'title is required and must be a non-empty string';
  }

  // description: optional string
  if (data.description !== undefined && typeof data.description !== 'string') {
    errors.description = 'description must be a string';
  }

  // powerLevel: required integer within range
  const powerLevel = data.powerLevel;
  if (!Number.isInteger(powerLevel) || powerLevel < MIN_POWER_LEVEL || powerLevel > MAX_POWER_LEVEL) {
    errors.powerLevel = `powerLevel must be an integer between ${MIN_POWER_LEVEL} and ${MAX_POWER_LEVEL}`;
  }

  // status: optional, defaults to 'pending'
  const status = data.status ?? 'pending';
  if (!VALID_STATUSES.includes(status)) {
    errors.status = `status must be one of: ${VALID_STATUSES.join(', ')}`;
  }

  if (Object.keys(errors).length > 0) {
    throw new ValidationError('Invalid task payload', errors);
  }

  return {
    title: data.title.trim(),
    description: (data.description ?? '').trim(),
    powerLevel,
    status,
  };
}

/**
 * Validate the payload for updating a task. All fields are optional, but at
 * least one recognised field must be present, and any provided field must be
 * valid.
 * @param {object} body Raw request body.
 * @returns {object} The subset of validated fields to apply.
 * @throws {ValidationError}
 */
function validateUpdate(body) {
  const errors = {};
  const data = body && typeof body === 'object' ? body : {};
  const changes = {};

  if (data.title !== undefined) {
    if (typeof data.title !== 'string' || data.title.trim() === '') {
      errors.title = 'title must be a non-empty string';
    } else {
      changes.title = data.title.trim();
    }
  }

  if (data.description !== undefined) {
    if (typeof data.description !== 'string') {
      errors.description = 'description must be a string';
    } else {
      changes.description = data.description.trim();
    }
  }

  if (data.powerLevel !== undefined) {
    if (
      !Number.isInteger(data.powerLevel) ||
      data.powerLevel < MIN_POWER_LEVEL ||
      data.powerLevel > MAX_POWER_LEVEL
    ) {
      errors.powerLevel = `powerLevel must be an integer between ${MIN_POWER_LEVEL} and ${MAX_POWER_LEVEL}`;
    } else {
      changes.powerLevel = data.powerLevel;
    }
  }

  if (data.status !== undefined) {
    if (!VALID_STATUSES.includes(data.status)) {
      errors.status = `status must be one of: ${VALID_STATUSES.join(', ')}`;
    } else {
      changes.status = data.status;
    }
  }

  if (Object.keys(errors).length > 0) {
    throw new ValidationError('Invalid task update payload', errors);
  }

  if (Object.keys(changes).length === 0) {
    throw new ValidationError('No valid fields provided to update');
  }

  return changes;
}

module.exports = { validateCreate, validateUpdate };
