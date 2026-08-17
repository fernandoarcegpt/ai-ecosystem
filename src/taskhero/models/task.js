'use strict';

/**
 * Task domain model for TaskHero.
 *
 * A task is a gamified unit of work. Its `powerLevel` represents difficulty
 * (1-10) and determines how much XP is awarded when the task is completed.
 * The XP formula is linear: XP = 10 × powerLevel.
 */

const VALID_STATUSES = Object.freeze(['pending', 'in-progress', 'completed']);
const MIN_POWER_LEVEL = 1;
const MAX_POWER_LEVEL = 10;
const XP_BASE = 10;

/**
 * Compute the XP reward for a given power level.
 * Formula: XP = XP_BASE × powerLevel (linear scaling)
 * @param {number} powerLevel
 * @returns {number}
 */
function xpForPowerLevel(powerLevel) {
  if (powerLevel < MIN_POWER_LEVEL || powerLevel > MAX_POWER_LEVEL) return 0;
  return XP_BASE * powerLevel;
}

module.exports = {
  VALID_STATUSES,
  MIN_POWER_LEVEL,
  MAX_POWER_LEVEL,
  XP_BASE,
  xpForPowerLevel,
};
