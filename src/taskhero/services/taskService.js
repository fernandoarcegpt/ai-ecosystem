'use strict';

const store = require('./taskStore');
const { NotFoundError } = require('../errors/AppError');
const { validateCreate, validateUpdate } = require('../validators/taskValidator');
const { xpForPowerLevel } = require('../models/task');

/**
 * Business logic for tasks (Service layer). Owns the gamification rules:
 * XP is derived from powerLevel, and completing a task stamps `completedAt`.
 */

/**
 * Create a new task, deriving its XP from the power level.
 * @param {object} body Raw request body.
 * @returns {object} The created task.
 */
function createTask(body) {
  const data = validateCreate(body);
  const xp = xpForPowerLevel(data.powerLevel);
  return store.create({ ...data, xp });
}

/**
 * @returns {object[]} All tasks.
 */
function listTasks() {
  return store.findAll();
}

/**
 * @param {string} id
 * @returns {object} The task.
 * @throws {NotFoundError}
 */
function getTask(id) {
  const task = store.findById(id);
  if (!task) throw new NotFoundError(`Task ${id} not found`);
  return task;
}

/**
 * Update a task. Recomputes XP if powerLevel changes and manages the
 * `completedAt` timestamp when the status transitions to/from completed.
 * @param {string} id
 * @param {object} body Raw request body.
 * @returns {object} The updated task.
 * @throws {NotFoundError}
 */
function updateTask(id, body) {
  const existing = store.findById(id);
  if (!existing) throw new NotFoundError(`Task ${id} not found`);

  const changes = validateUpdate(body);

  // XP tracks the current power level.
  if (changes.powerLevel !== undefined) {
    changes.xp = xpForPowerLevel(changes.powerLevel);
  }

  // Manage completion timestamp on status transitions.
  if (changes.status !== undefined && changes.status !== existing.status) {
    changes.completedAt = changes.status === 'completed' ? new Date().toISOString() : null;
  }

  return store.update(id, changes);
}

/**
 * Delete a task.
 * @param {string} id
 * @throws {NotFoundError}
 */
function deleteTask(id) {
  const removed = store.delete(id);
  if (!removed) throw new NotFoundError(`Task ${id} not found`);
}

module.exports = {
  createTask,
  listTasks,
  getTask,
  updateTask,
  deleteTask,
};
