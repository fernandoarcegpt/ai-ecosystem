'use strict';

const express = require('express');
const controller = require('../controllers/taskController');

/**
 * Task resource routes. Mounted under `/tasks` by the app.
 */
const router = express.Router();

router.get('/', controller.listTasks);
router.post('/', controller.createTask);
router.get('/:id', controller.getTask);
router.put('/:id', controller.updateTask);
router.delete('/:id', controller.deleteTask);

module.exports = router;
