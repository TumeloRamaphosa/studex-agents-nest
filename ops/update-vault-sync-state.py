#!/usr/bin/env python3
"""Update vault_sync block in memory/heartbeat-state.json for the 2026-10-25 EOD sync."""
import json, time, datetime, collections

P = '/workspace/memory/heartbeat-state.json'
d = json.load(open(P), object_pairs_hook=collections.OrderedDict)

vs = d.get('vault_sync')
if not isinstance(vs, dict):
    vs = collections.OrderedDict()
    d['vault_sync'] = vs

now = datetime.datetime(2026, 10, 25, 22, 0, 0)
vs['last_sync'] = '2026-10-25 22:00 UTC'
vs['last_sync_ts'] = int(now.timestamp())
vs['last_sync_date'] = '2026-10-25'
vs['last_sync_file'] = 'studex-obsidian-vault/daily/2026-10-25.md'
vs['vault_file'] = 'studex-obsidian-vault/daily/2026-10-25.md'
vs['last_file'] = 'studex-obsidian-vault/daily/2026-10-25.md'
vs['last_sync_sa_st'] = '2026-10-26 00:00 SAST'
vs['last_sync_cron_id'] = '4eba3bce-4551-4f02-8a03-fbbafa7084b0'
vs['sync_scope'] = ('2026-10-25 full Sunday EOD — research brief (China tariff lead finding + caviar permit '
                    'stack), Build Hour (tariff block v3 x3 files + applier, export checklist; UAE buyer list '
                    'NOT built), TASK-STUDEX-TRADE-001 content package (APPROVE, unpublished), '
                    'credential-surface closures x2. Orders 0/blind, revenue unfalsifiable, 0 posts published.')
vs['orders_confirmed'] = 0
vs['orders_status'] = ('UNKNOWN - Shopify Admin API 401 (studexmeat.myshopify.com); storefront 200 / 30 products; '
                       'AgentMail 4 keys live / 13 inboxes / 0 external inbound today (newest external still '
                       '2026-10-11); WhatsApp line unreadable from this host')
vs['revenue'] = 'unfalsifiable (no instrument)'
vs['content_published'] = 0
vs['content_status_today'] = ('Daily Content Agent 06:55 UTC wrote Roasted Coffee Washed (R400/kg) caption -> '
                               'posts/pending/2026-10-25.json, APPROVED_PENDING_FB_TOKEN, NOT published '
                               '(Meta 190, page token expired 27-Jun-26). TASK-STUDEX-TRADE-001 package APPROVE, '
                               'unpublished (11 files, 0 published/0 scheduled/0 queued). Blotato 401 at EOD + '
                               'FB account 38744 has subaccounts:[] -> no Page to post to. No working publish path.')
vs['research_lead_finding'] = ('2026-10-25 - our China copy was WRONG on the top commercial fact: zero tariff '
                               'effective 1 May 2026 (not 20 Jul), continental framework (not a bilateral SA-China '
                               'protocol), and Rwanda is an LDC so our duty-free position has NO expiry while SA/KE/'
                               'NG/EG expire 30 Apr 2028. Corrected in v3 tonight. Roasted-at-origin $8.50/kg vs '
                               'green $3.80 = +124% uplift, both duty-free. CO must cite the zero-tariff preference '
                               'or MFN 8-30% applies retroactively. EUDR 30 Dec 2026 and we hold no plot '
                               'geolocation. Caviar: CITES permit mandatory; no Russian provenance claims; '
                               'HS 1604.14.10 duty rate still unverified (20% modelled).')
vs['builds_2026_10_25'] = ('Build Hour ran 21:00 UTC. Delivered: CHINA TARIFF BLOCK v3 '
                            '(china-coffee-sheet-copy-paste.md TAB 3d + re-dated TAB 2 + LC + CO + CIIE escalated; '
                            'china-coffee-outreach.md v3; china-coffee-outreach-revised.md SUPERSEDED banner) and '
                            'EXPORT-DOCUMENT-CHECKLIST (export-docs/, 12.6KB, Parts A-D). NOT delivered: UAE buyer '
                            'list (Build 3). builds/2026-10-25.md was never written - artefact exists, receipt does not.')
vs['push_result'] = ('2026-10-25 22:00 UTC - commit lands locally; git push origin master fails, no GitHub '
                     'credential on this host (no GITHUB_PAT in .env, /root/.git-credentials 0 bytes, gh not '
                     'installed, no SSH key, Composio has no GitHub toolkit, Orgo 401). 852 commits unpushed '
                     '(was 782 at the 24 Oct EOD). Verified failure text: "fatal: could not read Username for https://github.com: terminal prompts disabled". Owner action: paste a classic PAT with repo scope (or '
                     'fine-grained contents:write) on TumeloRamaphosa/studex-agents-nest; I write it to '
                     '/root/.git-credentials and push the backlog in one go.')
vs['github_push'] = 'FAILED - no PAT; 852 commits unpushed (owner action: one PAT)'
vs['commits_pending'] = '853 ahead of origin/master (unpushed)'
vs['agentmail_key_status_correction'] = ('2026-10-25 - TOOLS.md is STALE on AGENTMAIL_API_KEY: it is listed as '
                                         'dead/revoked but returns HTTP 200 tonight and at 12:35 UTC. All 4 keys '
                                         'live, 13 inboxes reachable, 0 external inbound today.')
vs['credential_surface_2026_10_25'] = ('/tmp gateway log: R2_ACCESS_KEY_ID x4 masked 04:12 UTC, FEEDHIVE_API_KEY '
                                       'x5 masked 12:48 UTC; both re-verified by re-running the identical audit '
                                       '(VERDICT: CLEAN, files holding exposure: 0). ROOT CAUSE recorded in '
                                       'HEARTBEAT.md: credential probes that interpolate a key into a shell '
                                       'command line put the literal into argv and the gateway logs argv - the '
                                       'probe leaks the secret it checks. Probe from a script that reads .env '
                                       'in-process. Note: clean goes stale because the log keeps growing.')

json.dump(d, open(P, 'w'), indent=2, ensure_ascii=False)
print('heartbeat-state.json updated — vault_sync.last_sync =', vs['last_sync'])
