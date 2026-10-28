import { useState } from 'react';

type OutreachStatus = 'draft' | 'sent' | 'replied' | 'meeting_booked' | 'no_response';
type OutreachChannel = 'email' | 'linkedin' | 'ciie_portal' | 'phone';

interface OutreachEntry {
  id: string;
  buyer: string;
  company: string;
  country: string;
  contact: string;
  subject: string;
  template: string;
  status: OutreachStatus;
  channel: OutreachChannel;
  sentDate: string | null;
  lastFollowUp: string | null;
  notes: string;
  priority: 'high' | 'medium' | 'low';
  ciieMeeting: boolean;
  responseNotes: string;
}

const initialOutreach: OutreachEntry[] = [
  // ─── CHINA TARGETS ───────────────────────────────────────────────────────────
  {
    id: 'o1',
    buyer: 'Luckin Coffee Procurement',
    company: 'Luckin Coffee',
    country: '🇨🇳 China',
    contact: 'buyer@luckincoffee.com',
    subject: 'Rwanda A1 Specialty Coffee — CIIE 2026 Meeting Request',
    template: `Dear Luckin Coffee Procurement Team,

I am reaching out from Studex Meat (South Africa), representing Rwandan-origin specialty coffee through Full documentation: phytosanitary certificates, COA, fumigation records.

With Rwanda now China's #1 African coffee supplier, and the SA-China bilateral protocol active since July 20, we see a significant opportunity for Luckin to introduce a Rwanda specialty line — distinct from your existing Brazil supply.

Offer: Rwanda A1 Washed (jasmine/stone fruit) — FOB $4,200-4,800/MT (USD 4.20-4.80/kg). 20 MT container lots; 5-10 kg samples before bulk commitment. Full documentation: phytosanitary certificates, COA, fumigation records.

I will be attending CIIE 2026 (Shanghai, Nov 5-10) and would welcome the opportunity to meet. I have pre-registered as a buyer and can schedule time in advance.

Would your team be available for a 20-minute meeting at the expo?

Best regards,
Tumelo Ramaphosa
Studex Meat`,
    status: 'draft',
    channel: 'email',
    sentDate: null,
    lastFollowUp: null,
    notes: 'Luckin is locked into Brazil deal through 2029 — specialty line only. CIIE is the entry point.',
    priority: 'high',
    ciieMeeting: true,
    responseNotes: '',
  },
  // ─── UAE TARGETS (from tonight's research — white space, no Rwanda competition) ─
  {
    id: 'ouae1',
    buyer: 'Smart Square Goods Wholesalers — Green Coffee Division',
    company: 'Smart Square Goods Wholesalers LLC',
    country: '🇦🇪 UAE',
    contact: 'info@smartsquare.ae',
    subject: 'Rwanda A1/A2 Specialty Green Coffee — UAE Import Partnership',
    template: `Dear Smart Square Green Coffee Team,

I am Tumelo Ramaphosa of Studex Meat, writing regarding Rwandan specialty green coffee for the UAE market.

Smart Square Goods Wholesalers holds 15% of UAE green coffee imports — an impressive market position. Rwanda is not currently in your origin mix, which represents a genuine white space opportunity.

Our offer:
• Rwanda A1 Washed — FOB $4,200-4,800/MT (USD 4.20-4.80/kg) (jasmine, stone fruit, clean finish)
• Rwanda A2 Natural — FOB $3,600-4,000/MT (USD 3.60-4.00/kg) (blueberry, chocolate)
• Full documentation: phytosanitary certificates, COA, fumigation records
• MOQ: 60kg trial; 1-5MT for ongoing supply

With the China zero-tariff agreement on African origins now active (July 2026), Rwanda is the fastest-growing African origin. UAE re-export to China corridor is active.

Would you be open to a sample evaluation? We can ship 60kg DDP to Dubai.

Best regards,
Tumelo Ramaphosa
Studex Meat`,
    status: 'draft',
    channel: 'email',
    sentDate: null,
    lastFollowUp: null,
    notes: 'Top UAE green coffee importer — 15% market share. Sourcing Brazil, Ethiopia, Vietnam. Rwanda is white space. Best entry via sample shipment.',
    priority: 'high',
    ciieMeeting: false,
    responseNotes: '',
  },
  {
    id: 'ouae2',
    buyer: 'Dhirani Foodstuff Co — Coffee Division',
    company: 'Dhirani Foodstuff Co L L C',
    country: '🇦🇪 UAE',
    contact: 'info@dhiranifoodstuff.ae',
    subject: 'Rwanda Specialty Coffee — UAE Leading Importer Opportunity',
    template: `Dear Dhirani Foodstuff Coffee Team,

I am Tumelo Ramaphosa of Studex Meat regarding Rwandan specialty green coffee — sourced Full documentation: phytosanitary certificates, COA, fumigation records.

Dhirani Foodstuff holds 18% market share in UAE green coffee imports. Rwanda-origin coffee is not currently in your portfolio — and given Rwanda is now China's #1 African supplier post the July 2026 zero-tariff expansion, now is the moment to establish this corridor.

Our offer:
• Rwanda A1 Washed — FOB $4,200-4,800/MT (USD 4.20-4.80/kg)
• Rwanda A2 Natural — FOB $3,600-4,000/MT (USD 3.60-4.00/kg)
• MOQ: 60kg trial samples DDP Dubai; 1-10MT ongoing contracts

We are also exhibiting at CIIE 2026 (Shanghai, Nov 5-10) and would welcome the chance to meet you there or in Dubai beforehand.

Best regards,
Tumelo Ramaphosa
Studex Meat`,
    status: 'draft',
    channel: 'email',
    sentDate: null,
    lastFollowUp: null,
    notes: 'UAE leading importer — 18% market share. Established trader, decisions take time. Best approach: sample shipment + CIIE meeting.',
    priority: 'high',
    ciieMeeting: false,
    responseNotes: '',
  },
  {
    id: 'ouae3',
    buyer: 'BMC Overseas Trading — Commodities Desk',
    company: 'BMC Overseas Trading FZE',
    country: '🇦🇪 UAE',
    contact: 'trade@bmc-overseas.ae',
    subject: 'Rwanda Green Coffee — African Origin Opportunity for UAE Re-Export',
    template: `Dear BMC Overseas Trading Commodities Team,

I am Tumelo Ramaphosa of Studex Meat, writing regarding Rwandan specialty green coffee for your African origin desk.

BMC Overseas Trading is active in global green bean trading — Rwanda is an underserved origin in your current book that commands a premium in the China + Middle East markets.

Key offer:
• Rwanda A1 Washed — FOB $4,200-4,800/MT (USD 4.20-4.80/kg), Full documentation: phytosanitary certificates, COA, fumigation records
• Rwanda A2 Natural — FOB $3,600-4,000/MT (USD 3.60-4.00/kg)
• Re-export to China via Dubai corridor — zero-tariff advantage since July 2026
• 60kg sample minimum; 1-20MT contracts available

Happy to ship samples DDP to Dubai for your cupping evaluation.

Best regards,
Tumelo Ramaphosa
Studex Meat`,
    status: 'draft',
    channel: 'email',
    sentDate: null,
    lastFollowUp: null,
    notes: 'Major green bean trader. Aggressive commercial buyer. Focus on price competitiveness + re-export story.',
    priority: 'medium',
    ciieMeeting: false,
    responseNotes: '',
  },
  {
    id: 'ouae4',
    buyer: 'Dubagro LLC — Coffee Desk',
    company: 'Dubagro LLC FZ',
    country: '🇦🇪 UAE',
    contact: 'info@dubagro.ae',
    subject: 'Rwanda A1 Specialty Green Coffee — Dubai Import Enquiry',
    template: `Dear Dubagro Coffee Team,

I am Tumelo Ramaphosa of Studex Meat writing regarding Rwandan specialty green coffee for UAE import.

Dubagro LLC is an established UAE food and beverage importer — Rwanda specialty coffee would complement your existing origin portfolio with a differentiated, PROWTC-certified African origin.

Offer:
• Rwanda A1 Washed — FOB $4,200-4,800/MT (USD 4.20-4.80/kg)
• Rwanda A2 Natural — FOB $3,600-4,000/MT (USD 3.60-4.00/kg)  
• Full documentation: phytosanitary certificates, COA, fumigation records
• Sample shipment: 60kg DDP Dubai

Given the China-Africa zero-tariff agreement (active July 2026), Dubai-based re-export to China buyers is a strong angle.

Best regards,
Tumelo Ramaphosa
Studex Meat`,
    status: 'draft',
    channel: 'email',
    sentDate: null,
    lastFollowUp: null,
    notes: 'Active importer in UAE. Smaller than Smart Square / Dhirani but more agile. Good for trial shipments.',
    priority: 'medium',
    ciieMeeting: false,
    responseNotes: '',
  },
  {
    id: 'ouae5',
    buyer: 'BonCafe Middle East — Procurement',
    company: 'BonCafe Middle East Co LLC',
    country: '🇦🇪 UAE',
    contact: 'procurement@boncafe.ae',
    subject: 'Rwanda Specialty Coffee — UAE Premium Roaster Partnership',
    template: `Dear BonCafe Middle East Procurement Team,

I am Tumelo Ramaphosa of Studex Meat writing regarding Rwandan specialty green coffee — Full documentation: phytosanitary certificates, COA, fumigation records.

BonCafe Middle East has 53 green coffee shipment records on file — you are the definitive specialty coffee house in the UAE. Rwanda-origin is a natural fit for your premium positioning.

Our offer:
• Rwanda A1 Washed — FOB $4,200-4,800/MT (USD 4.20-4.80/kg) (floral, citrus, clean)
• Rwanda A2 Natural — FOB $3,600-4,000/MT (USD 3.60-4.00/kg) (dark fruit, chocolate)
• 60kg minimum trial; 500kg–5MT ongoing
• Full documentation: phytosanitary certificates, COA, fumigation records

We are attending CIIE 2026 in Shanghai (Nov 5-10) — if you have buyers visiting the expo, we would welcome a meeting.

Best regards,
Tumelo Ramaphosa
Studex Meat`,
    status: 'draft',
    channel: 'email',
    sentDate: null,
    lastFollowUp: null,
    notes: 'Leading UAE specialty roaster — . Highest credibility target. Full documentation and traceable lots are the differentiator for their EU-facing business.',
    priority: 'high',
    ciieMeeting: false,
    responseNotes: '',
  },
  {
    id: 'ouae6',
    buyer: 'Coffee Planet Roastery — Green Bean Sourcing',
    company: 'Coffee Planet Roastery FZE',
    country: '🇦🇪 UAE',
    contact: 'green@coffeeplanet.ae',
    subject: 'Rwanda Single-Origin — Specialty Roaster Opportunity',
    template: `Dear Coffee Planet Roastery Sourcing Team,

I am Tumelo Ramaphosa of Studex Meat writing regarding Rwanda single-origin green coffee — a compelling new origin story for your specialty roasting portfolio.

Coffee Planet Roastery FZE is positioned as a specialty roaster — Rwanda A1 Washed (jasmine, stone fruit, Earl Grey notes) would be an excellent single-origin offering for your UAE customers.

Offer:
• Rwanda A1 Washed — FOB $4,200-4,800/MT (USD 4.20-4.80/kg), Full documentation: phytosanitary certificates, COA, fumigation records
• Rwanda A2 Natural — FOB $3,600-4,000/MT (USD 3.60-4.00/kg)
• 60kg sample minimum DDP Dubai
• Full traceability: farm level, washing station, export docs

We can also supply in 1kg, 2kg, 5kg retail-ready bags for your roastery customers if desired.

Best regards,
Tumelo Ramaphosa
Studex Meat`,
    status: 'draft',
    channel: 'email',
    sentDate: null,
    lastFollowUp: null,
    notes: 'Specialty roaster + importer. Good fit for differentiated single-origin story. Slightly smaller operation.',
    priority: 'medium',
    ciieMeeting: false,
    responseNotes: '',
  },
  {
    id: 'ouae7',
    buyer: 'Dubai Tea Trading Centre — Beverage Division',
    company: 'Dubai Tea Trading Centre',
    country: '🇦🇪 UAE',
    contact: 'info@dtc.ae',
    subject: 'Rwanda Coffee — Cross-Category Opportunity for Tea Importers',
    template: `Dear Dubai Tea Trading Centre Team,

I am Tumelo Ramaphosa of Studex Meat writing regarding a new beverage origin opportunity.

Dubai Tea Trading Centre has deep relationships across the UAE food and beverage trade. We are introducing Rwandan specialty green coffee — Full documentation: phytosanitary certificates, COA, fumigation records — as a cross-category opportunity for your existing buyer network.

Why Rwanda now:
• China-Africa zero-tariff agreement (July 2026) creates UAE→China re-export arbitrage
• Rwanda is China\'s #1 African coffee supplier — fastest growing corridor
• Full documentation: phytosanitary certificates, COA, fumigation records

Offer: Rwanda A1 Washed $4,200-4,800/MT FOB, A2 Natural $3,600-4,000/MT FOB. MOQ 20 MT.

Best regards,
Tumelo Ramaphosa
Studex Meat`,
    status: 'draft',
    channel: 'email',
    sentDate: null,
    lastFollowUp: null,
    notes: 'Cross-category beverage trader. May not have coffee buyer relationships yet — angle is introducing Rwanda as new category.',
    priority: 'low',
    ciieMeeting: false,
    responseNotes: '',
  },
  {
    id: 'ouae8',
    buyer: 'Agrivet Trading LLC — Food & Beverage Import',
    company: 'Agrivet Trading LLC',
    country: '🇦🇪 UAE',
    contact: 'info@agrivetz.com',
    subject: 'Rwanda Specialty Coffee — African Origin Desk',
    template: `Dear Agrivet Trading Food & Beverage Team,

I am Tumelo Ramaphosa of Studex Meat writing regarding Rwandan specialty green coffee — Full documentation: phytosanitary certificates, COA, fumigation records.

Agrivet Trading LLC imports food and beverage products across the UAE. Rwanda specialty coffee is an underserved origin in your market segment — our offer is:

• Rwanda A1 Washed — FOB $4,200-4,800/MT (USD 4.20-4.80/kg)
• Rwanda A2 Natural — FOB $3,600-4,000/MT (USD 3.60-4.00/kg)
• 60kg minimum trial; 1-10MT for ongoing supply
• Full documentation: COO, phytosanitary, phytosanitary certificate and COA

We can ship DDP to Dubai. Happy to arrange cupping session with your team.

Best regards,
Tumelo Ramaphosa
Studex Meat`,
    status: 'draft',
    channel: 'email',
    sentDate: null,
    lastFollowUp: null,
    notes: 'Food/beverage importer. Smaller operation. Good for initial trial order.',
    priority: 'low',
    ciieMeeting: false,
    responseNotes: '',
  },
  {
    id: 'ouae9',
    buyer: 'Intertrade General Trading LLC — Commodities',
    company: 'Intertrade General Trading LLC',
    country: '🇦🇪 UAE',
    contact: 'trade@intertradegeneral.ae',
    subject: 'Rwanda Green Coffee — African Origin Commodity Opportunity',
    template: `Dear Intertrade General Trading Commodities Team,

I am Tumelo Ramaphosa of Studex Meat writing regarding Rwandan specialty green coffee for your African origin commodity book.

Intertrade General Trading LLC is an active UAE commodity trader — Rwanda is a high-demand origin post the July 2026 China-Africa zero-tariff expansion. Rwanda now supplies more coffee to China than any other African country.

Offer:
• Rwanda A1 Washed — FOB $4,200-4,800/MT (USD 4.20-4.80/kg), Full documentation: phytosanitary certificates, COA, fumigation records
• Rwanda A2 Natural — FOB $3,600-4,000/MT (USD 3.60-4.00/kg)
• 1-20MT lots; container and LCL options
• Can arrange freight to Dubai or direct to China

Please find attached our phytosanitary certificates and COAs. Happy to provide sample COAs.

Best regards,
Tumelo Ramaphosa
Studex Meat`,
    status: 'draft',
    channel: 'email',
    sentDate: null,
    lastFollowUp: null,
    notes: 'Active commodity trader. Focus on price + volume. Rwanda is a volume play here.',
    priority: 'medium',
    ciieMeeting: false,
    responseNotes: '',
  },
  {
    id: 'ouae10',
    buyer: 'Emirates Flight Catering (EKFC) — Airline Catering Coffee',
    company: 'Emirates Flight Catering (EKFC)',
    country: '🇦🇪 UAE',
    contact: 'procurement@ekac.ae',
    subject: 'Rwanda Specialty Coffee — Premium Airline Catering Origin',
    template: `Dear Emirates Flight Catering Procurement Team,

I am Tumelo Ramaphosa of Studex Meat writing regarding premium origin coffee for Emirates Flight Catering.

EKFC serves premium passengers across Emirates\' global route network. Rwanda specialty coffee — Full documentation: phytosanitary certificates, COA, fumigation records — would be a compelling addition to your origin selection, differentiating the Emirates inflight coffee experience.

Our offer:
• Rwanda A1 Washed — FOB $4,200-4,800/MT (USD 4.20-4.80/kg) (floral, clean, premium)
• Rwanda A2 Natural — FOB $3,600-4,000/MT (USD 3.60-4.00/kg) (dark fruit, full-bodied)
• Full documentation: phytosanitary certificates, COA, fumigation records — meets international airline food safety standards
• Supply capacity: 5-50MT/month
• Can supply pre-roasted or green bean for your roastery partners

We are attending CIIE 2026 in Shanghai (Nov 5-10) and would welcome a meeting.

Best regards,
Tumelo Ramaphosa
Studex Meat`,
    status: 'draft',
    channel: 'email',
    sentDate: null,
    lastFollowUp: null,
    notes: 'EKFC is major buyer of premium origin coffees for airline catering. Very high volume potential. full origin documentation: phytosanitary certificates, COA, fumigation records is essential for airline food standards.',
    priority: 'high',
    ciieMeeting: false,
    responseNotes: '',
  },
  {
    id: 'o2',
    buyer: 'Tim Hortons China Procurement',
    company: 'Tim Hortons China',
    country: '🇨🇳 China',
    contact: 'procurement.cn@timhortons.com',
    subject: 'Rwanda A2 Natural Coffee — Premium Blend Opportunity — CIIE 2026',
    template: `Dear Tim Hortons China Procurement Team,

I am Tumelo Ramaphosa of Studex Meat, representing Rwandan specialty green coffee sourced through Full documentation: phytosanitary certificates, COA, fumigation records.

Tim Hortons China represents an interesting fit for Rwanda A2 Natural — blueberry and dark chocolate notes that complement a heritage Canadian brand with strong Chinese market presence.

Offer: Rwanda A2 Natural (blueberry/chocolate) — FOB $8.20/kg. 5MT minimum. Full documentation: phytosanitary certificates, COA, fumigation records — satisfies your vendor traceability requirements.

I am attending CIIE 2026 in Shanghai (Nov 5-10) and would greatly appreciate a meeting. I am pre-registered as a buyer and can schedule time that suits your team.

Would Friday Nov 7 or Saturday Nov 8 work for a 20-minute meeting?

Warm regards,
Tumelo Ramaphosa
Studex Meat`,
    status: 'draft',
    channel: 'email',
    sentDate: null,
    lastFollowUp: null,
    notes: 'Tim Hortons China is owned by RBI. Formal vendor onboarding process. Best approached through CIIE meeting.',
    priority: 'high',
    ciieMeeting: true,
    responseNotes: '',
  },
  {
    id: 'o3',
    buyer: 'Ries Trading Co.',
    company: 'Ries Trading Co.',
    country: '🇦🇪 UAE',
    contact: 'info@riestrading.ae',
    subject: 'Rwanda A1/A2 Specialty Coffee — Dubai Re-Export Partnership',
    template: `Dear Ries Trading Team,

I am reaching out from Studex Meat regarding Rwanda-origin specialty coffee, currently positioned for re-export to China through Dubai.

With China entering a zero-tariff agreement on all 53 African origin coffees (effective July 20, 2026), the Dubai-to-China corridor is now significantly more competitive for African coffee vs Latin American supply.

We offer: Rwanda A1 Washed and A2 Natural, Full documentation: phytosanitary certificates, COA, fumigation records, at FOB $4.80–3.60-4.00/kg. Competitive for both UAE domestic and re-export markets.

Would you be open to a sample shipment evaluation? We can send 60kg trial samples to Dubai.

I am also attending CIIE 2026 in Shanghai — happy to meet there or in Dubai.

Best regards,
Tumelo Ramaphosa
Studex Meat`,
    status: 'draft',
    channel: 'email',
    sentDate: null,
    lastFollowUp: null,
    notes: 'Established Dubai trader, handles African origin coffees. Smaller lots acceptable.',
    priority: 'medium',
    ciieMeeting: false,
    responseNotes: '',
  },
  {
    id: 'o4',
    buyer: 'Nordic Coffee Co. Dubai',
    company: 'Nordic Coffee Co.',
    country: '🇦🇪 UAE',
    contact: 'hello@nordiccoffeeduai.com',
    subject: 'Rwanda Single-Origin — Dubai Specialty Roaster Partnership',
    template: `Dear Nordic Coffee Dubai Team,

I am Tumelo Ramaphosa from Studex Meat, representing Rwandan specialty green coffee — Full documentation: phytosanitary certificates, COA, fumigation records.

Your specialty roaster profile aligns well with our Rwanda A1 Washed offering (jasmine, stone fruit, clean finish) — a compelling single-origin story for the UAE specialty market.

FOB pricing: Rwanda A1 Washed USD 4.20-4.80/kg (FOB USD 4,200-4,800/MT). A2 Natural USD 3.60-4.00/kg (FOB USD 3,600-4,000/MT). 60kg minimum for trials.

Would you be open to a sample roast evaluation? Happy to ship 60kg DDP to Dubai for your assessment.

Best regards,
Tumelo Ramaphosa
Studex Meat`,
    status: 'draft',
    channel: 'email',
    sentDate: null,
    lastFollowUp: null,
    notes: 'Specialty roaster in Dubai, more agile than big traders. Good for small-lot trials. SOURCES direct.',
    priority: 'medium',
    ciieMeeting: false,
    responseNotes: '',
  },
  {
    id: 'o5',
    buyer: 'Pacific Coffee Company',
    company: 'Pacific Coffee',
    country: '🇭🇰 Hong Kong',
    contact: 'procurement@pacificcoffee.com',
    subject: 'Rwanda Specialty Coffee — CIIE 2026 Meeting Request',
    template: `Dear Pacific Coffee Procurement Team,

I am reaching out from Studex Meat regarding Rwanda-origin specialty coffee for your Asian market supply chain.

With 200+ stores across Hong Kong, China, and Singapore, Pacific Coffee is well-positioned to introduce a Rwanda single-origin offering — differentiated from mainstream commodity blends.

Offer: Rwanda A1 Washed + A2 Natural, Full documentation: phytosanitary certificates, COA, fumigation records, FOB $8.50–9.20/kg. Trial shipment from 2MT.

I will be attending CIIE 2026 in Shanghai (Nov 5-10) and would welcome the opportunity to meet. Pre-registered as buyer.

Would you have availability for a meeting at the expo?

Best regards,
Tumelo Ramaphosa
Studex Meat`,
    status: 'draft',
    channel: 'email',
    sentDate: null,
    lastFollowUp: null,
    notes: 'Pacific Coffee = 200+ stores in HK, China, Singapore. Good target for Rwanda specialty line.',
    priority: 'medium',
    ciieMeeting: true,
    responseNotes: '',
  },
  {
    id: 'o6',
    buyer: 'Al Ghurair Foods',
    company: 'Al Ghurair Foods',
    country: '🇦🇪 UAE',
    contact: 'info@alghuraifoods.com',
    subject: 'Rwanda Coffee — UAE Specialty Division Partnership',
    template: `Dear Al Ghurair Foods Team,

I am Tumelo Ramaphosa of Studex Meat, writing regarding Rwandan specialty coffee for your specialty division.

With the China zero-tariff agreement (effective July 20) and Rwanda as China's top African coffee supplier, we see strong potential for UAE-based re-export to China through your established network.

Offer: Rwanda A1/A2 Washed, Full documentation: phytosanitary certificates, COA, fumigation records. FOB $4.80–3.60-4.00/kg. 10MT+ for re-export corridors.

Open to discussing a distribution partnership for GCC markets as well.

Best regards,
Tumelo Ramaphosa
Studex Meat`,
    status: 'draft',
    channel: 'email',
    sentDate: null,
    lastFollowUp: null,
    notes: 'Major UAE importer, specialty division growing. Decisions slower than smaller traders.',
    priority: 'low',
    ciieMeeting: false,
    responseNotes: '',
  },
];

const statusConfig: Record<OutreachStatus, { label: string; color: string; icon: string }> = {
  draft: { label: 'DRAFT', color: '#7a8099', icon: '📝' },
  sent: { label: 'SENT', color: '#4a9eff', icon: '📨' },
  replied: { label: 'REPLIED', color: '#22c55e', icon: '💬' },
  meeting_booked: { label: 'MEETING BOOKED', color: '#d4a017', icon: '📅' },
  no_response: { label: 'NO RESPONSE', color: '#ff6b6b', icon: '😶' },
};

const priorityColors: Record<string, string> = {
  high: '#ef4444',
  medium: '#f59e0b',
  low: '#7a8099',
};

function getSASTDate(): string {
  const now = new Date();
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  const saTime = new Date(utc + 2 * 60 * 60 * 1000);
  return saTime.toLocaleDateString('en-ZA', { day: '2-digit', month: 'short', year: 'numeric' });
}

function getCIIECountdown(): { days: number; label: string } {
  const now = new Date();
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  const saTime = new Date(utc + 2 * 60 * 60 * 1000);
  const ciie = new Date('2026-11-05T00:00:00+02:00');
  const diff = ciie.getTime() - saTime.getTime();
  const days = Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
  return { days, label: `CIIE 2026 — D-${days}` };
}

export default function CIIEOutreachPanel() {
  const [outreach, setOutreach] = useState<OutreachEntry[]>(initialOutreach);
  const [selected, setSelected] = useState<OutreachEntry | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const [search, setSearch] = useState('');
  const [editingNotes, setEditingNotes] = useState<string>('');
  const today = getSASTDate();
  const ciieCountdown = getCIIECountdown();

  const filtered = outreach.filter(o => {
    const matchesFilter = filter === 'all' || o.status === filter || (filter === 'ciie' && o.ciieMeeting) || (filter === 'high_priority' && o.priority === 'high');
    const matchesSearch = !search || o.buyer.toLowerCase().includes(search.toLowerCase()) || o.company.toLowerCase().includes(search.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const markSent = (id: string) => {
    setOutreach(prev => prev.map(o => o.id === id ? { ...o, status: 'sent' as OutreachStatus, sentDate: today } : o));
    if (selected?.id === id) setSelected(prev => prev ? { ...prev, status: 'sent' as OutreachStatus, sentDate: today } : null);
  };

  const markReplied = (id: string) => {
    setOutreach(prev => prev.map(o => o.id === id ? { ...o, status: 'replied' as OutreachStatus } : o));
  };

  const markMeetingBooked = (id: string) => {
    setOutreach(prev => prev.map(o => o.id === id ? { ...o, status: 'meeting_booked' as OutreachStatus } : o));
  };

  const markNoResponse = (id: string) => {
    setOutreach(prev => prev.map(o => o.id === id ? { ...o, status: 'no_response' as OutreachStatus } : o));
  };

  const handleSelect = (o: OutreachEntry) => {
    setSelected(o);
    setEditingNotes(o.responseNotes);
  };

  const saveResponseNotes = (id: string) => {
    setOutreach(prev => prev.map(o => o.id === id ? { ...o, responseNotes: editingNotes } : o));
    setSelected(prev => prev?.id === id ? { ...prev, responseNotes: editingNotes } : prev);
  };

  const stats = {
    total: outreach.length,
    draft: outreach.filter(o => o.status === 'draft').length,
    sent: outreach.filter(o => o.status === 'sent').length,
    replied: outreach.filter(o => o.status === 'replied' || o.status === 'meeting_booked').length,
    highPriority: outreach.filter(o => o.priority === 'high' && o.status !== 'meeting_booked').length,
    ciie: outreach.filter(o => o.ciieMeeting).length,
  };

  return (
    <div className="ciie-outreach-panel">
      {/* Header */}
      <div className="ciie-header">
        <div className="ciie-title-row">
          <div>
            <div className="ciie-title">☕ CIIE 2026 COFFEE OUTREACH CRM</div>
            <div className="ciie-subtitle">{today} · Studex Meat Coffee Pipeline</div>
          </div>
          <div className="ciie-countdown">
            <div className="ciie-days">{ciieCountdown.days}</div>
            <div className="ciie-days-label">days to CIIE</div>
          </div>
        </div>

        {/* KPI strip */}
        <div className="ciie-kpi-strip">
          <div className="ciie-kpi">
            <span className="ciie-kpi-val" style={{ color: priorityColors.high }}>{stats.highPriority}</span>
            <span className="ciie-kpi-lbl">HIGH PRIORITY</span>
          </div>
          <div className="ciie-kpi">
            <span className="ciie-kpi-val" style={{ color: '#7a8099' }}>{stats.draft}</span>
            <span className="ciie-kpi-lbl">DRAFTS</span>
          </div>
          <div className="ciie-kpi">
            <span className="ciie-kpi-val" style={{ color: '#4a9eff' }}>{stats.sent}</span>
            <span className="ciie-kpi-lbl">SENT</span>
          </div>
          <div className="ciie-kpi">
            <span className="ciie-kpi-val" style={{ color: '#22c55e' }}>{stats.replied}</span>
            <span className="ciie-kpi-lbl">REPLIED / MEETING</span>
          </div>
          <div className="ciie-kpi">
            <span className="ciie-kpi-val" style={{ color: '#d4a017' }}>{stats.ciie}</span>
            <span className="ciie-kpi-lbl">CIIE TARGETS</span>
          </div>
          <div className="ciie-kpi">
            <span className="ciie-kpi-val" style={{ color: '#4a9eff' }}>ciie.org</span>
            <span className="ciie-kpi-lbl">REGISTER AS BUYER</span>
          </div>
        </div>
      </div>

      <div className="ciie-body">
        {/* Left: Contact list */}
        <div className="ciie-contact-list">
          {/* Search + filters */}
          <div className="ciie-search-row">
            <input
              className="ciie-search"
              placeholder="Search buyers..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
          <div className="ciie-filters">
            {[
              ['all', 'All'],
              ['draft', '📝 Draft'],
              ['sent', '📨 Sent'],
              ['replied', '💬 Replied'],
              ['meeting_booked', '📅 Meeting'],
              ['no_response', '😶 No Reply'],
              ['ciie', '🇨🇳 CIIE Only'],
              ['high_priority', '🔴 High Priority'],
            ].map(([val, label]) => (
              <button
                key={val}
                className={`ciie-filter-btn ${filter === val ? 'active' : ''}`}
                onClick={() => setFilter(val)}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Contact cards */}
          <div className="ciie-contacts">
            {filtered.map(o => {
              const cfg = statusConfig[o.status];
              return (
                <div
                  key={o.id}
                  className={`ciie-contact-card ${selected?.id === o.id ? 'selected' : ''}`}
                  onClick={() => handleSelect(o)}
                >
                  <div className="ccc-top">
                    <div className="ccc-country">{o.country}</div>
                    <div className="ccc-priority" style={{ color: priorityColors[o.priority] }}>
                      {o.priority === 'high' ? '🔴' : o.priority === 'medium' ? '🟡' : '⚪'} {o.priority.toUpperCase()}
                    </div>
                  </div>
                  <div className="ccc-buyer">{o.buyer}</div>
                  <div className="ccc-company">{o.company}</div>
                  <div className="ccc-bottom">
                    <span className="ccc-status" style={{ color: cfg.color }}>
                      {cfg.icon} {cfg.label}
                    </span>
                    {o.ciieMeeting && <span className="ccc-ciie-badge">📅 CIIE</span>}
                  </div>
                </div>
              );
            })}
            {filtered.length === 0 && (
              <div className="ciie-empty">No outreach matching this filter</div>
            )}
          </div>
        </div>

        {/* Right: Email template / detail panel */}
        <div className="ciie-detail-panel">
          {!selected ? (
            <div className="ciie-no-selection">
              <div className="ciie-ns-icon">👈</div>
              <div className="ciie-ns-text">Select a contact to view the email template</div>
              <div className="ciie-ns-sub">Draft your outreach, mark as sent, and track responses</div>
              <div className="ciie-ns-action">
                <a href="https://www.ciie.org" target="_blank" rel="noopener noreferrer" className="ciie-reg-btn">
                  🌐 Register as CIIE Buyer — ciie.org
                </a>
              </div>
            </div>
          ) : (
            <>
              <div className="cdp-header">
                <div>
                  <div className="cdp-buyer">{selected.buyer}</div>
                  <div className="cdp-company">{selected.company} · {selected.country}</div>
                  <div className="cdp-contact">{selected.contact}</div>
                </div>
                <div className="cdp-status-badge" style={{ color: statusConfig[selected.status].color, borderColor: statusConfig[selected.status].color }}>
                  {statusConfig[selected.status].icon} {statusConfig[selected.status].label}
                </div>
              </div>

              <div className="cdp-notes-strip">
                <span className="cdp-notes-label">📋 NOTES</span>
                <span className="cdp-notes-text">{selected.notes}</span>
                {selected.ciieMeeting && <span className="cdp-ciie-flag">📅 CIIE MEETING TARGET</span>}
              </div>

              {/* Email template */}
              <div className="cdp-email-section">
                <div className="cdp-email-subject-label">SUBJECT</div>
                <div className="cdp-email-subject">{selected.subject}</div>
                <div className="cdp-email-body-label">EMAIL BODY</div>
                <textarea
                  className="cdp-email-body"
                  value={selected.template}
                  onChange={e => {
                    setOutreach(prev => prev.map(o => o.id === selected.id ? { ...o, template: e.target.value } : o));
                    setSelected(prev => prev?.id === selected.id ? { ...prev, template: e.target.value } : prev);
                  }}
                  rows={14}
                />
              </div>

              {/* Response tracking */}
              <div className="cdp-response-section">
                <div className="cdp-response-label">💬 RESPONSE NOTES</div>
                <textarea
                  className="cdp-response-input"
                  placeholder="Log any replies or meeting outcomes here..."
                  value={editingNotes}
                  onChange={e => setEditingNotes(e.target.value)}
                  rows={3}
                />
                <button className="cdp-save-notes-btn" onClick={() => saveResponseNotes(selected.id)}>
                  💾 Save Notes
                </button>
              </div>

              {/* Action buttons */}
              <div className="cdp-actions">
                {selected.status === 'draft' && (
                  <button className="cdp-action-btn primary" onClick={() => markSent(selected.id)}>
                    📨 Mark as Sent
                  </button>
                )}
                {selected.status === 'sent' && (
                  <>
                    <button className="cdp-action-btn success" onClick={() => markReplied(selected.id)}>
                      💬 Mark Replied
                    </button>
                    <button className="cdp-action-btn warn" onClick={() => markMeetingBooked(selected.id)}>
                      📅 Meeting Booked
                    </button>
                    <button className="cdp-action-btn danger" onClick={() => markNoResponse(selected.id)}>
                      😶 No Response
                    </button>
                  </>
                )}
                {selected.status === 'no_response' && (
                  <button className="cdp-action-btn" onClick={() => markSent(selected.id)}>
                    🔄 Resend Follow-Up
                  </button>
                )}
                {(selected.status === 'replied' || selected.status === 'meeting_booked') && (
                  <div className="cdp-success-banner">
                    ✅ {selected.status === 'meeting_booked' ? 'CIIE meeting confirmed!' : 'Buyer replied — act fast!'}
                  </div>
                )}
                <div className="cdp-copy-hint">
                  Copy the email above and send directly from your email client to <strong>{selected.contact}</strong>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
