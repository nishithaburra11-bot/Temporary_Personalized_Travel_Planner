const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const frontend = path.join(__dirname, '../frontend');

function calendarAt(now) {
    class Element {
        constructor() { this.value = ''; this.hidden = true; this.children = []; this.attrs = {}; this.events = {}; }
        addEventListener(name, fn) { this.events[name] = fn; }
        setAttribute(name, value) { this.attrs[name] = value; }
        append(child) { this.children.push(child); }
        replaceChildren() { this.children = []; }
        focus() {}
        dispatchEvent() {}
        querySelector(query) {
            return this.children.find(e => query.includes('aria-pressed') ? e.attrs['aria-pressed'] === 'true' : e.type === 'button' && !e.disabled);
        }
    }
    const elements = {};
    const get = id => elements[id] ||= new Element();
    class Clock extends Date { constructor(...args) { super(...(args.length ? args : [now])); } }
    const context = { Date: Clock, Event: class {}, window: {}, localStorage: { removeItem() {} }, document: { getElementById: get, createElement: () => new Element(), addEventListener() {} } };
    vm.runInNewContext(fs.readFileSync(path.join(frontend, 'travel-date-picker.js'), 'utf8'), context);
    return { get, api: context.window.travelDatePicker, click: id => get(id).events.click() };
}

test('past dates and earlier months are blocked, today and future dates are selectable', () => {
    const c = calendarAt('2026-11-16T12:00:00');
    c.api.setValue('2026-11-15');
    assert.equal(c.get('startDate').value, '');
    c.click('startDate');
    assert.equal(c.get('previousMonth').disabled, true);
    const buttons = c.get('calendarDays').children.filter(e => e.type === 'button');
    assert.equal(buttons.length, 30);
    assert.equal(buttons.filter(e => e.disabled).length, 15);
    buttons[15].events.click();
    assert.equal(c.get('startDate').value, '2026-11-16');
    c.click('startDate');
    c.click('nextMonth');
    assert.equal(c.get('previousMonth').disabled, false);
    c.click('previousMonth');
    c.click('previousMonth');
    assert.equal(c.get('previousMonth').disabled, true);
    c.click('calendarClear');
    assert.equal(c.get('startDate').value, '');
});

test('year rollover and leap day remain available without accepting invalid dates', () => {
    const c = calendarAt('2027-12-31T12:00:00');
    c.click('startDate');
    c.click('nextMonth');
    assert.match(c.get('calendarMonth').textContent, /2028/);
    c.click('nextMonth');
    assert.equal(c.get('calendarDays').children.filter(e => e.type === 'button').length, 29);
    c.api.setValue('2028-02-29');
    assert.equal(c.get('startDate').value, '2028-02-29');
    c.api.setValue('2028-02-30');
    assert.equal(c.get('startDate').value, '');
});

test('plan separates three summary stats and maps the full budget including entry fees', () => {
    const html = fs.readFileSync(path.join(frontend, 'plan.html'), 'utf8');
    const body = html.split('function renderResult(data) {')[1].split('// 3. Days')[0];
    const elements = {};
    vm.runInNewContext(body, { data: { itinerary_by_day: [{ stops: [{}, {}] }], total_distance_km: 12, cost_breakdown: { fuel: { amount: 100 }, food: { amount: 200 }, accommodation: { amount: 300 }, entry_fees: { amount: 40 }, total: 640 } }, document: { getElementById: id => elements[id] ||= {} } });
    assert.equal((elements.summaryCard.innerHTML.match(/class="summary-stat"/g) || []).length, 3);
    assert.doesNotMatch(elements.summaryCard.innerHTML, /Estimated Spend/);
    for (const amount of [100, 200, 300, 640, 40]) assert.ok(elements.spendCard.innerHTML.includes(`₹${amount}`));
});

test('all inline page scripts parse', () => {
    for (const file of ['plan.html', 'preferences.html']) {
        const html = fs.readFileSync(path.join(frontend, file), 'utf8');
        for (const match of html.matchAll(/<script>([\s\S]*?)<\/script>/g)) new vm.Script(match[1]);
    }
});
