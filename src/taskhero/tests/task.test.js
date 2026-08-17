'use strict';

const request = require('supertest');
const createApp = require('../app');
const store = require('../services/taskStore');
const { xpForPowerLevel, MIN_POWER_LEVEL, MAX_POWER_LEVEL, XP_BASE } = require('../models/task');

/**
 * Unit tests for TaskHero REST API.
 *
 * These tests exercise the HTTP layer (via supertest) and the XP formula.
 * The store is a shared singleton, so each test clears it first to stay
 * isolated.
 */

const app = createApp();

beforeEach(() => {
  store.clear();
});

describe('XP formula', () => {
  test('XP is linear: xp = 10 × powerLevel', () => {
    for (let p = MIN_POWER_LEVEL; p <= MAX_POWER_LEVEL; p++) {
      expect(xpForPowerLevel(p)).toBe(XP_BASE * p);
    }
  });

  test('out-of-range powerLevel yields 0 XP', () => {
    expect(xpForPowerLevel(0)).toBe(0);
    expect(xpForPowerLevel(11)).toBe(0);
  });
});

describe('POST /tasks', () => {
  test('creates a task with valid power level (1-10)', async () => {
    const res = await request(app)
      .post('/tasks')
      .send({ title: 'Write docs', description: 'Update README', powerLevel: 7 });

    expect(res.status).toBe(201);
    expect(res.body.data).toMatchObject({
      title: 'Write docs',
      description: 'Update README',
      powerLevel: 7,
      status: 'pending',
    });
    // XP = 10 × 7 = 70
    expect(res.body.data.xp).toBe(70);
    expect(res.body.data.id).toBeDefined();
  });

  test('rejects powerLevel out of range (e.g. 11)', async () => {
    const res = await request(app)
      .post('/tasks')
      .send({ title: 'Too strong', powerLevel: 11 });

    expect(res.status).toBe(400);
    expect(res.body.error).toBeDefined();
  });

  test('rejects missing title', async () => {
    const res = await request(app)
      .post('/tasks')
      .send({ powerLevel: 3 });

    expect(res.status).toBe(400);
    expect(res.body.error).toMatch(/title/i);
  });
});

describe('GET /tasks', () => {
  test('returns an empty list initially', async () => {
    const res = await request(app).get('/tasks');
    expect(res.status).toBe(200);
    expect(res.body.data).toEqual([]);
    expect(res.body.count).toBe(0);
  });

  test('returns created tasks', async () => {
    await request(app).post('/tasks').send({ title: 'A', powerLevel: 2 });
    await request(app).post('/tasks').send({ title: 'B', powerLevel: 5 });

    const res = await request(app).get('/tasks');
    expect(res.status).toBe(200);
    expect(res.body.count).toBe(2);
    expect(res.body.data.map((t) => t.title)).toEqual(['A', 'B']);
  });
});

describe('XP awarded on completion', () => {
  test('completing a task keeps its XP (10 × powerLevel)', async () => {
    const created = await request(app)
      .post('/tasks')
      .send({ title: 'Defeat boss', powerLevel: 10 });
    const id = created.body.data.id;

    const updated = await request(app).put(`/tasks/${id}`).send({ status: 'completed' });

    expect(updated.status).toBe(200);
    expect(updated.body.data.status).toBe('completed');
    expect(updated.body.data.xp).toBe(100); // 10 × 10
    expect(updated.body.data.completedAt).not.toBeNull();
  });
});

describe('Error handling', () => {
  test('GET /tasks/:id returns 404 for unknown id', async () => {
    const res = await request(app).get('/tasks/nonexistent');
    expect(res.status).toBe(404);
    expect(res.body.error).toBeDefined();
  });
});
