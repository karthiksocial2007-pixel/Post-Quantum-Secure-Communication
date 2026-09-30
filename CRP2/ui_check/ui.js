const { JSDOM } = require('jsdom');
const BASE = 'http://127.0.0.1:5000';
let failed = 0;
const check = (name, cond) => { if(!cond) failed++; console.log((cond ? 'PASS ' : 'FAIL ') + name); };
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function load() {
  const dom = await JSDOM.fromURL(BASE + '/', { runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true,
    beforeParse(w) {
      w.fetch = (u, o) => fetch(new URL(u, BASE), o);
      w.Element.prototype.scrollIntoView = function(){};
      w.alert = m => { throw new Error('alert: ' + m); };
    }});
  await new Promise(r => dom.window.addEventListener('load', r));
  await sleep(400);
  return dom.window;
}
const txt = (w,id) => w.document.getElementById(id).textContent.replace(/\s+/g,' ').trim();
const cls = (w,id) => w.document.getElementById(id).className;
const until = async (fn, ms=8000) => { const t=Date.now(); while(Date.now()-t<ms){ if(fn()) return true; await sleep(100);} return false; };

(async () => {
  let w = await load();
  const $ = id => w.document.getElementById(id);
  await w.resetSession(); await sleep(500);

  console.log('--- initial state ---');
  check('status shows System Secure', txt(w,'systemStatus') === 'System Secure');
  check('relay chip empty', txt(w,'relayChip') === 'Relay: empty');
  check('step 1 active only', cls(w,'step-send').includes('active') && !cls(w,'step-attack').includes('active'));
  check('packet section hidden', $('messageResult').classList.contains('hidden'));
  check('copy buttons added (3)', w.document.querySelectorAll('.copy-button').length === 3);

  console.log('--- send ---');
  $('sender').value = 'Bob'; $('message').value = 'hello alice';
  await w.sendMessage();
  check('packet section visible', !$('messageResult').classList.contains('hidden'));
  check('relay chip shows 1 in transit', txt(w,'relayChip').includes('1 message'));
  check('integrity chip unmodified', txt(w,'integrityChip') === 'Packet unmodified');
  check('Bob shows sent, Alice waiting', txt(w,'bobStatus').includes('sent') && txt(w,'aliceStatus').includes('waiting'));
  check('receive button enabled', !$('receiveButton').disabled);
  check('steps: send done, attack+receive active', cls(w,'step-send').includes('done') && cls(w,'step-attack').includes('active') && cls(w,'step-receive').includes('active'));

  console.log('--- attack 01 then inline receive ---');
  await w.runAttack('tampering');
  check('attack result says DETECTED', txt(w,'result-tampering').includes('ATTACK DETECTED'));
  check('attack shows verifier detail', txt(w,'result-tampering').includes('Verifier said'));
  check('inline Receive button appears', !!w.document.querySelector('#result-tampering .inline-receive'));
  check('integrity chip warns modified', txt(w,'integrityChip').includes('Modified in transit (Ciphertext Tampering)'));
  check('packet chip warns modified', txt(w,'packetState').includes('Modified'));
  check('attack step done', cls(w,'step-attack').includes('done'));
  w.document.querySelector('#result-tampering .inline-receive').click();
  check('inline verdict rejected', await until(() => /Rejected/.test(txt(w,'receiveResult'))) );
  await sleep(300);
  check('main receive box shows rejected + reason', txt(w,'receiveResult').includes('AES-256-GCM authentication failed'));
  check('inline verdict shown', txt(w,'result-tampering').includes('Message Rejected'));
  check('inline button removed', !w.document.querySelector('#result-tampering .inline-receive'));
  check('Alice shows Rejected', txt(w,'aliceStatus').includes('Rejected'));
  check('integrity chip rejected', txt(w,'integrityChip').includes('Rejected by Alice'));
  check('receive button disabled (relay empty)', $('receiveButton').disabled);
  check('relay empty again', txt(w,'relayChip') === 'Relay: empty');

  console.log('--- attack 02 via normal Receive ---');
  $('sender').value = 'Alice'; $('message').value = 'second';
  await w.sendMessage();
  check('outcome cleared on new send', !txt(w,'integrityChip').includes('Rejected'));
  await w.runAttack('signature');
  check('signature attack detected', txt(w,'result-signature').includes('ATTACK DETECTED'));
  await w.receiveMessage();
  check('Bob rejected: ML-DSA', txt(w,'receiveResult').includes('Invalid ML-DSA signature'));

  console.log('--- passive attacks + success path ---');
  $('message').value = 'third'; await w.sendMessage();
  await w.runAttack('wrong-key'); await w.runAttack('interception');
  check('wrong-key detected', txt(w,'result-wrong-key').includes('ATTACK DETECTED'));
  check('interception protected', txt(w,'result-interception').includes('INTERCEPTION PROTECTED'));
  check('no inline receive on passive attacks', !w.document.querySelector('#result-wrong-key .inline-receive'));
  check('still unmodified', txt(w,'integrityChip') === 'Packet unmodified');
  await w.receiveMessage();
  check('receive verified', txt(w,'receiveResult').includes('Message Successfully Verified') && txt(w,'receiveResult').includes('third'));
  check('Bob shows Verified', txt(w,'bobStatus').includes('Verified'));
  check('integrity chip delivered', txt(w,'integrityChip').includes('Delivered and verified'));

  console.log('--- replay ---');
  await w.runAttack('replay');
  check('replay detected', txt(w,'result-replay').includes('ATTACK DETECTED'));
  check('replay does not disturb verified state', txt(w,'integrityChip').includes('Delivered'));

  console.log('--- receive with empty relay (button disabled; direct call) ---');
  await w.receiveMessage();
  check('graceful message, no stale rejection', txt(w,'receiveResult').includes('No message is waiting'));

  console.log('--- validation + log ---');
  $('message').value = '   '; await w.sendMessage();
  check('empty message blocked', txt(w,'messageStatus') === 'Enter a message');
  const n = w.document.querySelectorAll('#logList li').length;
  check('activity log has entries ('+n+')', n >= 10);
  w.toggleLog(); check('log opens', !$('logPanel').classList.contains('hidden'));
  w.clearLog(); check('log clears', txt(w,'logCount') === '0');

  console.log('--- reload keeps server relay ---');
  $('message').value = 'pending msg'; await w.sendMessage();
  const w2 = await load();
  check('reload shows waiting message', !w2.document.getElementById('messageResult').classList.contains('hidden') && w2.document.getElementById('relayChip').textContent.includes('1 message'));
  await w2.resetSession(); await sleep(300);

  console.log(failed ? `\n${failed} FAILED` : '\nALL UI CHECKS PASSED');
  process.exit(failed ? 1 : 0);
})().catch(e => { console.error('ERROR', e); process.exit(2); });
