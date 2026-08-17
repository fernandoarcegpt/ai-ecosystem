'use strict';

/**
 * Unit tests for the TaskHero API domain layer.
 *
 * Runner: Node's built-in test runner (`node --test`), matching package.json's
 * "test" script. No external deps (express/jest are not installed).
 *
 * Coverage (per team-lead brief, aligned to backend-dev's actual code):
 *   1. GET  /tasks  -> taskStore.findAll (task list retrieval)
 *   2. POST /tasks  -> validateCreate + taskStore.create (create with power level)
 *   3. XP calculation logic (model.xpForPowerLevel)
 *   4. Error handling for invalid input (ValidationError / NotFoundError)
 *
 * Two layers are covered:
 *   - Unit tests on the model/validator/store (no HTTP, fully isolated).
 *   - HTTP integration tests that boot backend-dev's Express app (app.js
 *     factory) on an ephemeral port and drive it with the built-in fetch.
 */

const { test, describe, beforeEach, after } = require('node:test');
const assert = require('node:assert/strict');

const createApp = require('../app');
const store = require('../services/taskStore');
const { TaskStore } = require('../services/taskStore');
const { validateCreate, validateUpdate } = require('../validators/taskValidator');
const {
  xpForPowerLevel,
  XP_BY_POWER_LEVEL,
  VALID_STATUSES,
  MIN_POWER_LEVEL,
  MAX_POWER_LEVEL,
} = require('../models/task');
const { AppError, ValidationError, NotFoundError } = require('../errors/AppError');

/**
 * Simulate the create-task flow a POST /tasks controller performs:
 * validate the raw body, compute XP from the power level, then persist.
 * @param {object} body Raw request body.
 * @param {object} repo Task store to persist into.
 * @returns {object} The stored task.
 */
function createTaskFlow(body, repo) {
  const data = validateCreate(body);
  const xp = xpForPowerLevel(data.powerLevel);
  return repo.create({ ...data, xp });
}

// ---------------------------------------------------------------------------
// 1. XP calculation logic
// ---------------------------------------------------------------------------
describe('XP calculation (models/task.xpForPowerLevel)', () => {
  test('returns the configured XP for every valid power level', () => {
    assert.equal(xpForPowerLevel(1), 10);
    assert.equal(xpForPowerLevel(2), 25);
    assert.equal(xpForPowerLevel(3), 50);
    assert.equal(xpForPowerLevel(4), 100);
    assert.equal(xpForPowerLevel(5), 200);
  });

  test('matches the XP_BY_POWER_LEVEL table for the full valid range', () => {
    for (let level = MIN_POWER_LEVEL; level <= MAX_POWER_LEVEL; level += 1) {
      assert.equal(xpForPowerLevel(level), XP_BY_POWER_LEVEL[level]);
    }
  });

  test('higher power levels are worth strictly more XP', () => {
    for (let level = MIN_POWER_LEVEL; level < MAX_POWER_LEVEL; level += 1) {
      assert.ok(
        xpForPowerLevel(level + 1) > xpForPowerLevel(level),
        `xp(${level + 1}) should exceed xp(${level})`,
      );
    }
  });

  test('returns 0 for out-of-range / invalid power levels', () => {
    assert.equal(xpForPowerLevel(0), 0);
    assert.equal(xpForPowerLevel(6), 0);
    assert.equal(xpForPowerLevel(-1), 0);
    assert.equal(xpForPowerLevel(undefined), 0);
    assert.equal(xpForPowerLevel(null), 0);
  });

  test('resolves a numeric-string power level (JS object keys are strings)', () => {
    // Documents lenient model behavior: XP_BY_POWER_LEVEL['3'] === XP_BY_POWER_LEVEL[3].
    // The validator still rejects string powerLevels at the boundary, so this
    // only matters if a caller reaches the model directly.
    assert.equal(xpForPowerLevel('3'), 50);
  });
});

// ---------------------------------------------------------------------------
// 2. POST /tasks — create a task with a power level (service + validator)
// ---------------------------------------------------------------------------
describe('POST /tasks flow — create task with power level', () => {
  let repo;

  beforeEach(() => {
    repo = new TaskStore();
  });

  test('creates a task and awards XP matching its power level', () => {
    const created = createTaskFlow(
      { title: 'Defeat the boss', powerLevel: 5 },
      repo,
    );

    assert.ok(created.id, 'should assign an id');
    assert.equal(created.title, 'Defeat the boss');
    assert.equal(created.powerLevel, 5);
    assert.equal(created.xp, 200, 'XP should match power level 5');
    assert.equal(created.status, 'pending', 'defaults to pending');
    assert.equal(created.completedAt, null);
    assert.ok(created.createdAt, 'should stamp createdAt');
  });

  test('persists the created task so it is retrievable', () => {
    const created = createTaskFlow(
      { title: 'Grind XP', powerLevel: 2 },
      repo,
    );
    const fetched = repo.findById(created.id);
    assert.deepEqual(fetched, created);
    assert.equal(fetched.xp, 25);
  });

  test('trims title and applies default empty description', () => {
    const created = createTaskFlow(
      { title: '  Whitespace quest  ', powerLevel: 1 },
      repo,
    );
    assert.equal(created.title, 'Whitespace quest');
    assert.equal(created.description, '');
  });

  test('accepts the boundary power levels 1 and 5', () => {
    const low = createTaskFlow({ title: 'Easy', powerLevel: MIN_POWER_LEVEL }, repo);
    const high = createTaskFlow({ title: 'Hard', powerLevel: MAX_POWER_LEVEL }, repo);
    assert.equal(low.xp, 10);
    assert.equal(high.xp, 200);
  });
});

// ---------------------------------------------------------------------------
// 3. GET /tasks — return the task list (service layer)
// ---------------------------------------------------------------------------
describe('GET /tasks flow — list tasks', () => {
  let repo;

  beforeEach(() => {
    repo = new TaskStore();
  });

  test('returns an empty array when no tasks exist', () => {
    assert.deepEqual(repo.findAll(), []);
  });

  test('returns all created tasks', () => {
    createTaskFlow({ title: 'Task A', powerLevel: 1 }, repo);
    createTaskFlow({ title: 'Task B', powerLevel: 3 }, repo);
    createTaskFlow({ title: 'Task C', powerLevel: 5 }, repo);

    const list = repo.findAll();
    assert.equal(list.length, 3);
    assert.deepEqual(
      list.map((t) => t.title).sort(),
      ['Task A', 'Task B', 'Task C'],
    );
  });

  test('returns copies, so mutating the result does not corrupt the store', () => {
    const created = createTaskFlow({ title: 'Immutable', powerLevel: 2 }, repo);
    const list = repo.findAll();
    list[0].title = 'HACKED';
    list[0].xp = 99999;

    const fresh = repo.findById(created.id);
    assert.equal(fresh.title, 'Immutable');
    assert.equal(fresh.xp, 25);
  });
});

// ---------------------------------------------------------------------------
// 4. Error handling for invalid input
// ---------------------------------------------------------------------------
describe('Error handling — invalid input', () => {
  let repo;

  beforeEach(() => {
    repo = new TaskStore();
  });

  test('rejects a missing title with a 400 ValidationError', () => {
    assert.throws(
      () => validateCreate({ powerLevel: 3 }),
      (err) => {
        assert.ok(err instanceof ValidationError);
        assert.equal(err.statusCode, 400);
        assert.ok(err.details.title, 'details should flag the title');
        return true;
      },
    );
  });

  test('rejects an empty/whitespace-only title', () => {
    assert.throws(() => validateCreate({ title: '   ', powerLevel: 1 }), ValidationError);
  });

  test('rejects a power level above the valid range', () => {
    assert.throws(
      () => validateCreate({ title: 'Too strong', powerLevel: 10 }),
      (err) => {
        assert.ok(err instanceof ValidationError);
        assert.match(err.details.powerLevel, /between 1 and 5/);
        return true;
      },
    );
  });

  test('rejects a non-integer / zero / negative power level', () => {
    assert.throws(() => validateCreate({ title: 'X', powerLevel: 0 }), ValidationError);
    assert.throws(() => validateCreate({ title: 'X', powerLevel: -2 }), ValidationError);
    assert.throws(() => validateCreate({ title: 'X', powerLevel: 2.5 }), ValidationError);
    assert.throws(() => validateCreate({ title: 'X', powerLevel: '3' }), ValidationError);
  });

  test('rejects an invalid status value', () => {
    assert.throws(
      () => validateCreate({ title: 'X', powerLevel: 1, status: 'done' }),
      (err) => {
        assert.ok(err instanceof ValidationError);
        assert.ok(err.details.status);
        return true;
      },
    );
  });

  test('reports multiple field errors at once', () => {
    assert.throws(
      () => validateCreate({ powerLevel: 99, status: 'nope' }),
      (err) => {
        assert.ok(err.details.title);
        assert.ok(err.details.powerLevel);
        assert.ok(err.details.status);
        return true;
      },
    );
  });

  test('handles a null / non-object body without crashing', () => {
    assert.throws(() => validateCreate(null), ValidationError);
    assert.throws(() => validateCreate(undefined), ValidationError);
    assert.throws(() => validateCreate('not an object'), ValidationError);
  });

  test('update rejects an empty change set', () => {
    assert.throws(() => validateUpdate({}), ValidationError);
  });

  test('update rejects an invalid field but accepts a valid partial change', () => {
    assert.throws(() => validateUpdate({ powerLevel: 42 }), ValidationError);
    assert.deepEqual(validateUpdate({ status: 'completed' }), { status: 'completed' });
  });

  test('NotFoundError carries a 404 status for missing-resource cases', () => {
    // A GET /tasks/:id controller returns null from the store -> throws 404.
    assert.equal(repo.findById('does-not-exist'), null);
    const err = new NotFoundError('Task not found');
    assert.ok(err instanceof AppError);
    assert.equal(err.statusCode, 404);
    assert.equal(err.isOperational, true);
  });
});

// ---------------------------------------------------------------------------
// Full CRUD round-trip on the store (backs the REST endpoints)
// ---------------------------------------------------------------------------
describe('CRUD round-trip (services/taskStore)', () => {
  let repo;

  beforeEach(() => {
    repo = new TaskStore();
  });

  test('create -> read -> update -> delete', () => {
    const created = createTaskFlow({ title: 'Lifecycle', powerLevel: 4 }, repo);
    assert.equal(created.xp, 100);

    // read
    assert.deepEqual(repo.findById(created.id), created);

    // update: complete the task and bump its power level (+ recomputed XP)
    const updated = repo.update(created.id, {
      status: 'completed',
      powerLevel: 5,
      xp: xpForPowerLevel(5),
      completedAt: new Date().toISOString(),
    });
    assert.equal(updated.status, 'completed');
    assert.equal(updated.xp, 200);
    assert.equal(updated.id, created.id, 'id is preserved across update');
    assert.equal(updated.createdAt, created.createdAt, 'createdAt is preserved');

    // delete
    assert.equal(repo.delete(created.id), true);
    assert.equal(repo.findById(created.id), null);
    assert.equal(repo.delete(created.id), false, 'second delete is a no-op');
  });
});

// ---------------------------------------------------------------------------
// HTTP integration tests — drive backend-dev's Express app end-to-end
// ---------------------------------------------------------------------------
describe('HTTP endpoints (Express app)', () => {
  // The service uses a singleton store, so start each test from a clean slate.
  let server;
  let baseUrl;

  // Boot one app on an ephemeral port for the whole suite.
  const app = createApp();
  server = app.listen(0);
  const { port } = server.address();
  baseUrl = `http://127.0.0.1:${port}`;

  after(() => server.close());

  beforeEach(() => store.clear());

  test('GET /tasks returns an empty list initially', async () => {
    const res = await fetch(`${baseUrl}/tasks`);
    assert.equal(res.status, 200);
    const body = await res.json();
    assert.deepEqual(body, { data: [], count: 0 });
  });

  test('POST /tasks creates a task with the correct XP and returns 201', async () => {
    const res = await fetch(`${baseUrl}/tasks`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ title: 'Slay the dragon', powerLevel: 4 }),
    });
    assert.equal(res.status, 201);
    const body = await res.json();
    assert.equal(body.data.title, 'Slay the dragon');
    assert.equal(body.data.powerLevel, 4);
    assert.equal(body.data.xp, 100, 'power level 4 -> 100 XP');
    assert.equal(body.data.status, 'pending');
    assert.ok(body.data.id);
  });

  test('POST then GET /tasks reflects the created task in the list', async () => {
    await fetch(`${baseUrl}/tasks`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ title: 'First', powerLevel: 1 }),
    });
    const res = await fetch(`${baseUrl}/tasks`);
    const body = await res.json();
    assert.equal(body.count, 1);
    assert.equal(body.data[0].title, 'First');
    assert.equal(body.data[0].xp, 10);
  });

  test('POST /tasks with an invalid power level returns 400 with details', async () => {
    const res = await fetch(`${baseUrl}/tasks`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ title: 'Overpowered', powerLevel: 10 }),
    });
    assert.equal(res.status, 400);
    const body = await res.json();
    assert.equal(body.error.status, 400);
    assert.ok(body.error.details.powerLevel, 'should report the bad field');
  });

  test('POST /tasks with a missing title returns 400', async () => {
    const res = await fetch(`${baseUrl}/tasks`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ powerLevel: 2 }),
    });
    assert.equal(res.status, 400);
    const body = await res.json();
    assert.ok(body.error.details.title);
  });

  test('GET /tasks/:id for a missing task returns 404', async () => {
    const res = await fetch(`${baseUrl}/tasks/nonexistent-id`);
    assert.equal(res.status, 404);
    const body = await res.json();
    assert.equal(body.error.status, 404);
  });

  test('PUT /tasks/:id updates status, recomputes XP, and stamps completedAt', async () => {
    const createRes = await fetch(`${baseUrl}/tasks`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ title: 'Quest', powerLevel: 1 }),
    });
    const { data: created } = await createRes.json();

    const putRes = await fetch(`${baseUrl}/tasks/${created.id}`, {
      method: 'PUT',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ status: 'completed', powerLevel: 5 }),
    });
    assert.equal(putRes.status, 200);
    const { data: updated } = await putRes.json();
    assert.equal(updated.status, 'completed');
    assert.equal(updated.xp, 200, 'XP recomputed for new power level');
    assert.ok(updated.completedAt, 'completedAt stamped on completion');
  });

  test('DELETE /tasks/:id removes the task (204), then 404 on re-delete', async () => {
    const createRes = await fetch(`${baseUrl}/tasks`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ title: 'Disposable', powerLevel: 3 }),
    });
    const { data: created } = await createRes.json();

    const del1 = await fetch(`${baseUrl}/tasks/${created.id}`, { method: 'DELETE' });
    assert.equal(del1.status, 204);

    const del2 = await fetch(`${baseUrl}/tasks/${created.id}`, { method: 'DELETE' });
    assert.equal(del2.status, 404);
  });

  test('unknown route returns a 404 error envelope', async () => {
    const res = await fetch(`${baseUrl}/not-a-route`);
    assert.equal(res.status, 404);
    const body = await res.json();
    assert.match(body.error.message, /Route not found/);
  });
});
