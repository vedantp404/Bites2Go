import test from 'node:test';
import assert from 'node:assert/strict';
import { theme } from '../src/theme/tokens.ts';
function luminance(hex) {
  const rgb = hex
    .slice(1)
    .match(/../g)
    .map((x) => parseInt(x, 16) / 255)
    .map((x) => (x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4));
  return rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722;
}
test('all screen text pairs meet AA normal-text contrast', () => {
  const c = theme.colors;
  for (const [fg, bg] of [
    [c.text, c.background],
    [c.muted, c.background],
    [c.text, c.surface],
    [c.muted, c.surface],
    [c.surface, c.primary],
    [c.primary, c.accent],
    [c.primary, c.background],
  ]) {
    const values = [luminance(fg), luminance(bg)].sort((a, b) => b - a);
    assert.ok((values[0] + 0.05) / (values[1] + 0.05) >= 4.5, `${fg} on ${bg}`);
  }
});
