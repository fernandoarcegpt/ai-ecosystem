'use strict';

const crypto = require('crypto');

/**
 * In-memory storage service (Repository) for tasks.
 *
 * Holds tasks in a Map keyed by id. This is intentionally process-local and
 * non-persistent; it can be swapped for a database-backed repository later
 * without changing the service/controller layers.
 */
class TaskStore {
  constructor() {
    /** @type {Map<string, object>} */
    this._tasks = new Map();
  }

  /**
   * Persist a new task. Generates the id, timestamps, and defaults.
   * @param {object} data Pre-validated task fields.
   * @returns {object} The stored task.
   */
  create(data) {
    const now = new Date().toISOString();
    const task = {
      id: crypto.randomUUID(),
      title: data.title,
      description: data.description ?? '',
      powerLevel: data.powerLevel,
      xp: data.xp,
      status: data.status,
      completedAt: null,
      createdAt: now,
      updatedAt: now,
    };
    this._tasks.set(task.id, task);
    return { ...task };
  }

  /**
   * @returns {object[]} A shallow copy of all tasks.
   */
  findAll() {
    return Array.from(this._tasks.values()).map((t) => ({ ...t }));
  }

  /**
   * @param {string} id
   * @returns {object|null} The task, or null if not found.
   */
  findById(id) {
    const task = this._tasks.get(id);
    return task ? { ...task } : null;
  }

  /**
   * Merge `changes` into an existing task.
   * @param {string} id
   * @param {object} changes
   * @returns {object|null} The updated task, or null if not found.
   */
  update(id, changes) {
    const existing = this._tasks.get(id);
    if (!existing) return null;
    const updated = {
      ...existing,
      ...changes,
      id: existing.id,
      createdAt: existing.createdAt,
      updatedAt: new Date().toISOString(),
    };
    this._tasks.set(id, updated);
    return { ...updated };
  }

  /**
   * @param {string} id
   * @returns {boolean} true if a task was removed.
   */
  delete(id) {
    return this._tasks.delete(id);
  }

  /** Remove all tasks (primarily for tests). */
  clear() {
    this._tasks.clear();
  }
}

// Export a singleton so all layers share one store instance.
module.exports = new TaskStore();
module.exports.TaskStore = TaskStore;
