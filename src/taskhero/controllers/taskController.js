'use strict';

const taskService = require('../services/taskService');

/**
 * HTTP controllers for task endpoints. Controllers translate between HTTP and
 * the service layer: they read request data, call the service, and shape the
 * response with the correct status code. Errors are forwarded to the
 * error-handling middleware via `next`.
 */

/** GET /tasks */
function listTasks(req, res) {
  const tasks = taskService.listTasks();
  res.status(200).json({ data: tasks, count: tasks.length });
}

/** POST /tasks */
function createTask(req, res, next) {
  try {
    const task = taskService.createTask(req.body);
    res.status(201).json({ data: task });
  } catch (err) {
    next(err);
  }
}

/** GET /tasks/:id */
function getTask(req, res, next) {
  try {
    const task = taskService.getTask(req.params.id);
    res.status(200).json({ data: task });
  } catch (err) {
    next(err);
  }
}

/** PUT /tasks/:id */
function updateTask(req, res, next) {
  try {
    const task = taskService.updateTask(req.params.id, req.body);
    res.status(200).json({ data: task });
  } catch (err) {
    next(err);
  }
}

/** DELETE /tasks/:id */
function deleteTask(req, res, next) {
  try {
    taskService.deleteTask(req.params.id);
    res.status(204).send();
  } catch (err) {
    next(err);
  }
}

module.exports = {
  listTasks,
  createTask,
  getTask,
  updateTask,
  deleteTask,
};
