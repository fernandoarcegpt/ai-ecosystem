'use strict';

const createApp = require('./app');

const PORT = process.env.PORT || 3000;

const app = createApp();

const server = app.listen(PORT, () => {
  console.log(`[TaskHero] Server listening on port ${PORT}`);
});

// Graceful shutdown on termination signals.
function shutdown(signal) {
  console.log(`[TaskHero] ${signal} received, shutting down.`);
  server.close(() => process.exit(0));
}

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));

module.exports = server;
