/**
 * ClickUp Service — StudEx War Room Integration
 * Fetches tasks from ClickUp Lists for Coffee, Caviar, and Biltong ops
 *
 * API Docs: https://developer.clickup.com/reference/gettasks
 *
 * The ClickUp API token is NEVER read in the browser. Vite inlines VITE_-prefixed
 * variables into the bundle verbatim, so a client-side token read publishes it to
 * every visitor. The browser talks to a same-origin proxy route that holds the
 * token - the same shape as VITE_LEAD_PROXY_URL and the server-side lead proxy.
 *
 * Required env vars:
 *   VITE_CLICKUP_PROXY_URL=/api/clickup   (default) — the server route holding the token
 *   VITE_CLICKUP_WORKSPACE=90152650899
 */

export interface ClickUpTask {
  id: string;
  name: string;
  status: {
    status: string;
    color: string;
  };
  priority: string | null;
  priority_color?: string;
  assignee: {
    id: number;
    username: string;
    email: string;
    color: string;
    profilePicture: string | null;
  } | null;
  due_date: string | null;
  date_created: string;
  time_estimate: number | null;
  url: string;
  list_id: string;
  project_name: string;
  tags: { name: string; color: string }[];
  custom_id: string;
}

export interface ClickUpList {
  id: string;
  name: string;
  color: string;
  space_name: string;
}

export const LISTS: Record<string, string> = {
  COFFEE:  import.meta.env.VITE_CLICKUP_LIST_COFFEE  as string || '2kyr8j4k-315',
  CAVIAR:  import.meta.env.VITE_CLICKUP_LIST_CAVIAR  as string || '',
  BILTONG: import.meta.env.VITE_CLICKUP_LIST_BILTONG as string || '',
};

const PROXY_BASE = (
  (import.meta.env.VITE_CLICKUP_PROXY_URL as string) || '/api/clickup'
).replace(/\/+$/, '');

/** Fetch all tasks from a single List */
export async function getListTasks(listId: string): Promise<ClickUpTask[]> {
  if (!listId) return [];

  const tasks: ClickUpTask[] = [];
  let page = 0;
  const limit = 100;

  while (true) {
    const url = `${PROXY_BASE}/list/${listId}/task?limit=${limit}&page=${page}`;
    const res = await fetch(url, { headers: { 'Content-Type': 'application/json' } });
    if (!res.ok) {
      console.error(`[ClickUp] Failed to fetch list ${listId}: ${res.status} ${res.statusText}`);
      break;
    }
    const data = await res.json();
    tasks.push(...(data.tasks || []));
    if (!data.has_more) break;
    page++;
  }
  return tasks;
}

/** Fetch all tasks across all three product lines */
export async function getAllTasks(): Promise<Record<string, ClickUpTask[]>> {
  const [coffee, caviar, biltong] = await Promise.all([
    getListTasks(LISTS.COFFEE),
    getListTasks(LISTS.CAVIAR),
    getListTasks(LISTS.BILTONG),
  ]);
  return { coffee, caviar, biltong };
}

/** Priority display config */
export const PRIORITY_CONFIG: Record<string, { label: string; emoji: string; color: string }> = {
  urgent: { label: 'URGENT', emoji: '🔴', color: '#ef4444' },
  high:   { label: 'HIGH',   emoji: '🟡', color: '#f59e0b' },
  medium: { label: 'MED',    emoji: '🟢', color: '#22c55e' },
  low:    { label: 'LOW',    emoji: '⚪', color: '#94a3b8' },
  null:   { label: 'NONE',   emoji: '⚪', color: '#64748b' },
};

/** Status color map */
export function getStatusColor(status: string): string {
  const s = status?.toLowerCase() || '';
  if (s.includes('done') || s.includes('complete') || s.includes('closed')) return '#22c55e';
  if (s.includes('progress') || s.includes('active') || s.includes('doing')) return '#f59e0b';
  if (s.includes('review') || s.includes('test')) return '#3b82f6';
  if (s.includes('block') || s.includes('stuck')) return '#ef4444';
  return '#64748b';
}

/** Format due date */
export function formatDueDate(dueDate: string | null): string {
  if (!dueDate) return '—';
  const d = new Date(parseInt(dueDate));
  return d.toLocaleDateString('en-ZA', { day: '2-digit', month: 'short' });
}

/** Get tasks grouped by status for a list */
export function groupByStatus(tasks: ClickUpTask[]) {
  const groups: Record<string, ClickUpTask[]> = {};
  for (const task of tasks) {
    const key = task.status?.status || 'Unknown';
    if (!groups[key]) groups[key] = [];
    groups[key].push(task);
  }
  return groups;
}
