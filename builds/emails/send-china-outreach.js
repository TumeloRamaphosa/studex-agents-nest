const https = require('https');

const API_KEY = 'am_us_24fcb06c6b1babba88c56d49b1a83fc33f1b8acf153acf3ef905136f335e7502';
const FROM = 'robusca@agent.studexmeat.com';

function sendEmail(to, subject, body) {
  const payload = JSON.stringify({ from: FROM, to, subject, body });
  const options = {
    hostname: 'api.agentmail.to',
    path: '/v0/send',
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(payload)
    }
  };
  return new Promise((resolve, reject) => {
    const req = https.request(options, res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({ status: res.statusCode, body: data }));
    });
    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

const luckinEmail = `Dear Luckin Coffee Procurement Team,

I hope this message finds you well. My name is Tumelo Ramaphosa, founder of Studex Meat, a South African premium food and beverage company now expanding into green coffee exports from Rwanda.

We're writing to you because a rare first-mover window opens July 20 — South African green coffee gains access to the Chinese market under the SA-China bilateral agricultural protocol. We are ready to ship.

We source Rwanda A1 and A2 grade — fully washed and naturally processed — with cup profiles that suit medium-to-dark roast profiles at scale for chains like yours.

What we offer:
- Rwanda Grade A1 — Washed: jasmine, stone fruit, clean finish
- Rwanda Grade A2 — Natural: blueberry, dark chocolate, full body
- PROWTC certified + Rainforest Alliance certified
- FOB Kigali from USD 4.80/kg | Minimum order: 60kg bags
- Full logistics from Kigali to your roastery included

Why South Africa as your import partner:
- Supply chain resilience — no Red Sea disruption, routing via Durban
- CIIE November 2026 in Shanghai — we'll be there, happy to meet in person
- Sample orders can be dispatched immediately

Would you be open to a 20-minute call this week? Happy to send 1kg samples to your roastery for a no-obligation cupping evaluation.

Warm regards,
Tumelo Ramaphosa
Founder & CEO
Studex Meat
tumelo@studexmeat.com | coffee@studexmeat.com
studexmeat.com`;

const jdEmail = `Dear JD.com Fresh / International Trade Team,

I hope this message finds you well. My name is Tumelo Ramaphosa, founder of Studex Meat, a South African premium food and beverage company now expanding into green coffee exports from Rwanda to China.

A first-mover window opens July 20 — South African green coffee imports into China under the SA-China bilateral agricultural protocol. We are ready to be your supplier.

We source Rwanda A1 and A2 grade — fully washed and naturally processed — at price points that compete with Brazilian commodity coffee while offering the provenance and certification story Chinese consumers increasingly demand.

Product offering:
- Rwanda Grade A1 — Washed: jasmine, stone fruit, clean finish | FOB Kigali USD 4.80/kg
- Rwanda Grade A2 — Natural: blueberry, dark chocolate, full body | FOB Kigali USD 5.20/kg
- PROWTC certified + Rainforest Alliance certified | Minimum order: 60kg bags
- Full logistics from Kigali to your warehouse included

Why JD.com + Studex is a strong fit:
- Rwanda single-origin aligns with JD.com's premium domestic positioning
- South African import channel = supply chain resilience vs Red Sea routing
- We handle all customs, clearance, and freight — you receive the coffee ready to roast

We are applying for the CIIE November 2026 booth in Shanghai — if JD.com sources green coffee, we would welcome the opportunity to meet there.

Happy to arrange a call this week or next. Samples can be dispatched immediately.

Warm regards,
Tumelo Ramaphosa
Founder & CEO
Studex Meat
tumelo@studexmeat.com | coffee@studexmeat.com
studexmeat.com`;

async function main() {
  console.log('Sending to Luckin Coffee...');
  const r1 = await sendEmail(
    'procurement@luckincoffee.cn',
    'South African Coffee — Rwanda A1 Grade, Wildlife Verified, PROWTC Certified',
    luckinEmail
  );
  console.log('Luckin result:', r1.status, r1.body);

  console.log('Sending to JD.com...');
  const r2 = await sendEmail(
    'jd-food-import@jd.com',
    'Rwanda A1 Coffee — South African Import Partner, PROWTC Certified, FOB Kigali USD 4.80/kg',
    jdEmail
  );
  console.log('JD.com result:', r2.status, r2.body);
}

main().catch(console.error);
